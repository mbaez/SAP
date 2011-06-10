# -*- coding: utf-8 -*-
from repoze.what import predicates
from tg import request
# project specific imports
from sap.model import DBSession, metadata

from sap.model import *

#import para la generacion del codigo
import time

"""Modulo que contiene un conjunto de metodos de uso frecuente

   :author: Maximiniliano Baez Gonzalez
   :mail: mxbg.py@gmail.com
"""

class Util ():

	__current = None
	__model__ = None
	__sec = 0

	def get_current (self, id):
		"""
		@type  id : Integer
		@param id : Identificador, clave primaria de la tabla

		@rtype  : Entity
		@return : Instancia actual
		"""
		if self.__current == None or self.get_primary_key() != id and id != 0 :

				self.__current = DBSession.query(self.__model__).get(id)

		return self.__current

	def gen_codigo(self, prefijo):
		now = time.localtime()
		time_string = str(now.tm_year)[2:] + str(now.tm_yday) +\
					  str(now.tm_min*60 + now.tm_sec) +str(self.__sec)
		self.__sec += 1
		return prefijo+time_string

	def get_by_codigo(self, codigo):

		return DBSession.query(__model__).filter(self.cmp_codigo(codigo)).first()

	def distinct (self, list):
		buff_list = []
		for element in list :
			if element not in buff_list :
				buff_list.append(element)
		return buff_list

	# Funciones que interactuan con el current del modelo
	def get_primary_key(self):
		pass

	def cmp_codigo(self,codigo):
		pass


class ProyectoUtil(Util):

	__model__ = Proyecto

	#Interactuan con el current
	def get_primary_key(self):
		return self.__current.id_proyecto

	def cmp_codigo(self, codigo):
		return Proyecto.codigo == codigo
	#
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
		current_user = session_util.get_current_user()

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
		proyecto =  proyecto_util.get_current(proyecto_id)
		#se asocia el rol al proyecto
		rol = rol_util.asociar_rol_proyecto(cod_rol, proyecto)
		#se asigna el rol al usuario
		rol = rol_util.asignar_rol_usuario(usuario_id, rol.codigo, proyecto_id)

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

	def get_poyect_list(self, permiso_name):
		"""
		Obtiene un lista de los proyectos para los cuales el usuario
		que se encuentra logeado posee el correspondiente permiso.

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Proyecto [ ]
		@return : retorna una lista de los poryectos
		"""
		current_user = session_util.get_current_user()

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


class RolUtil(Util):

	__model__ = Rol

	def get_primary_key(self):
		return self.__current.rol_id

	def cmp_codigo(self, codigo):
		return Rol.codigo == codigo

	def asignar_rol_usuario(self,usuario_id , cod_rol, id_proyecto):
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
		rol = rol_util.get_by_codigo(cod_rol)
		#Se verifica si el usuario posee el rol
		rol_usuario = usuario_util.usuario_has_rol(usuario_id, rol)
		#si no posee el rol, se le asigna
		if rol_usuario == None:
			rol_usuario = RolUsuario()
			rol_usuario.usuario_id = usuario_id
			rol_usuario.rol_id = rol.rol_id

			DBSession.add(rol_usuario)

		return rol

	def asociar_rol_proyecto(self, cod_rol, proyecto):
		"""
		Crea una copia del template de un rol, anhadiendo al nombre del este
		rol el id de un proyecto.

		@type  cod_rol   : String
		@param cod_rol   : Codigo del rol

		@type  proyecto   : Proyecto
		@param proyecto   : Proyecto al cual se va aplicar el rol

		@rtype  : Rol
		@return : El rol que es aplicado al proyecto.
		"""
		#Se obtine el rol template
		rol_template = rol_util.get_by_codigo(cod_rol)

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
		rol = rol_util.get_by_codigo(rol.codigo)
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
			__rol = rol_util.get_by_codigo(roles[i].codigo+"_"+str(proyecto_id))
			if __rol != None :
				roles[i] = __rol
		return roles


class FaseUtil(Util):

	__model__ = Fase

	def get_primary_key(self):
		return self.__current.id_fase

	def cmp_codigo(self, codigo):
		return Fase.codigo == codigo

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

		current_user = session_util.get_current_user()
		#Se obtiene la fase actual
		fase = fase_util.get_current (id_fase)
		#se recupera el rol del lider del proyecto
		rol = rol_util.get_by_codigo('lider_' + str(fase.proyecto))
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
		current_user = session_util.get_current_user()

		fases = DBSession.query(Fase).\
					filter(UsuarioPermisoFase.usuario_id == current_user.usuario_id).\
					filter(UsuarioPermisoFase.fase_id == Fase.id_fase).\
					filter(Permiso.permiso_id == UsuarioPermisoFase.permiso_id).\
					filter(Permiso.nombre == permiso_name).\
					filter(RolUsuario.usuario_id == current_user.usuario_id).\
					filter(Fase.proyecto == idproyecto).\
					all()
		return fases


