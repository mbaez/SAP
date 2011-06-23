# -*- coding: utf-8 -*-
from repoze.what import predicates, authorize
from tg import request
# project specific imports
from sap.model import DBSession, metadata
from tg.controllers import RestController
from sap.model import *

#import para la generacion del codigo
import time

#imports para graficar los grafos
#import de la libreria de grafo
from sap.lib.pygraph.classes.digraph import *
from sap.lib.pygraph.algorithms.cycles import *
from sap.lib.pygraph.readwrite.dot import write
# Import graphviz

import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv
import pygraphviz as pgv

"""Modulo que contiene un conjunto de metodos de uso frecuente

   :author: Maximiniliano Baez Gonzalez
   :mail: mxbg.py@gmail.com
"""

class Util ():

	def __init__(self, model=None, current=None, sec=0):
		self.__current = current
		self.__model__ = model
		self.__sec = sec

	def get_current (self, id):
		"""
		@type  id : Integer
		@param id : Identificador, clave primaria de la tabla

		@rtype  : Entity
		@return : Instancia actual
		"""
		#print "#### IN CURRENT " + str(self.__current)
		if self.__current != None :
			#print "#### IN PK" + str(self.get_primary_key(self.__current))
			pass
		if self.__current == None or self.get_primary_key(self.__current) != id and id != 0 :
			try:
				self.__current = DBSession.query(self.__model__).get(id)
			except:
				print "ID "+str(id)+" ERROR!!! "+str(__model__)

		#print "@@@@@ OUT CURRENT " + str(self.__current)
		return self.__current

	def gen_codigo(self, prefijo):
		now = time.localtime()
		time_string = str(now.tm_year)[2:] + str(now.tm_yday) +\
					  str(now.tm_min*60 + now.tm_sec) +str(self.__sec)
		self.__sec += 1
		return prefijo+time_string

	def get_by_codigo(self, codigo):

		instance = DBSession.query(self.__model__).filter(self.cmp_codigo(codigo)).first()
		print "GET "+str(instance)
		return instance

	def distinct (self, list):
		buff_list = []
		for element in list :
			if element not in buff_list :
				buff_list.append(element)
		return buff_list

	# Funciones que interactuan con el current del modelo

	def cmp_codigo(self,codigo):
		pass

