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
"""

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

	def distinct (self, list):
		buff_list = []
		for element in list :
			if element not in buff_list :
				buff_list.append(element)
		return buff_list

	def asociar_usuario_fase(self, usuario_id, fase_id):
		"""
		Asocia los permisos de un usuario con una fase, asi los usuarios que posean
		el rol estaran asociados a la fase.

		@type  usuario_id  : String
		@param usuario_id : Codigo del rol

		@type  fase_id   : Integer
		@param fase_id   : Identificador de la fase

		@rtype  : Rol
		@return : El rol que es aplicado a la fase.
		"""

		#rol = self.get_rol_by_codigo(cod_rol)
		#usuario = DBSession.query(Usuario).get(usuario_id)
		fase = DBSession.query(Fase).get(fase_id)
		#Se obtienen los permisos del template
		permisos_rol = self.distinct(DBSession.query(Permiso).\
						filter(RolPermisoProyecto.permiso_id == Permiso.permiso_id).\
						filter(RolPermisoProyecto.proyecto_id == fase.proyecto)
						)

		#Se se asocian el rol con la fase
		for permiso in permisos_rol:

			rpu = UsuarioPermisoFase()

			rpu.fase_id = fase_id
			rpu.usuario_id = usuario_id
			rpu.permiso_id = permiso.permiso_id
			#Asocia el rol con los permisos y la fase
			DBSession.add(rpu)

	def asignar_rol_usuario(self,usuario_id , cod_rol, id_proyecto, can_commit=True):
		"""
		Asigna un rol asociado a un proyecto al usuario determinado.

		@type  usuario_id  : Integer
		@param usuario_id  : Identificador del usuario

		@type  cod_rol    : String
		@param cod_rol    : Codigo del rol

		@type  id_proyecto : Integer
		@param id_proyecto : Identificador del proyecto al cual se va aplicar el rol

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
					filter(UsuarioPermisoFase.usuario_id == Usuario.usuario_id).\
					filter(UsuarioPermisoFase.fase_id == id).\
					filter(UsuarioPermisoFase.permiso_id == Permiso.permiso_id).\
					filter(Permiso.nombre == permiso_name).all()
		#Si el usuairo es lider del proyecto se saltan los controles
		user = checker.get_current_user()
		fase = DBSession.query(Fase).get(id)
		rol = self.get_rol_by_codigo('lider_' + str(fase.proyecto))

		if self.usuario_has_rol(user.usuario_id, rol ):
			usuarios.append(user)

		return self.distinct(usuarios)

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
		historial.codigo = item.codigo
		historial.estado = item.estado
		historial.tipo_item = item.tipo_item
		historial.fase = item.fase
		historial.version = item.version
		historial.prioridad = item.prioridad
		historial.complejidad = item.complejidad
		historial.descripcion = item.descripcion
		historial.observacion = item.observacion
		historial.linea_base = item.linea_base
		#historial de detalles
		detalles = DBSession.query(DetalleItem).\
					filter(DetalleItem.id_item==historial.id_item).\
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
							filter((RelacionItem.id_item_actual or 
							RelacionItem.id_item_relacionado) == item.id_item).\
							all()
							
		for relacion in relaciones:
			historial_relacion = HistorialRelacion()
			historial_relacion.id_item_1 = relacion.id_item_actual
			historial_relacion.id_item_2 = relacion.id_item_relacionado
			historial_relacion.id_tipo_relacion = relacion.relacion_parentesco
			historial.relaciones.append(historial_relacion)

		DBSession.add(historial)

	def revertir_item (self, historial_item):
		"""
		Dada una entidad HistorialItem que representa una version
		anterior del item en si se obtiene de la tabla las entradas de
		esa version para que el item recupere los valores de esa version
		"""
		#debe ser una version posterior a la actual
		item = DBSession.query(Item).get(historial_item.id_item)
		version = int(item.version) + 1
		
		item = Item()
		item.id_item = historial_item.id_item
		item.nombre = historial_item.nombre
		item.codigo = historial_item.codigo
 		item.estado = historial_item.estado
		item.tipo_item = historial_item.tipo_item
		item.fase = historial_item.fase
		item.version = version 
		item.prioridad = historial_item.prioridad
		item.complejidad = historial_item.complejidad
		item.descripcion = historial_item.descripcion
		item.observacion = historial_item.observacion
		item.linea_base = historial_item.linea_base

		#recuperar los detalles
		historial_detalles = DBSession.query(HistorialDetalleItem).\
			filter(HistorialDetalleItem.id_item==historial_item.id_item).\
			all()

		for hist_detalle in historial_detalles:
			detalle = DetalleItem()
			detalle.id_detalle = hist_detalle.id_detalle
			detalle.id_item = hist_detalle.id_item
			detalle.recurso = hist_detalle.recurso
			detalle.valor = hist_detalle.valor
			item.detalles.append(detalle)

		#recuperar los relaciones
		historial_relaciones = DBSession.query(HistorialRelacion).\
			filter((HistorialRelacion.id_item_1 or 
			HistorialRelacion.id_item_2) == item.id_item).\
			all()

		for hist_relacion in historial_relaciones:
			relacion = RelacionItem()
			if(DBSession.query(Item).get(hist_relacion.id_item_1)!=None and
				DBSession.query(Item).get(hist_relacion.id_item_2)!=None):
				relacion.id_item_actual = hist_relacion.id_item_1
				relacion.id_item_relacionado = hist_relacion.id_item_2
				relacion.relacion_parentesco = hist_relacion.id_tipo_relacion
				DBSession.merge(relacion)

		DBSession.merge(item)

	def revivir_item (self, historial_item):
		"""
		Restaura el item a su ultima version sin sus relaciones
		"""
		item = Item()
		item.id_item = historial_item.id_item
		item.nombre = historial_item.nombre
		item.codigo = historial_item.codigo
		#el estado del item es en desarrollo al revivir
		item.estado = 2
		item.tipo_item = historial_item.tipo_item
		item.fase = historial_item.fase
		item.version = historial_item.version
		item.prioridad = historial_item.prioridad
		item.complejidad = historial_item.complejidad
		item.descripcion = historial_item.descripcion
		item.observacion = historial_item.observacion
		item.linea_base = historial_item.linea_base

		#recuperar los detalles
		historial_detalles = DBSession.query(HistorialDetalleItem).\
			filter(HistorialDetalleItem.id_item==historial_item.id_item).\
			all()

		for hist_detalle in historial_detalles:
			detalle = DetalleItem()
			detalle.id_detalle = hist_detalle.id_detalle
			detalle.id_item = hist_detalle.id_item
			detalle.recurso = hist_detalle.recurso
			detalle.valor = hist_detalle.valor
			item.detalles.append(detalle)

		DBSession.merge(item)

	def get_aprobados_sin_lineas (self, idfase):
		#lista de items aprobados de la fase. Suponiendo que el id del estado "aprobado"
		#sea 1
		itemsAprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado==1).\
												filter(Item.linea_base==None).\
												all()
		return itemsAprobados

	def get_detalles_by_item(self, iditem):
		"""
		Retorna los atributos del tipo de item al que pertenece el item
		especificado
		"""
		item = DBSession.query(Item).get(iditem)
		#tipo_item = DBSession.query(TipoItem).get(item.tipo_item)
		#atibutos = tipo_item.atributos
		detalles = item.detalles
		return detalles

