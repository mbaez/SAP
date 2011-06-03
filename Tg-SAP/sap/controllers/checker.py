# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context, redirect, validate

from sap.model import *

import transaction

"""Modulo que contiene un conjunto de metodos de uso frecuente

   :author: Maximiniliano Baez Gonzalez
   :mail: mxbg.py@gmail.com
   :version: 0.1
"""

class SessionChecker():

	def check_proyecto_permiso(self, id_proyecto, permiso_name,nuleable=False):
		"""
		Controla si el usuario que actualmente se encuentra logeado posee
		el deteminado permiso sobre un proyecto.

		@type   id_proyecto : Integer
		@param  id_proyecto : Identificador del proyecto

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@type      nuleable : Boolean
		@param     nuleable : Variable de control del valor de retorno.
							  Si es True y el usuario no posee permisos
							  retorna None

		@rtype  : Predicates
		@return : retorna las credenciales del usuario
		"""
		current_user = self.get_current_user()
		rol_permiso_proyecto = DBSession.query(RolPermisoProyecto).\
								filter(RolPermisoProyecto.rol_id ==
									RolUsuario.rol_id).\
								filter(RolPermisoProyecto.proyecto_id ==
									id_proyecto).\
								filter(Permiso.permiso_id ==
									RolPermisoProyecto.permiso_id).\
								filter(Permiso.nombre ==
									permiso_name).\
								filter(RolUsuario.usuario_id ==
									current_user.usuario_id).\
								all()

		if (len(rol_permiso_proyecto) != 0):
			return predicates.has_permission(permiso_name)
		elif nuleable == False:
			#return predicates.has_permission(permiso_name+' '+str(id_proyecto))
			return predicates.unmet()
		else:
			return None

	def get_current_user(self):
		"""
		Obtiene el username del usuario que se encuentra actualmente
		logeado en el sistema de la cabecera http y recupera
		de la base de datos el usuario.

		@rtype  : Usuario
		@return : retorna una instancia de la clase usuario
		"""
		identity = request.environ.get('repoze.who.identity')
		username = identity['repoze.who.userid']

		current_user = DBSession.query(Usuario).\
				filter(Usuario.user_name == username ).\
				first()

		return current_user


	def get_poyect_list(self, permiso_name):
		"""
		Obtiene un lista de los proyectos para los cuales el usuario
		que se encuentra logeado posee el correspondiente permiso.

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Proyecto [ ]
		@return : retorna una lista de los poryectos
		"""
		current_user = self.get_current_user()

		proyectos = DBSession.query(Proyecto).\
					filter(	RolPermisoProyecto.rol_id ==
							RolUsuario.rol_id).\
					filter(	RolPermisoProyecto.proyecto_id ==
							Proyecto.id_proyecto).\
					filter(	Permiso.permiso_id ==
							RolPermisoProyecto.permiso_id).\
					filter(	Permiso.nombre ==
							permiso_name).\
					filter(	RolUsuario.usuario_id ==
							current_user.usuario_id).\
					all()
		return proyectos


	def get_fases_by_proyecto_list(self, idproyecto, permiso_name):
		"""
		Obtiene un lista de las fases que pertenecen a un proyecto, para
		los cuales el usuario que se encuentra logeado posee el
		correspondiente permiso.

		@type   idproyecto : Integer
		@param  idproyecto : Identificador del proyecto

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Fase []
		@return : retorna una lista de fases
		"""
		current_user = self.get_current_user()

		fases = DBSession.query(Fase).\
					filter(RolPermisoFase.rol_id == RolUsuario.rol_id).\
					filter(RolPermisoFase.fase_id == Fase.id_fase).\
					filter(Permiso.permiso_id == RolPermisoFase.permiso_id).\
					filter(Permiso.nombre == permiso_name).\
					filter(RolUsuario.usuario_id == current_user.usuario_id).\
					filter(Fase.proyecto == idproyecto).\
					all()
		return fases


checker =  SessionChecker()

