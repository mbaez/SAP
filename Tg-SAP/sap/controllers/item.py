# -*- coding: utf-8 -*-
"""Main Controller"""


from tg import expose, flash, require, url, request, redirect, response
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates, authorize

#import de la libreria de grafo
from sap.lib.pygraph.classes.digraph import *
from sap.lib.pygraph.algorithms.cycles import *
from sap.lib.pygraph.readwrite.dot import write

#pagination
from webhelpers import paginate
from tg.decorators import paginate as paginatedeco

# Import graphviz
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv
import pygraphviz as pgv

#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata

from sap.controllers.item_detalle import *
from tg.controllers import RestController

from sap.controllers.util import *

class ItemController(RestController):
	"""Controlador del item"""

	item_detalle = ItemDetalleController()

	"""Instancia del controlador del Detalle del item"""

	params = {'title':'', 'header_file':'', 'modelname':'', 'new_url':'',
			  'idfase':'', 'permiso':'', 'progreso':0, 'cantidad':'',
			  'item':'', 'impacto':'', 'atributos':'', 'permiso_editar':'',
			  'permiso_eliminar':'', 'linea_base':''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.item')
	@require(predicates.has_permission('ver_item'))
	def ver(self, id_item, **kw):

		tmpl_context.widget = detalle_item_table
		self.params['item'] = DBSession.query(Item).get(id_item)

		has_permiso = fase_util.check_fase_permiso(self.params['item'].fase,'ver_item',True)

		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+ \
				str(self.params['item'].fase),'error')

			redirect('/miproyecto/fase/item/error')

		progreso = self.params['item'].complejidad*10
		self.params['progreso'] = progreso

		if (self.params['item'].linea_base == None):
			self.params['permiso_editar'] = 'editar_item'
			self.params['permiso_eliminar'] = 'eliminar_item'
			self.params['linea_base'] = 'No posee linea base'

		elif(self.params['item'].linea_base != None):
			linea_base = DBSession.query(LineaBase).get(self.params['item'].id_linea_base)
			estado_linea_base = DBSession.query(EstadoLineaBase).get(linea_base.id_estado_linea_base)

			if(estado_linea_base.nombre == 'Abierta'):
				self.params['permiso_editar'] = 'editar_item'
				self.params['permiso_eliminar'] = 'eliminar_item'
				self.params['linea_base'] = 'Abierta'

			elif(estado_linea_base.nombre == 'Cerrada' or estado_linea_base.nombre == 'Comprometida'):
				self.params['permiso_editar'] = 'NO EDITAR'
				self.params['permiso_eliminar'] = 'NO ELIMINAR'

				if(estado_linea_base.nombre == 'Cerrada'):
					self.params['linea_base'] = 'Cerrada'

				elif(estado_linea_base.nombre == 'Comprometida'):
					self.params['linea_base'] = 'Comprometida'

		value = detalle_item_filler.get_value(self.params['item'].detalles)
		self.params['idfase'] = self.params['item'].fase
		return dict(value=value , params=self.params)

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_item'))
	def new(self, idfase, args={}, **kw):
		"""
		Encargado de cargar el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear

		@type  idtipo : Integer
		@param idtipo : Identificador del Atributo del item.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""
		new_item_form.tipo_item_relacion.idfase = idfase
		new_item_form.relaciones.idfase = idfase
		tmpl_context.widget = new_item_form

		self.params['title'] = 'Nuevo Item'
		self.params['modelname'] = 'Item'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/administracion/miproyecto/fase/item/'+idfase+'/new'
		self.params['permiso'] = 'crear_item'
		self.params['idfase'] = idfase
		self.params['cancelar_url'] = '/miproyecto/fase/get_all/'+str(idfase)
		return dict(value=kw, params=self.params)


	@validate(new_item_form, error_handler=new)
	@require(predicates.has_permission('crear_item'))
	@expose()
	def post(self, idfase, args={},**kw):
		"""
		Evento invocado luego de un evento post en el form de crear
		ecargado de persistir las nuevas instancias.

		@type  idfase : Integer
		@param idfase : Identificador de la fase.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""

		del kw['sprox_id']
		item = Item()
		item.nombre = kw['nombre']
		item.descripcion = kw['descripcion']
		item.complejidad = kw['complejidad']
		item.prioridad = kw['prioridad']
		item.observacion = kw['observacion']
		item.fase = idfase
		# Se crea con estado En Desarrollo por defecto
		item.estado = 2
		item.tipo_item = kw['tipo_item_relacion']
		item.version = 1

		tipo_item = DBSession.query(TipoItem).get(item.tipo_item)

		#anhadir detalles al item segun el tipo de item al cual corresponda
		item.detalles = item_util.anadir_detalles(tipo_item)

		item.codigo = util.gen_codigo(tipo_item.codigo + "-")
		DBSession.add(item)
		DBSession.flush()

		# Se guarda la relacion elegida en el formulario
		if(kw['relaciones'] != None):
			relacion = RelacionItem()
			#el padre es el item que se selecciono en el combo
			relacion.id_item_actual = kw['relaciones']
			#el item nuevo es el hijo
			relacion.id_item_relacionado = item.id_item
			item_relacionado = DBSession.query(Item).get(kw['relaciones'])

			if(item_relacionado.fase == int(idfase)):
				#relacion padre-hijo
				relacion.relacion_parentesco = 1
			else:
				relacion.relacion_parentesco = 2

 			DBSession.add(relacion)
			DBSession.flush()

		#flash("El item se ha creado correctamente")
		redirect('/miproyecto/fase/item/ver/'+str(item.id_item))


	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_item'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del Item.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		item =  DBSession.query(Item).get(id)
		#se verifica si el usuario posee el permiso de ver para la fase actual
		has_permiso = fase_util.check_fase_permiso(item.fase,'ver_item',True)
		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+ \
				str(self.params['item'].fase),'error')

			redirect('/miproyecto/fase/item/error')

		item_edit_form.relaciones.idfase = item.fase

		tmpl_context.widget = item_edit_form
		kw['id_item'] = item.id_item
		kw['descripcion'] = item.descripcion
		kw['nombre'] = item.nombre
		kw['codigo'] = item.codigo
		kw['complejidad'] = item.complejidad
		kw['prioridad'] = item.prioridad
		kw['observacion'] = item.observacion
		self.params['modelname'] = 'Item'
		self.params['header_file'] = 'abstract'

		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(item_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_item'))
	@expose()
	def put(self, id_item, **kw):
		item =  DBSession.query(Item).get(id_item)
		# Se registra en el historial el item antes de ser modificado
		item_util.audit_item(item)
		# Se modifica el item
		item.descripcion = kw['descripcion']
		item.codigo = kw['codigo']
		item.nombre = kw['nombre']
		item.complejidad = kw['complejidad']
		item.prioridad = kw['prioridad']
		item.observacion = kw['observacion']
		item.version = int(item.version) + 1
		item.estado = 2 # En Desarrollo
		#Se persiste el item
		DBSession.merge(item)
		DBSession.flush()

		#se verifica si ya tenia un padre
		relacion = DBSession.query(RelacionItem).\
					filter(RelacionItem.id_item_relacionado==item.id_item).\
					filter(RelacionItem.relacion_parentesco==1).\
					all()


		# Se guarda la relacion elegida en el formulario
		if(kw['relaciones'] != None):
			#no se puede relacionar consigo mismo
			if int(kw['relaciones']) == int(item.id_item):
				flash('El item no puede relacionarse consigo mismo')
				redirect('/miproyecto/fase/item/'+str(item.id_item)+'/edit')

			item_padre_antecesor = DBSession.query(Item).get(kw['relaciones'])

			if relacion != []:
				if item_padre_antecesor.fase == int(item.fase):
					#relacion padre-hijo
					relacion[0].id_item_actual = kw['relaciones']
					DBSession.merge(relacion)
				else:
					relacion = RelacionItem()
					relacion.relacion_parentesco = 2
					relacion.id_item_actual = kw['relaciones']
					relacion.id_item_relacionado = item.id_item
					DBSession.add(relacion)
			else:
				relacion = RelacionItem()
				relacion.relacion_parentesco = 1
				relacion.id_item_actual = kw['relaciones']
				relacion.id_item_relacionado = item.id_item
				DBSession.add(relacion)

			DBSession.flush()

		else:
			if relacion != []:
				DBSession.delete(relacion[0])

		fase = DBSession.query(Fase).get(item.fase)
		grafo = item_util.proyectGraphConstructor(fase.proyecto)
		item_util.marcar_en_revision(grafo, item.id_item)

		#la linea del item modificado permanece abierta
		if item.linea_base != None:
			linea = item.linea_base
			linea.estado = estado_linea_base_util.get_by_codigo('Abierta')

		flash("El item " +str(item.nombre)+ " ha sido modificado correctamente.")
		redirect('/miproyecto/fase/item/ver/'+str(item.id_item))

	@expose()
	def poner_en_revision(self, id_item):

		item = DBSession.query(Item).get(id_item)
		fase = DBSession.query(Fase).get(item.fase)
		grafo = item_util.proyectGraphConstructor(fase.proyecto)

		item_util.marcar_en_revision(grafo, item.id_item)

		flash("El item " +str(item.nombre)+ " fue puesto en revision.", 'warning')
		redirect('/miproyecto/fase/item/ver/'+str(item.id_item))

	"""
	Falta verificar si deja huerfano a alguien!
	"""
	@require(predicates.has_permission('eliminar_item'))
	@expose()
	def eliminar(self, id_item):
		#se utiliza el campo estado para determinar en la tabla historial que
		#esta muerto
		item = item_util.get_current(id_item)


		has_permiso = fase_util.check_fase_permiso(item.fase,'ver_item',True)
		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+ \
				str(self.params['item'].fase),'error')

			redirect('/miproyecto/fase/item/error')

		#validar que no pertenezca a una linea base
		if (not item_util.verificar_linea_base(item)):
			flash('El item pertence a un linea base Cerrada y no puede ser eliminado')
			redirect("/miproyecto/fase/item/ver/"+str(item.id_item))

		if item_util.deja_huerfanos(item):
			flash('El item no puede ser eliminado ya que algun item de la fase siguiente depende de este')
			redirect("/miproyecto/fase/item/ver/"+str(item.id_item))

		#estado muerto
		item.estado = 4
		item_util.audit_item(item)
		relaciones = DBSession.query(RelacionItem).\
								filter((RelacionItem.id_item_actual or\
								RelacionItem.id_item_actual) == id_item).\
								all()
		#se eliminan las relaciones que contienen al item
		for relacion in relaciones:
			DBSession.delete(relacion)

		DBSession.flush()

		DBSession.delete(item)
		flash("El item fue eliminado con exito")
		redirect("/miproyecto/fase/get_all/"+str(item.fase))

	@expose()
	def aprobar_item(self, iditem, **kw):
		"""
		Metodo para aprobar un item
		"""
		item = DBSession.query(Item).get(iditem)
		item.estado = 1
		idfase = item.fase
		DBSession.merge(item)
		flash("El item " + item.codigo+ " ha sido aprobado correctamente")
		redirect('/miproyecto/fase/item/ver/'+str(iditem))
	"""
	@expose('sap.templates.list')
	@require(predicates.has_permission('editar_item'))
	def historial_versiones(self, id_item):
		versiones = DBSession.query(HistorialItem).\
								filter(HistorialItem.id_item==id_item).\
								all()
		tmpl_context.widget = historial_table
		value = historial_filler.get_value(versiones)
		self.params['title'] = 'Versiones Anteriores'
		self.params['modelname'] = 'Historial'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/'
		self.params['permiso'] = 'NONE'
		self.params['idfase'] = 'NONE'
		return dict (value=value, params=self.params)
	"""

	@require(predicates.has_permission('editar_item'))
	@expose('sap.templates.list_pagination')
	@paginatedeco("historiales", items_per_page=10)
	def historial_versiones(self, id_item):
		historiales = DBSession.query(HistorialItem).\
								filter(HistorialItem.id_item==id_item).\
								all()

		tmpl_context.widget = historial_table
		filler = historial_filler

		self.params['title'] = 'Versiones Anteriores'
		self.params['modelname'] = 'Historial'
		self.params['header_file'] = 'item'
		self.params['new_url'] = '/'
		self.params['permiso'] = 'NONE'
		self.params['idfase'] = 'NONE'
		self.params['item'] = DBSession.query(Item).get(id_item)
		return dict (params=self.params, filler=filler, historiales=historiales)

	@expose()
	@require(predicates.has_permission('editar_item'))
	def revertir(self, id_historial):
		historial = DBSession.query(HistorialItem).get(id_historial)
		item = DBSession.query(Item).get(historial.id_item)
		# Se registra en el historial el item antes de ser revertido

		linea_base = item.linea_base
		if linea_base != None :
			estado_linea_base = linea_base.estado
			if(estado_linea_base.nombre == 'Cerrada' or estado_linea_base.nombre == 'Comprometida'):
				flash("El item pertenece a una linea base Cerrada!", 'error')
				redirect("/miproyecto/fase/item/ver/"+str(item.id_item))

		item_util.audit_item(item)
		#se revierte
		item_util.revertir_item(historial)
		redirect("/miproyecto/fase/item/ver/"+str(item.id_item))

	@expose('sap.templates.impacto')
	@require(predicates.has_permission('editar_item'))
	def impacto(self, id_item,**kw):
		item = DBSession.query(Item).get(id_item)
		fase = DBSession.query(Fase).get(item.fase)
		grafo = item_util.proyectGraphConstructor(fase.proyecto)
		nodos = []
		impacto, nodos = item_util.calcular_impacto(grafo, item.id_item)
		item_util.dibujar_grafo(nodos, item, impacto)
		self.params['cantidad'] = len(nodos)
		self.params['impacto'] = impacto
		self.params['item'] = item
		return dict(params = self.params)


	@expose('sap.templates.fase')
	@require(predicates.has_permission('editar_item'))
	def items_borrados(self, id_fase):
		#se obtienen los items borrados de esta fase que tengan estado
		#"muerto" (4)
		muertos = DBSession.query(HistorialItem).\
								filter(HistorialItem.fase==id_fase).\
								filter(HistorialItem.estado==4).\
								all()

		tmpl_context.widget = historial_revivir_table
		value = historial_revivir_filler.get_value(muertos)
		self.init_params(id_fase)

		self.params['title'] = 'Items borrados '
		self.params['modelname'] = 'Items Borrados'
		self.params['header_file'] = 'fase'
		self.params['new_url'] = '/'
		self.params['permiso'] = 'NONE'
		#self.params['idfase'] = 'NONE'
		return dict (value=value, params=self.params)

	def init_params(self, id):
		#para saber si mostrar o no el boton editar
		permiso_editar = fase_util.check_fase_permiso(id,
												'editar_fase')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = fase_util.check_fase_permiso(id,
											'administrar_participantes')
		usuarios = util.get_usuarios_by_fase(id)

		fase = fase_util.get_current(id)
		roles = util.get_roles_by_proyectos(fase.proyecto)
		value = participantes_fase_filler.get_value(roles)

		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		self.params['fase'] = fase
		self.params['idfase'] = id
		self.params['usuarios'] = usuarios

	@expose()
	@require(predicates.has_permission('editar_item'))
	def revivir(self, id_historial):
		historial = DBSession.query(HistorialItem).get(id_historial)
		#se revive el item a partir de su historial
		item_util.revivir_item(historial)
		#se elimina el historial del item muerto
		DBSession.delete(historial)
		redirect("/miproyecto/fase/item/ver/"+str(historial.id_item))

