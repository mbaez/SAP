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
#import del controlador
from tg.controllers import RestController

class LineaBaseController(BaseController):

	"""
	Encargado de carga el widget para crear nuevas instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new(self, idfase, **kw):
		tmpl_context.widget = new_linea_base_form
		header_file = "abstract"
		return dict(value=kw, modelname= "LineaBase",header_file=header_file)
	
	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_linea_base_form, error_handler=new)
	@require(predicates.has_permission('manage'))
	@expose()
	def post(self, idfase, **kw):
		del kw['sprox_id']
		linea_base = LineaBase(**kw)
		linea_base.fase = idfase
		DBSession.add(linea_base)
		redirect("/proyectos")
	
	"""
	Encargado de carga el widget para editar las instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	#@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		linea_base =  DBSession.query(LineaBase).get(id)
		tmpl_context.widget = linea_base_edit_form
		kw['id_linea_base'] = linea_base.id_linea_base
		kw['fase'] = linea_base.fase
		kw['estado'] = linea_base.estado
		return dict(value=kw, modelname='LineaBase')

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(linea_base_edit_form, error_handler=edit)
	#@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		linea_base = LineaBase(**kw)
		DBSession.merge(linea_base)
		flash("La LB ha sido modificado correctamente.")
		redirect("/proyectos")
	
	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente 
	los usuarios que posena el permiso de ver, este widget se encuentra 
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, idfase, **kw):
		'''
		Lista todos tipos de items de la bd.
		Se debe modificar para que liste solo los
		de la fase actual
		'''
		tmpl_context.widget = linea_base_table
		value = linea_base_filler.get_value()
		header_file = "abstract"
		new_url = "/miproyecto/fase/linea_base/generarLineaBase/" + str(idfase)
		return dict(modelname='LineaBases', header_file = header_file,new_url=new_url, value=value)
		
	"""	
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_linea_base, **kw):
		DBSession.delete(DBSession.query(LineaBase).get(id_linea_base))
		flash("La linea base ha sido eliminada correctamente.")
		redirect("/proyectos")
		
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def ver(self, idfase, id_linea_base, **kw):
		tmpl_context.widget = item_table
		# Se obtienen los items de que pertenecen a la linea base de la 
		# fase actual.
		items = DBSession.query(Item).filter(Item.id_item == LineaBaseItem.id_item).\
									filter(Item.fase == idfase).\
									filter(LineaBaseItem.id_linea_base == id_linea_base).all()
		value = item_filler.get_value(items)
		header_file = "abstract"
		new_url = "/miproyecto/fase/linea_base/" + str(idfase) + "/new"
		return dict(modelname='LineaBases', header_file=header_file, new_url=new_url, value=value)
	
	@expose('sap.templates.new')
	def generarLineaBase(self, idfase, **kw):
		tmpl_context.widget = item_table
		#items = DBSession.query(Item).filter(Item.fase == idfase).\
		#							filter(Item.estado_id == 2)
		items = util.get_items_aprobados_by_fase(idfase)
		for i in items:
			i.complejidad = 33

		value = item_filler.get_value(items)
		new_url = "/miproyecto/fase/linea_base/" + str(idfase) + "/new"
		header_file = 'abstract'
		return dict(modelname='Items', header_file = header_file,new_url=new_url, value=value)
		
