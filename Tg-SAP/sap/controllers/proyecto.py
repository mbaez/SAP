# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""
Import the usuario widget
"""
from tg import tmpl_context
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

class ProyectoController(RestController):

	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new(self, **kw):
		tmpl_context.widget = new_proyecto_form
		return dict(value=kw, modelname='Proyecto')
		
	@validate(new_proyecto_form, error_handler=new)
	@expose()
	def post(self, modelname, **kw):
		del kw['sprox_id']
		kw['lider'] = DBSession.query(Usuario).get(kw['lider'])
		kw['estado'] = DBSession.query(EstadoProyecto).get(kw['estado'])
		proyecto = Proyecto(**kw)
		DBSession.add(proyecto)
		flash("El proyecto ha sido creado correctamente.")
		redirect("/proyecto/list")
	
	@expose('sap.templates.edit')
	@require(predicates.has_permission('manage'))
	def edit(self, id,**kw):
		proyecto =  DBSession.query(Proyecto).get(id)
		tmpl_context.widget = proyecto_edit_form
		kw['id_proyecto'] = proyecto.id_proyecto
		kw['nombre'] = proyecto.nombre
		kw['lider'] = DBSession.query(Usuario).all() # get(proyecto.lider_id)
		kw['estado'] = DBSession.query(EstadoProyecto).all() #get( proyecto.estado)
		kw['lider_id'] = proyecto.lider_id
		kw['estado_id'] = proyecto.estado_id
		kw['nro_fases'] = proyecto.nro_fases
		kw['descripcion'] = proyecto.descripcion
		return dict(value=kw, modelname='Proyecto')
	
	@validate(proyecto_edit_form, error_handler=edit)
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		kw['lider'] = DBSession.query(Usuario).get(kw['lider'])
		kw['estado'] = DBSession.query(EstadoProyecto).get(kw['estado'])
		proyecto = Proyecto(**kw)
		DBSession.merge(proyecto)
		flash("El proyecto ha sido modificado correctamente.")
		redirect("/proyecto/list")
	

	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list(self, **kw):
		"""Lista todos los proyectos de la base de datos"""
		tmpl_context.widget = proyecto_table
		value = proyecto_filter.get_value()
		return dict(modelname='Proyectos',value=value)
	
	@expose()
	def post_delete(self, id_proyecto, **kw):
		DBSession.delete(DBSession.query(Proyecto).get(id_proyecto))
		flash("El proyecto ha sido "+ id_proyecto +" eliminado correctamente.")
		redirect("/proyecto/list")
	