class ProyectoUtil(Util):

	def __init__(self):
		Util.__init__(self,Proyecto)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	#Interactuan con el current
	def get_primary_key(self, current):
		return current.id_proyecto

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

	def __init__(self):
		Util.__init__(self,Rol)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	def get_primary_key(self, current):
		return current.rol_id

	def cmp_codigo(self, codigo):
		return Rol.codigo == codigo
	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)


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

	def __init__(self):
		Util.__init__(self,Fase)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	def get_primary_key(self, current):
		return current.id_fase

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
		if usuario_util.usuario_has_rol(current_user.usuario_id, rol) :
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

	def __init__(self):
		return Util.__init__(self,Item)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	def get_primary_key(self, current):
		return current.id_item

	def cmp_codigo(self, codigo):
		return Item.codigo == codigo

	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)

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

		#~ #historial de detalles
		#~ detalles = DBSession.query(DetalleItem).\
					#~ filter(DetalleItem.id_item==item.id_item).\
					#~ all()

		for detalle in item.detalles:
			historial_detalle = HistorialDetalleItem()
			historial_detalle.id_detalle = detalle.id_item_detalle
			historial_detalle.id_atributo_tipo_item = detalle.id_atributo_tipo_item
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
		DBSession.flush()

	def revertir_item (self, historial_item):
		"""
		Dada una entidad HistorialItem que representa una version
		anterior del item en si se obtiene de la tabla las entradas de
		esa version para que el item recupere los valores de esa version
		"""
		#debe ser una version posterior a la actual
		item = DBSession.query(Item).get(historial_item.id_item)
		detalles = item.detalles
		print "Recuperar el item "+str(item)
		item.nombre = historial_item.nombre
		item.codigo = historial_item.codigo
 		item.estado_actual = estado_item_util.get_by_codigo('Revision')
		#item.estado = item.estado_actual.id_estado_item
		item.tipo_item = historial_item.tipo_item
		item.fase = historial_item.fase
		item.version += 1
		item.prioridad = historial_item.prioridad
		item.complejidad = historial_item.complejidad
		item.descripcion = historial_item.descripcion
		item.observacion = historial_item.observacion
		item.linea_base = None
		print "Recuperar los detalles"
		#recuperar los detalles
		historial_detalles = DBSession.query(HistorialDetalleItem).\
			filter(HistorialDetalleItem.id_historial == historial_item.id_historial_item).\
			all()


		#variable para indexar las posiciones que corresponden a los valores
		#de esa version
		atributo_mapper = {}
		index = 0

		"""
		Se establecen los detalles actuales del item a None
		para que el item conserve los campos definidos por su tipo de
		item. El item recuperara los valores de la version a la cual se
		quiere revertir
		"""
		for detalle in item.detalles:
			detalle.valor = None
			detalle.adjunto = None
			detalle.observacion = None
			atributo_mapper[detalle.id_atributo_tipo_item] = index
			index += 1

		for hist_detalle in historial_detalles:

			index = atributo_mapper[hist_detalle.id_atributo_tipo_item]

			item.detalles[index].adjunto = hist_detalle.adjunto
			item.detalles[index].observacion = hist_detalle.observacion
			item.detalles[index].valor = hist_detalle.valor

		DBSession.merge(item)


		print "Recuperar las relaciones"
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
		print "Merge"
		DBSession.merge(item)
		print "Flush"
		DBSession.flush()
		return

	def revivir_item (self, historial_item):
		"""
		Restaura el item a su ultima version sin sus relaciones
		"""
		item = Item()
		item.id_item = historial_item.id_item
		item.nombre = historial_item.nombre
		item.codigo = historial_item.codigo
		#el estado del item es en desarrollo al revivir
		item.estado_actual = estado_item_util.get_by_codigo('Revision')
		item.tipo_item = historial_item.tipo_item
		item.fase = historial_item.fase
		item.version = historial_item.version
		item.prioridad = historial_item.prioridad
		item.complejidad = historial_item.complejidad
		item.descripcion = historial_item.descripcion
		item.observacion = historial_item.observacion
		item.linea_base = None

		#se vacian los detalles
		item.detalles = []
		atributo_mapper = {}
		#Se obtienen los atributos actuales del tipo de item al que pertenece
		tipo_item = DBSession.query(TipoItem).get(historial_item.tipo_item)

		for atributo in tipo_item.atributos:
			detalle = DetalleItem()
			detalle.id_item = historial_item.id_item
			detalle.id_atributo_tipo_item = atributo.id_atributo_tipo_item
			detalle.adjunto = None
			detalle.valor = None

			atributo_mapper[atributo.id_atributo_tipo_item] = len(item.detalles)

			item.detalles.append(detalle)

		#recuperar los detalles
		historial_detalles = DBSession.query(HistorialDetalleItem).\
			filter(HistorialDetalleItem.id_item==historial_item.id_item).\
			all()

		#Se setean los valores a los atributos ya existentes
		for hist_detalle in historial_detalles:
			#Se obtiene el indice correspondiente al atributo del tipo de item
			index = atributo_mapper[hist_detalle.id_atributo_tipo_item]

			item.detalles[index].adjunto = hist_detalle.adjunto
			item.detalles[index].valor = hist_detalle.valor

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

	def anadir_detalles (self, tipo_item):
		"""
		Crea los detalles que corresponden al item segun el tipo de item
		al cual corresponda
		"""
		detalles = []
		for atributo in tipo_item.atributos:
			detalle = DetalleItem()
			detalle.nombre = atributo.nombre
			detalle.id_atributo_tipo_item = atributo.id_atributo_tipo_item
			detalle.valor = None
			detalle.recurso = None
			detalles.append(detalle)

		return detalles

	def get_items_aprobados (self, idfase):
		#lista de items aprobados de la fase. Suponiendo que el id del estado "aprobado"
		#sea 1
		items_aprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado==EstadoItem.id_estado_item).\
												filter(EstadoItem.nombre == 'Aprobado').\
												all()
		items = []
		for item in items_aprobados:
			linea_base = item.linea_base

			if(linea_base == None):
				items.append(item)
			else:
				estado_linea_base = DBSession.query(EstadoLineaBase).get(linea_base.id_estado_linea_base)
				if(estado_linea_base.nombre == 'Abierta'):
					items.append(item)

		return items

	def verificar_linea_base(self, item):
		"""
		Verifica si un item no pertenece a una linea base o si no
		pertenece a una linea base Comprometida o Cerrdada
		"""
		linea_base = item.linea_base
		if(linea_base == None):
			return True

		estado_linea_base = linea_base.estado
		if(estado_linea_base.nombre == "Cerrada" or \
			estado_linea_base.nombre == "Comprometida"):
			print "ENTROOOO"
			return False
		elif(estado_linea_base.nombre == "Abierta"):
			return True


	def deja_huerfanos (self, item):
		relaciones = DBSession.query(RelacionItem).\
					filter(RelacionItem.id_item_actual==item.id_item).\
					all()
		#por cada sucesor se obtienen
		for relacion in relaciones:
			antecesores = self.get_incidentes(relacion.id_item_relacionado)
			if(len(antecesores) == 1):
				return True

		return False


	"""
	metodo que retorna los antecesores de un item.
	parametros:
	- id_item Integer
	retorna:
	- antecesores : List []
	"""
	def get_incidentes (self, id_item):
		#lista de padres
		antecesores = []
		#relaciones
		relaciones = []

		#se obtienen todas las relaciones del item. Si el id de la relacion
		#hijo-padre es 1 se obtienen todas las relaciones de este tipo que
		#tiene el item actual
		relaciones = DBSession.query(RelacionItem).\
			filter(RelacionItem.id_item_relacionado==id_item).\
			all()

		for relacion in relaciones:
			antecesores.append(relacion.id_item_actual)

		return antecesores

	"""
	metodo que retorna el padres de un item.
	parametros:
	- item Item
	retorna:
	- item Item
	"""
	def getPadre (self, item):
		#lista de padres
		padre = []
		#relaciones
		relacion = []

		#se obtienen todas las relaciones del item. Si el id de la relacion
		#hijo-padre es 1 se obtienen todas las relaciones de este tipo que
		#tiene el item actual
		relacion = DBSession.query(RelacionItem).\
			filter(RelacionItem.id_item_relacionado==item.id_item).\
			filter(RelacionItem.relacion_parentesco==1).\
			first()

		padre = DBSession.query(Item).get(relacion.id_item_actual)
		return padre

	"""
	metodo que retorna los items aprobados de una fase.
	parametros:
	- idfase Integer
	retorna:
	- List[] Item
	"""
	def getItemsAprobados (self, idfase):
		#lista de items aprobados de la fase. Suponiendo que el id del estado "aprobado"
		#sea 1
		itemsAprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado_item==1).\
												all()
		return itemsAprobados

	"""
	Construye el grafo completo del proyecto con las todas las relaciones
	parametros:
	idproyecto: Integer
	retorna:
	grafo: digraph
	"""
	def proyectGraphConstructor(self, idproyecto):
		fases = DBSession.query(Fase).filter(Fase.proyecto==idproyecto).all()
		grafo = digraph()
		items = []
		itemsId = []

		#se "obtienen los items de cada fase
		for fase in fases:
			items = items + list(DBSession.query(Item).filter(Item.fase==fase.id_fase))

		for item in items:
			grafo.add_nodes([item.id_item])

		#guardar los ids de los items
		for item in items:
			itemsId = itemsId + [item.id_item]
 		"""
		Se busca en la tabla RelacionItem todas las relaciones
		que contengan a los items del proyecto
		"""
		relaciones = DBSession.query(RelacionItem).\
						filter((RelacionItem.id_item_actual).in_(itemsId)).\
						all()

		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id_item_actual,relacion.id_item_relacionado))


		return grafo

	"""
	construye el grafo "Padre-Hijo" dentro de una fase
	parametros:
	- idfase Integer
	retorna:
	- grafo digraph (grafo dirigido)
	"""
	def faseGraphConstructor(self, idfase):
		#lista de items para el grafo
		items = DBSession.query(Item).filter(Item.fase==idfase).all()
		itemsId = []

		"""
		Todos los items de la fase forman parte del grafo (item = nodo)
		"grafo" es un grafo dirigido que representa las relaciones padre-hijo
		en una fase.
		"""
		grafo = digraph()
		for item in items:
			grafo.add_nodes([item.id_item])

		"""
		Se busca en la tabla RelacionItem todas las relaciones de padre-hijo
		que contengan a los items de la fase
		"""
		#guardar los ids de los items
		for item in items:
			itemsId = itemsId + [item.id_item]

		relaciones = DBSession.query(RelacionItem).\
						filter(RelacionItem.relacion_parentesco==1).\
						filter(RelacionItem.id_item_actual.in_(itemsId)).\
						filter(RelacionItem.id_item_relacionado.in_(itemsId)).\
						all()

		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id_item_actual,relacion.id_item_relacionado))

		return grafo

	"""
	metodo para verificar si una nueva relacion provoca un ciclo
	parametros:
	- nuevaRelacion tipo RelacionItem
	- idfase tipo Integer
	retorna
		List [] si no tiene ciclo
		List [edges] los enlaces que forman el ciclo
	"""
	def ciclo (self, id1, id2, idfase):
		grafo = self.faseGraphConstructor(idfase)
		if(grafo.has_edge((id1,id2))):
			return []
		grafo.add_edge((id1,id2))
		return cycle(grafo)

	"""
	metodo que calcula el impacto de la modificacion de un item
	parametros:
	- itemId tipo Integer
	- grafo del proyecto
	retorna:
	- valorImpacto Tipo Integer
	"""
	def calcular_impacto(self, grafo, itemId):
		"""
		obtener la lista de todos antecesores directos e indirectos
		el list(set()) es para que elimine los repetidos
		los metodos listBackwards y listForward retornan listas con elementos
		repetidos.
		"""
		antecesores = list(set(self.listBackward(grafo, grafo.incidents(itemId))))
		"""
		se añade a la lista el propio item
		"""
		item = [itemId]
		"""
		obtener la lista de todos sucesores directos e indirectos
		"""
		sucesores = list(set(self.listForward(grafo, grafo.neighbors(itemId))))

		#suma de listas
		impactoList = antecesores + item + sucesores

		valorImpacto = 0;
		for idItem in impactoList:
			itemActual = DBSession.query(Item).get(idItem)
			valorImpacto = valorImpacto + itemActual.complejidad

		return valorImpacto, impactoList

	"""
	metodo recursivo para obtener la lista de sucesores del item
	TODO que ya filtre los repetidos
	parametros:
	- grafo digraph
	- items List[Item]
	retorna
	List[Item]
	"""
	def listForward(self, grafo, items):
		if(len(items)==0):
			return []
		if(len(items)==1 and len(grafo.neighbors(items[0])) == 0):
			return [items[0]]
		lista = []
		for item in items:
			if(item in lista):
				lista = lista + self.listForward(grafo, grafo.neighbors(item))
			else:
				lista = lista + self.listForward(grafo, grafo.neighbors(item)) + [item]

		return lista

	"""
	metodo recursivo para obtener la lista de antecesores del item
	TODO que ya filtre los repetidos
	parametros:
	- grafo digraph
	- items List[Item]
	retorna
	List[Item]
	"""
	def listBackward(self, grafo, items):
		if(len(items)==0):
			return []
		if(len(items)==1 and len(grafo.incidents(items[0]))==0):
			return [items[0]]

		lista = []
		for item in items:
			if(item in lista):
				lista = lista + self.listBackward(grafo, grafo.incidents(item))
			else:
				lista = lista + self.listBackward(grafo, grafo.incidents(item)) + [item]

		return lista

	def marcar_en_revision(self, grafo, itemId):
		"""
		Se marca en revision los items relacionados hacia atras y adelante.
		Las lineas base de los items relacionados se marcan con estado
		Comprometida.
		obtener la lista de todos antecesores directos e indirectos
		el list(set()) es para que elimine los repetidos
		los metodos listBackwards y listForward retornan listas con elementos
		repetidos.
		"""
		antecesores = list(set(self.listBackward(grafo, grafo.incidents(itemId))))
		"""
		se añade a la lista el propio item
		"""
		item = [itemId]
		"""
		obtener la lista de todos sucesores directos e indirectos
		"""
		sucesores = list(set(self.listForward(grafo, grafo.neighbors(itemId))))

		#suma de listas
		items = antecesores + item + sucesores
		relacionados = antecesores + sucesores

		for id_item in items:
			item_actual = DBSession.query(Item).get(id_item)
			item_actual.estado = 3
			DBSession.merge(item_actual)

		# Se marca con estado comprometido cada linea base de los items
		# sucesores y antecesores.
		if(relacionados != None):
			for id_item in relacionados:
				item_actual = DBSession.query(Item).get(id_item)
				if item_actual.linea_base != None:
					linea_base = item_actual.linea_base #DBSession.query(LineaBase).get(item_actual.id_linea_base)
					linea_base.estado = estado_linea_base_util.get_by_codigo('Comprometida')
					DBSession.merge(linea_base)

			flash('Lineas base comprometidas')
		else:
			flash('El item no posee relaciones')

	def dibujar_grafo(self, nodos, item_impacto):
		fase = DBSession.query(Fase).get(item_impacto.fase)
		fases = DBSession.query(Fase).filter(Fase.proyecto==fase.proyecto).\
										all()
		desplazamiento_x = []
		for i in fases:
			desplazamiento_x.append(i.id_fase)

		desplazamiento_y = []
		for i in range(len(fases)):
			desplazamiento_y.append(0)

		gr = pgv.AGraph(directed=True, label="Grafico calculo de impacto")
		for nodo in nodos:
			item = DBSession.query(Item).get(nodo)
			valor = str(item.codigo)+" : "+str(item.complejidad)
			index = desplazamiento_x.index(item.fase)
			posicion =  str(index*2)+','+str(90-desplazamiento_y[index]*2)
			desplazamiento_y[index] = desplazamiento_y[index] + 1
			url= "/miproyecto/fase/item/ver/"+str(item.id_item)
			if(nodo == item_impacto.id_item):
				gr.add_node(valor, label=valor, fillcolor='#008ee8',
					style="filled", pos=posicion, href=url, pin=True)
			else:
				gr.add_node(valor, label=valor, fillcolor='white',
					style="filled", pos=posicion, href=url, pin=True)

		#relaciones son aristas
		aristas = DBSession.query(RelacionItem).\
						filter(RelacionItem.id_item_actual.in_(nodos)).\
						filter(RelacionItem.id_item_relacionado.in_(nodos)).\
						all()
		for arista in aristas:
			if(gr.has_edge((arista.id_item_actual, arista.id_item_relacionado))==False):
				item1 = item = DBSession.query(Item).get(arista.id_item_actual)
				item2 = item = DBSession.query(Item).get(arista.id_item_relacionado)
				valor1 = str(item1.codigo)+" : "+str(item1.complejidad)
				valor2 = str(item2.codigo)+" : "+str(item2.complejidad)
				gr.add_edge((valor1, valor2), color='#8dad48', href="/")

		gr.layout()
		gr.draw('sap/public/img/calculo_impacto.svg')