class ItemUtil(Util):

	__model__ = Item

	def get_primary_key(self):
		return self.__current.id_item

	def cmp_codigo(self, codigo):
		return Item.codigo == codigo

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
			historial_detalle.id_detalle = detalle.id_item_detalle
			historial_detalle.id_item = detalle.id_item
			historial_detalle.adjunto = detalle.adjunto
			historial_detalle.observacion = detalle.observacion
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
		item = self.get_current(historial_item.id_item)
		version = int(item.version) + 1

		item = Item()
		item.id_item = historial_item.id_item
		item.nombre = historial_item.nombre
		item.codigo = historial_item.codigo
 		item.estado = estado_item_util.get_by_codigo('Revsion')
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
			detalle.id_item_detalle = hist_detalle.id_detalle
			detalle.id_item = hist_detalle.id_item
			detalle.adjunto = hist_detalle.adjunto
			detalle.observacion = hist_detalle.observacion
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
		item.estado = estado_item_util.get_by_codigo('Revsion')
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
		items_aprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado==EstadoItem.id_estado_item).\
												filter(EstadoItem.nombre == 'Aprobado').\
												filter(Item.linea_base==None).\
												all()
		return items_aprobados

	def get_detalles_by_item(self, iditem):
		"""
		Retorna los atributos del tipo de item al que pertenece el item
		especificado
		"""
		item = self.get_current(iditem)
		detalles = item.detalles
		return detalles


class TipoItemUtil(Util):

	__model__ = TipoItem

	def get_primary_key(self):
		return self.__current.id_tipo_item

	def cmp_codigo(self, codigo):
		return TipoItem.codigo == codigo

class UsuarioUtil(Util):

	__model__ = Usuario

	def get_primary_key(self):
		return self.__current.usuario_id

	def cmp_codigo(self, codigo):
		return Usuario.codigo == codigo

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


		return rol_usuario

	def get_usuarios_by_permiso(self, proyecto_id, permiso_name='ver_proyecto'):
		"""
		Obtiene una lista de los usuarios que poseen el permiso especificado sobre
		un proyecto.

		@type  proyecto_id  : Integer
		@param proyecto_id  : Identificador del proyecto al cual se va aplicar
							  el rol

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

		return self.distinct(usuarios)

	def get_usuarios_by_fase(self, id, permiso_name='ver_fase'):
		"""
		Obtiene una lista de los usuarios que poseen el permiso especificado sobre
		un proyecto.

		@type  id  : Integer
		@param id  : Identificador de la fase

		@type  permiso_name : String
		@param permiso_name : Nombre del permiso

		@rtype  : Usuario []
		@return : Lista de usuarios que poseen el permiso sobre la fase
		"""
		usuarios = DBSession.query(Usuario).\
					filter(UsuarioPermisoFase.usuario_id == Usuario.usuario_id).\
					filter(UsuarioPermisoFase.fase_id == id).\
					filter(UsuarioPermisoFase.permiso_id == Permiso.permiso_id).\
					filter(Permiso.nombre == permiso_name).all()
		#Si el usuairo es lider del proyecto se saltan los controles
		user = self.get_current()
		fase = fase_utl.get_current(id)
		rol = rol_util.get_by_codigo('lider_' + str(fase.proyecto))

		if self.usuario_has_rol(user.usuario_id, rol ):
			usuarios.append(user)

		return self.distinct(usuarios)

class EstadoItemUtil(Util):
	__model__ = EstadoItem

	def get_primary_key(self):
		return self.__current.id_estado_item

	def cmp_codigo(self, codigo):
		return Usuario.nombre == nombre

class SessionUtil():

	__current = None

	__username = ''

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
		if self.__current == None or self.__username != username :

			self.__current_user = DBSession.query(Usuario).\
					filter(Usuario.user_name == username ).first()

			self.__username = username

		return self.__current_user


#Se instancian las clases
proyecto_util = ProyectoUtil()
rol_util = RolUtil()
fase_util = FaseUtil()
item_util = ItemUtil()
estado_item_util = EstadoItemUtil()
tipo_item_util = TipoItemUtil()
usuario_util = UsuarioUtil()
session_util = SessionUtil()