util = SessionUtil()


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
			return predicates.has_permission(permiso_name+' '+str(id_proyecto))
		else:
			return None

	def check_fase_permiso(self, id_fase, permiso_name,nuleable=False):
		"""
		Controla si el usuario que actualmente se encuentra logeado posee
		el deteminado permiso sobre una fase.

		@type   id_fase : Integer
		@param  id_fase : Identificador de la fase

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
		#Se obtiene la fase actual
		fase = DBSession.query(Fase).get(id_fase)
		#se recupera el rol del lider del proyecto
		rol = util.get_rol_by_codigo('lider_' + str(fase.proyecto))
		#si el usuario es lider del proyecto se salta los controles
		if util.usuario_has_rol(current_user.usuario_id, rol) :
			return predicates.has_permission(permiso_name)

		usuario_permiso_fase = DBSession.query(UsuarioPermisoFase).\
								filter(UsuarioPermisoFase.usuario_id ==
									RolUsuario.usuario_id).\
								filter(UsuarioPermisoFase.fase_id ==
									id_fase).\
								filter(Permiso.permiso_id ==
									UsuarioPermisoFase.permiso_id).\
								filter(Permiso.nombre ==
									permiso_name).\
								filter(RolUsuario.usuario_id ==
									current_user.usuario_id).\
								all()

		if (len(usuario_permiso_fase) != 0):
			return predicates.has_permission(permiso_name)
		elif nuleable == False:
			#return predicates.has_permission(permiso_name+' '+str(id_proyecto))
			return predicates.has_permission('Sin permiso')
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
					filter(UsuarioPermisoFase.usuario_id == current_user.usuario_id).\
					filter(UsuarioPermisoFase.fase_id == Fase.id_fase).\
					filter(Permiso.permiso_id == UsuarioPermisoFase.permiso_id).\
					filter(Permiso.nombre == permiso_name).\
					filter(RolUsuario.usuario_id == current_user.usuario_id).\
					filter(Fase.proyecto == idproyecto).\
					all()
		return fases


checker =  SessionChecker()
