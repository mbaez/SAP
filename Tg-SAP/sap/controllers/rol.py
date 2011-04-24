# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""
Import widgets
"""
from tg import tmpl_context
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

class RolController(RestController):

	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new(self, **kw):
		tmpl_context.widget = new_rol_form
		return dict(value=kw, modelname='Rol')
		
	@validate(new_rol_form, error_handler=new)
	@expose()
	def post(self, modelname, **kw):
		del kw['sprox_id']
		rol = Rol(**kw)
		DBSession.add(rol)
		flash("El rol ha sido creado correctamente.")
		redirect("/rol/list")
	
	@expose('sap.templates.edit')
	@require(predicates.has_permission('manage'))
	def edit(self, id,**kw):
		rol =  DBSession.query(Rol).get(id)
		tmpl_context.widget = rol_edit_form
		kw['id_rol'] = rol.id_rol
		kw['nombre'] = rol.nombre
		kw['descripcion'] = rol.descripcion
		return dict(value=kw, modelname='Rol')
	
	@validate(rol_edit_form, error_handler=edit)
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		rol = Rol(**kw)
		DBSession.merge(rol)
		flash("El rol ha sido modificado correctamente.")
		redirect("/rol/list")
	

	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list(self, **kw):
		"""Lista todos los roles de la base de datos"""
		tmpl_context.widget = rol_table
		value = rol_filter.get_value()
		return dict(modelname='Rol',value=value)
	
	@expose()
	def post_delete(self, id_rol, **kw):
		DBSession.delete(DBSession.query(Rol).get(id_rol))
		flash("El rol ha sido "+ id_rol +" eliminado correctamente.")
		redirect("/rol/list")
	
