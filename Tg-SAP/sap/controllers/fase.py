# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

__all__ = ['RootController']

class FaseController(BaseController):
	
	@expose('sap.templates.desarrollo.fase.list')
	#@require(predicates.has_permission('manage'))
	def ver(self, idfase):
		return dict(modelname='Fase')
		
	"""
	Encargado de carga el widget para crear nuevas instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	#@require(predicates.has_permission('crear_fase'))
	def new(self, **kw):
		tmpl_context.widget = new_fase_form
		return dict(value=kw, modelname='Fase')
	
	@validate(new_fase_form, error_handler=new)
	#@require(predicates.has_permission('crear_fase'))
	@expose()
	def post(self, modelname, **kw):
		del kw['sprox_id']
		fase = Fase(**kw)
		DBSession.add(fase)
		flash("El fase ha sido creada correctamente.")
		redirect("/miproyecto/fase/list")
	
	"""
	Encargado de carga el widget para editar las instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	#@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		fase =  DBSession.query(Fase).get(id)
		tmpl_context.widget = fase_edit_form
		kw['id_fase'] = fase.id_fase
		kw['nombre'] = fase.nombre
		kw['descripcion'] = fase.descripcion
		return dict(value=kw, modelname='Fase')

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(fase_edit_form, error_handler=edit)
	#@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		fase = Fase(**kw)
		DBSession.merge(fase)
		flash("La fase '" + fase.nombre+ "'ha sido modificado correctamente.")
		redirect("/miproyecto/fase/list")
	
	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente 
	los usuarios que posena el permiso de ver, este widget se encuentra 
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, **kw):
		"""
		tmpl_context.widget = proyecto_table
		
		se obtiene la lista de los proyectos en los cuales pose el
		permiso de ver_proyecto
		
		proyectos = checker.get_poyect_list('ver_proyecto')
		value = proyecto_filler.get_value(proyectos)
		"""
		return dict(modelname='Fases')
		
	"""	
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_fase, **kw):
		DBSession.delete(DBSession.query(Fase).get(id_fase))
		flash("La fase "+ id_proyecto + "ha sido eliminada correctamente.")
		redirect("/miproyecto/fase/list")

		
	
		
