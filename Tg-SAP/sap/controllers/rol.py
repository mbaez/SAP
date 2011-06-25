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


class RolController(RestController):
	"""Controlador de los roles"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':'', 'label':'', 'cancelar_url':''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_rol'))
	def new(self, **kw):
		"""
		Encargado de cargar el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		tmpl_context.widget = new_rol_form

		self.params['title'] = 'Nuevo Rol'
		self.params['modelname'] = 'Rol'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'crear_rol'
		self.params['cancelar_url'] = '/administracion/rol'
		return dict(value=kw, params=self.params)

	@validate(new_rol_form, error_handler=new)
	@expose()
	def post(self, args={}, **kw):
		"""
		Evento invocado luego de un evento post en el form de crear
		ecargado de persistir las nuevas instancias.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""

		del kw['sprox_id']
		rol = Rol()
		rol.codigo = kw['codigo']
		rol.nombre = kw['nombre']
		rol.descripcion = kw['descripcion']

		for permiso in kw['permisos'] :
			rol.permisos.append(DBSession.query(Permiso).get(permiso))

		DBSession.add(rol)
		flash("El rol ha sido creado correctamente.")
		redirect("/administracion/rol/get_all")

	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_rol'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del Rol.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		tmpl_context.widget = rol_edit_form
		kw['rol_id'] = id
		value = rol_edit_filler.get_value(kw)
		self.params['modelname'] = 'Rol'
		self.params['header_file'] = 'administracion'
		self.params['permiso'] = 'editar_rol'
		return dict(value=value, params=self.params)

	@validate(rol_edit_form, error_handler=edit)
	@expose()
	def put(self, args={}, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		ecargado de persistir las modificaciones de las instancias.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""
		del kw['sprox_id']
		rol = DBSession.query(Rol).get(int(kw['rol_id']))
		rol.nombre = kw['nombre']
		rol.codigo = kw['codigo']
		rol.descripcion = kw['descripcion']
		rol.is_template = kw['is_template']
		rol.permisos = []

		for permiso_id in kw['permisos'] :
			rol.permisos.append(DBSession.query(Permiso).get(permiso_id))

		DBSession.merge(rol)
		flash("El rol '"+rol.nombre+"' ha sido modificado correctamente.")
		redirect("/administracion/rol/get_all")


	@expose('sap.templates.list')
	@require(predicates.has_permission('admin_rol'))
	def get_all(self, **kw):
		"""Lista todos los roles de la base de datos"""
		tmpl_context.widget = rol_table
		value = rol_filler.get_value()
		self.params['new_url'] = 'new/'
		self.params['modelname'] = 'Roles'
		self.params['header_file'] = 'administracion'
		self.params['permiso'] = 'crear_rol'
		self.params['label'] = 'Nuevo Rol'
		return dict(value=value, params=self.params)

	@expose()
	def post_delete(self, id_rol, **kw):
		DBSession.delete(DBSession.query(Rol).get(id_rol))
		flash("El rol ha sido "+ id_rol +" eliminado correctamente.")
		redirect("/administracion/rol/get_all")

