# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
# imports del modelo
from sap.model import *
from tg import tmpl_context, redirect, validate
#impot del checker de permisos
from sap.controllers.checker import *
#import de los controladores utilizados en la fase
from sap.controllers.item import *
from sap.controllers.tipo_item import TipoItemController
from sap.controllers.relacion import RelacionController
from sap.controllers.linea_base import LineaBaseController
from sap.controllers.participante import ParticipanteController
#import del controlador
from tg.controllers import RestController

class FaseController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'', 'label': '', 'cancelar_url': ''}

	item = ItemController()
	tipo_item = TipoItemController()
	relacion = RelacionController()
	linea_base = LineaBaseController()
	
	""" Contorlador de los participantes de la fase"""
	participantes = ParticipanteController()

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_fase'))
	def new(self, idproyecto, modelname, **kw):
		"""
		Encargado de carga el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear
		"""
		tmpl_context.widget = new_fase_form
		header_file = "abstract"
		self.params['title'] = 'Nueva Fase'
		self.params['modelname'] = 'Fase'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'crear_fase'
		self.params['cancelar_url'] = '/miproyecto/ver/'+str(idproyecto)
		return dict(value=kw, params = self.params)

	@validate(new_fase_form, error_handler=new)
	@require(predicates.has_permission('editar_fase'))
	@expose()
	def post(self, idproyecto, **kw):
		"""
		Evento invocado luego de un evento post en el form de crear
		ecargado de persistir las nuevas instancias.
		"""
		del kw['sprox_id']
		fase = Fase(**kw)
		fase.proyecto = idproyecto
		DBSession.add(fase)
		redirect("/miproyecto/ver/"+idproyecto)


	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		"""
		Encargado de carga el widget para editar las instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de editar
		"""
		fase =  DBSession.query(Fase).get(id)
		tmpl_context.widget = fase_edit_form
		kw['id_fase'] = fase.id_fase
		kw['nombre'] = fase.nombre
		kw['descripcion'] = fase.descripcion
		self.params['modelname'] = 'Fase'
		return dict(value=kw, params = self.params)


	@validate(fase_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		encargado de persistir las modificaciones de las instancias.
		"""
		del kw['sprox_id']
		fase = Fase(**kw)
		DBSession.merge(fase)
		flash("La fase '" + fase.nombre+ "'ha sido modificado correctamente.")
		redirect("/miproyecto/fase/list")


	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, **kw):
		"""
		Encargado de cargar el widget de listado, pueden acceder unicamente
		los usuarios que posena el permiso de ver, este widget se encuentra
		acompanhado de enlaces de editar y eliminar
		"""
		"""
		tmpl_context.widget = proyecto_table

		se obtiene la lista de los proyectos en los cuales pose el
		permiso de ver_proyecto

		proyectos = checker.get_poyect_list('ver_proyecto')
		value = proyecto_filler.get_value(proyectos)
		"""
		self.params['modelname'] = 'Fases'
		return dict(modelname='Fases')


	@expose()
	def post_delete(self, id_fase, **kw):
		"""
		Evento invocado desde el listado, se encarga de eliminar una instancia
		de la base de datos.
		"""
		DBSession.delete(DBSession.query(Fase).get(id_fase))
		flash("La fase "+ id_proyecto + "ha sido eliminada correctamente.")
		redirect("/miproyecto/fase/")

	@expose('sap.templates.fase')
	@require(predicates.has_permission('ver_fase'))
	def get_all(self, idfase, **kw):
		"""Lista todos los items de la fase"""
		tmpl_context.widget = item_table
		items = DBSession.query(Item).filter(Item.fase==idfase).all()
		value = item_filler.get_value(items)

		self.params['title'] = 'Titulo'
		self.params['modelname'] = 'Items'
		self.params['header_file'] = 'fase'
		self.params['permiso'] = 'crear_item'
		self.params['idfase'] = idfase
		self.params['fase'] = DBSession.query(Fase).get(idfase)
		self.params['new_url'] = '/miproyecto/fase/item/'+idfase+'/new/'
		self.params['label'] = 'Agregar Atributo'
		self.params['usuarios'] = util.get_usuarios_by_fase(self.params['fase'].proyecto)

		return dict(value=value, params = self.params)