class SessionUtil() :

	def asignar_lider(self, proyecto):
		"""
		Al usuario que fue seleccionado como lider en el proyecto es registrado
		como un participante en el proyecto, con el rol de lider.

		@type  proyecto : Proyecto
		@param proyecto : Proyecto al cual estara asociado el lider.

		"""
		self.asignar_participante (proyecto.lider.usuario_id,
									'lider',#codigo del rol
									proyecto.id_proyecto)

	def get_rol_by_codigo(self, cod_rol):
		"""
		Obtiene el rol que posee el nombre especificado

		@type  cod_rol   : String
		@param cod_rol   : Codigo unico del rol

		@rtype  : Rol
		@return : El rol que posee dicho codigo, en el caso de que no exista
				  ningun rol con dicho nombre retorna None
		"""
		rol = DBSession.query(Rol).filter(Rol.codigo == cod_rol).first()
		#if rol == None :
		#	return None
		return rol

	def asociar_rol_proyecto(self, cod_rol, proyecto, can_commit=True):
		"""
		Crea una copia del template de un rol, anhadiendo al nombre del este
		rol el id de un proyecto.

		@type  cod_rol   : String
		@param cod_rol   : Codigo del rol

		@type  proyecto   : Proyecto
		@param proyecto   : Proyecto al cual se va aplicar el rol

		@type  can_commit : Boolean
		@param can_commit : Variable de control de la transaccion

		@rtype  : Rol
		@return : El rol que es aplicado al proyecto.
		"""
		#Se obtine el rol template
		rol_template = self.get_rol_by_codigo(cod_rol)

		if rol_template.is_template ==  True :
			rol = self.get_rol_by_codigo(cod_rol+'_'+str(proyecto.id_proyecto))
		else:
			rol= rol_template
		#Si ya existe el rol para el proyecto
		if rol != None:
			print "ES NONE!!"
			return rol
		
		#Si no existe el rol para el proyecto lo crea
		rol = Rol()
		#cambia el nombre del rol
		rol.codigo = cod_rol+'_'+str(proyecto.id_proyecto)
		rol.nombre = rol_template.nombre
		rol.descripcion = rol_template.descripcion
		#se periste el rol
		DBSession.add(rol)

		#rol = self.get_rol_by_codigo(rol.nombre)
		#Se obtienen los permisos del template
		permisos_rol = DBSession.query(Permiso).\
						filter(RolPermiso.permiso_id == Permiso.permiso_id).\
						filter(RolPermiso.rol_id == rol_template.rol_id)
		#Anhade a la session el rol para ser persistido
		rol = self.get_rol_by_codigo(rol.codigo)
		#Se copian los permisos del template a rol nuevo
		for permiso in permisos_rol:
			rol.permisos.append(permiso)

			rpp = RolPermisoProyecto()
			rpp.proyecto_id = proyecto.id_proyecto
			rpp.rol_id = rol.rol_id
			rpp.permiso_id = permiso.permiso_id
			#Asocia el rol con los permisos y el proyecto
			#rol._permisos.append(permiso)
			DBSession.add(rpp)

		DBSession.add(rol)
		#En el caso de que
		#self.commit_transaction(can_commit)

		return rol

	def asociar_rol_fase(self, cod_rol, fase_id):
		"""
		Asocia los permisos rol con una fase, asi los usuarios que posean
		el rol estaran asociados a la fase.

		@type  cod_rol   : String
		@param cod_rol   : Codigo del rol

		@type  fase_id   : Integer
		@param fase_id   : Identificador de la fase

		@rtype  : Rol
		@return : El rol que es aplicado a la fase.
		"""

		rol = self.get_rol_by_codigo(cod_rol)

		#Se obtienen los permisos del template
		permisos_rol = DBSession.query(Permiso).\
						filter(RolPermiso.permiso_id == Permiso.permiso_id).\
						filter(RolPermiso.rol_id == rol.rol_id)

		#Se se asocian el rol con la fase
		for permiso in permisos_rol:

			rpf = RolPermisoFase()
			rpf.fase_id = fase_id
			rpf.rol_id = rol.rol_id
			rpf.permiso_id = permiso.permiso_id
			#Asocia el rol con los permisos y la fase
			DBSession.add(rpf)

		return rol

	def asignar_rol_usuario(self,usuario_id , cod_rol, id_proyecto, can_commit=True):
		"""
		Asigna un rol asociado a un proyecto al usuario determinado.

		@type  usuario_id  : Integer
		@param usuario_id  : Identificador del usuario

		@type  cod_rol    : String
		@param cod_rol    : Codigo del rol

		@type  id_proyecto : Integer
		@param id_proyecto : Identificador del proyecto al cual se va aplicar el rol

		@type  can_commit  : Boolean
		@param can_commit  : Variable de control de la transaccion

		@rtype  : Rol
		@return : El rol que es asignado al usuario.
		"""
		#Se obtiene el rol con el nombre correspondiente
		rol = self.get_rol_by_codigo(cod_rol)
		#Se verifica si el usuario posee el rol
		rol_usuario = self.usuario_has_rol(usuario_id, rol)
		#si no posee el rol, se le asigna
		if rol_usuario == None:
			rol_usuario = RolUsuario()
			rol_usuario.usuario_id = usuario_id
			rol_usuario.rol_id = rol.rol_id

			DBSession.add(rol_usuario)

			#self.commit_transaction(can_commit)

		return rol

	def usuario_has_rol(self,usuario_id, rol):
		"""
		Verifica si el usuario posee el rol especificado

		@type  usuario_id    : Integer
		@param usuario_id    : Identificador del usuario

		@type  rol_name      : String
		@param rol_name      : Nombre del rol

		@rtype  : RolUsuario
		@return : la relacion entre el usuario y el rol.
		"""
		rol_usuario = DBSession.query(RolUsuario).\
					filter(RolUsuario.usuario_id == usuario_id).\
					filter(RolUsuario.rol_id == rol.rol_id).first()

		#if len(rol_usurio)==0 :
		#	return None
		return rol_usuario

	def commit_transaction(self, can_commit):
		"""
		Realiza commit de la transaccion

		@type  can_commit  : Boolean
		@param can_commit  : Variable de control de la transaccion
		"""
		if can_commit == True :
			DBSession.flush()
			transaction.commit()


	def asignar_participante(self, usuario_id, cod_rol, proyecto_id ):
		"""
		Asigna un el rol al participante y de asociar los permisos del rol
		al proyecto especificado

		@type  usuario_id  : Integer
		@param usuario_id  : Identificador del usuario

		@type  cod_rol    : String
		@param cod_rol    : Codigo del rol

		@type  id_proyecto : Integer
		@param id_proyecto : Identificador del proyecto al cual se va aplicar el rol
		"""
		#Se obtienel proyecto al cual se asociara al usuario
		proyecto = DBSession.query(Proyecto).get(proyecto_id)
		#se asocia el rol al proyecto
		rol = self.asociar_rol_proyecto(cod_rol, proyecto)
		#se asigna el rol al usuario
		rol = self.asignar_rol_usuario(usuario_id, rol.codigo, proyecto_id)
		#se hace commit de toda la transaccion
		#self.commit_transaction(True)

	def get_usuarios_by_fase(self, id, permiso_name='ver_fase'):
		"""
		Obtiene una lista de los usuarios que poseen el permiso especificado sobre
		un proyecto.

		@type  proyecto_id  : Integer
		@param proyecto_id  : Identificador del proyecto al cual se va aplicar el rol

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Usuario []
		@return : Lista de usuarios que poseen el permiso sobre el proyecto
		"""
		usuarios = DBSession.query(Usuario).\
					filter(RolUsuario.usuario_id == Usuario.usuario_id).\
					filter(RolPermisoFase.rol_id == RolUsuario.rol_id).\
					filter(RolPermisoFase.fase_id == id).\
					filter(RolPermisoFase.permiso_id == Permiso.permiso_id).\
					filter(Permiso.nombre == permiso_name).all()

		return usuarios

	def get_usuarios_by_permiso(self, proyecto_id, permiso_name='ver_proyecto'):
		"""
		Obtiene una lista de los usuarios que poseen el permiso especificado sobre
		un proyecto.

		@type  proyecto_id  : Integer
		@param proyecto_id  : Identificador del proyecto al cual se va aplicar el rol

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Usuario []
		@return : Lista de usuarios que poseen el permiso sobre el proyecto
		"""
		usuarios = DBSession.query(Usuario).\
					filter(RolUsuario.usuario_id == Usuario.usuario_id).\
					filter(RolPermisoProyecto.rol_id == RolUsuario.rol_id).\
					filter(RolPermisoProyecto.proyecto_id == proyecto_id).\
					filter(RolPermisoProyecto.permiso_id == Permiso.permiso_id).\
					filter(Permiso.nombre == permiso_name).all()

		return usuarios

	__get_usuario_proyectos__ = get_usuarios_by_permiso

	def get_roles_by_proyectos(self,proyecto_id):
		"""
		Obtiene una lista de los roles que de un proyecto. Esta lista en el
		caso de que el rol ya este asociado a un poryecto se anhade a la lista,
		en el caso de que este no este asiciado se anhade el template.
		De esta forma se obtinte una lista de roles cuyos nombres son distintos.

		@type  proyecto_id  : Integer
		@param proyecto_id  : Identificador del proyecto al cual se va aplicar el rol

		@rtype  : Rol []
		@return : Lista de roles de nombres distintos.
		"""
		#obtiene todos los templates
		roles = DBSession.query(Rol).filter(Rol.is_template == True).all()
		#en el casos de que un rol ya este asiciado a un poryecto no se
		#muestra el template
		for i in range(len(roles)) :
			__rol = self.get_rol_by_codigo(roles[i].codigo+"_"+str(proyecto_id))
			if __rol != None :
				roles[i] = __rol
		return roles

	def audit_item(self, item):
		"""
		Registra los cambios realizados al item determinado en el historial
		se persiste los valore del item y su atributos en el historial.

		@type  item  : Integer
		@param item  : Identificador del proyecto al cual se va aplicar el rol
		"""
		historial = HistorialItem()

		historial.id_item = item.id_item
		historial.nombre = item.nombre
		historial.estado = item.estado
		historial.tipo_item = item.tipo_item
		historial.fase = item.fase
		historial.version = item.version
		historial.prioridad = item.prioridad
		historial.complejidad = item.complejidad
		historial.descripcion = item.descripcion
		historial.observacion = item.observacion
		#historial de detalles
		detalles = DBSession.query(DetalleItem).\
					filter(DetalleItem.id_item==item.id_item).\
					all()
		for detalle in detalles:
			historial_detalle = HistorialDetalleItem()
			historial_detalle.id_detalle = detalle.id_detalle
			historial_detalle.id_item = detalle.id_item
			historial_detalle.recurso = detalle.recurso
			historial_detalle.valor = detalle.valor
			historial.detalles.append(historial_detalle)
		
		#Obtener las relaciones
		relaciones = DBSession.query(RelacionItem).\
					filter(RelacionItem.id_item_actual==item.id_item or
						RelacionItem.id_item_relacionado==item.id_item).\
						all()
		
		for relacion in relaciones: 
			historial_relacion = HistorialRelacion()
			historial_relacion.id_item_1 = relacion.id_item_actual
			historial_relacion.id_item_2 = relacion.id_item_relacionado
			historial_relacion.id_tipo_relacion = relacion.relacion_parentesco
			historial.relaciones.append(historial_relacion)
			
		DBSession.add(historial)

	def get_aprobados_sin_lineas (self, idfase):
		#lista de items aprobados de la fase. Suponiendo que el id del estado "aprobado"
		#sea 1
		itemsAprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado==1).\
												filter(Item.linea_base==None).\
												all()
		return itemsAprobados



util = SessionUtil()