class TipoItemUtil(Util):

	def __init__(self):
		Util.__init__(self,TipoItem)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	def get_primary_key(self, current):
		return current.id_tipo_item

	def cmp_codigo(self, codigo):
		return TipoItem.codigo == codigo
	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)

class UsuarioUtil(Util):

	def __init__(self):
		return Util.__init__(self,Usuario)

	def get_current (self, id=0):
		return Util.get_current(self, id)

	def get_primary_key(self, current):
		return current.usuario_id

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
	def __init__(self):
		return Util.__init__(self,EstadoItem)
	def get_primary_key(self, current):
		return current.id_estado_item

	def cmp_codigo(self, codigo):
		print "CODIGO:"+codigo
		return EstadoItem.nombre == codigo

	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)

class EstadoProyectoUtil(Util):
	def __init__(self):
		return Util.__init__(self,EstadoProyecto)
	def get_primary_key(self, current):
		return current.id_estado_proyecto

	def cmp_codigo(self, codigo):
		return EstadoProyecto.nombre == codigo

	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)

class EstadoLineaBaseUtil(Util):
	def __init__(self):
		return Util.__init__(self,EstadoLineaBase)
	def get_primary_key(self, current):
		return current.id_estado_linea_base

	def cmp_codigo(self, codigo):
		return EstadoLineaBase.nombre == codigo

	def get_by_codigo(self, codigo):
		return Util.get_by_codigo(self, codigo)

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

	def authorize_fase(self, permiso, id=0, fase=None):
		try:
			if fase != None:
				id = fase.id_fase

			return fase_util.check_fase_permiso(id,permiso, True)
		except:
			return None

	def authorize_proyecto(self, permiso, id=0, proyecto=None):
		try:
			if proyecto != None:
				id = proyecto.id_proyecto
			return proyecto_util.check_proyecto_permiso(id,permiso, True)
		except:
			return None



#Se instancian las clases
proyecto_util = ProyectoUtil()
rol_util = RolUtil()
fase_util = FaseUtil()
item_util = ItemUtil()
estado_item_util = EstadoItemUtil()
estado_proyecto_util = EstadoProyectoUtil()
estado_linea_base_util = EstadoLineaBaseUtil()
tipo_item_util = TipoItemUtil()
usuario_util = UsuarioUtil()
session_util = SessionUtil()
