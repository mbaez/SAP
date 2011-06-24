# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""
Import create and tablefilter widget
"""
from tg import tmpl_context
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController
#import del util
from sap.controllers.util import *

class UsuarioContoller(RestController):
	"""
	Controlador del Usuario
	"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':'', 'label': '', 'cancelar_url':''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_usuario'))
	def new(self, args={}, **kw):
		"""
		Encargado de cargar el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		tmpl_context.widget = new_usuario_form
		self.params['title'] = 'Nuevo usuario'
		self.params['modelname'] = 'Usuario'
		self.params['header_file'] = 'administracion'
		self.params['cancelar_url'] = '/administracion/usuario'
		return dict(value=kw,params=self.params)

	@validate(new_usuario_form, error_handler=new)
	@expose()
	@require(predicates.has_permission('crear_usuario'))
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
		usuario = Usuario(**kw)
		DBSession.add(usuario)
		flash("El usuario ha sido creado correctamente.")
		redirect("/administracion/usuario/get_all")

	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_usuario'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del usuario.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""
		tmpl_context.widget = usuario_edit_form
		kw['usuario_id'] = id
		value = usuario_edit_filler.get_value(kw)
		self.params['title'] = 'Titulo'
		self.params['modelname'] = 'Usuario'
		self.params['header_file'] = 'administracion'
		return dict(value=value,params=self.params)

	@validate(usuario_edit_form, error_handler=edit)
	@expose()
	def put(self, id, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		ecargado de persistir las modificaciones de las instancias.

		@type  id : Integer
		@param id : Identificador del usuario.

		@type  kw : Hash
		@param kw : Keywords

		"""

		usuario = DBSession.query(Usuario).get( int(id) )

		usuario.nombre = kw['nombre']
		usuario.email_address = kw['email_address']

		if usuario._password != kw['password'] :
			print 'Actualizando la contrasenha'
			usuario._set_password(kw['password'])

		DBSession.merge(usuario)
		flash("El usuario '"+usuario.nombre+"' ha sido modificado correctamente.")
		redirect("/administracion/usuario/get_all")


	@expose('sap.templates.list')
	@require(predicates.has_permission('admin_usuario'))
	def get_all(self, **kw):
		"""Lista todos los usuarios de la base de datos"""
		tmpl_context.widget = usuario_table
		value = usuario_filler.get_value()
		self.params['title'] = 'Titulo'
		self.params['modelname'] = 'Usuario'
		self.params['header_file'] = 'administracion'
		self.params['permiso'] = 'crear_usuario'
		self.params['new_url'] = '/administracion/usuario/new'
		self.params['label'] = 'Nuevo Usuario'
		return dict(value=value,params=self.params)

	@expose()
	@require(predicates.has_permission('eliminar_usuario'))
	def post_delete(self, id_usuario, **kw):
		DBSession.delete(DBSession.query(Usuario).get(id_usuario))
		flash("El usuario ha sido "+ id_usuario +" eliminado correctamente.")
		redirect("/administracion/usuario/get_all")
