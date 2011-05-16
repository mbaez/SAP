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

header_file="administracion"

class UsuarioContoller(RestController):
	"""
	prueba de abm y de visibilidad de datos en el template master.html
	anhadi py:if="tg.predicates.has_permission('manage')" para que solo
	muestre el link a los usuarios que posean el permiso 'manage'
	ademas los metodos de new_usuario, create_usuario y list_usuario estan
	anotados con @require(predicates.has_permission('manage')) esto es para que
	no se pueda acceder a al formulario atravez de la url.
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new(self, modelname='',**kw):
		tmpl_context.widget = new_usuario_form
		return dict(value=kw,header_file=header_file, modelname='Usuario')

	@validate(new_usuario_form, error_handler=new)
	@expose()
	def post(self, modelname='', **kw):
		del kw['sprox_id']
		usuario = Usuario(**kw)
		DBSession.add(usuario)
		flash("El usuario ha sido creado correctamente.")
		redirect("/administracion/usuario/list")

	@expose('sap.templates.edit')
	@require(predicates.has_permission('manage'))
	def edit(self, id,**kw):
		usuario =  DBSession.query(Usuario).get(id)
		tmpl_context.widget = usuario_edit_form
		kw['id_usuario'] = usuario.id_usuario
		kw['username'] = usuario.username
		kw['nombre'] = usuario.nombre
		kw['apellido'] = usuario.apellido
		kw['contrasenha'] = usuario.contrasenha
		kw['mail'] = usuario.mail
		kw['observacion'] = usuario.observacion
		kw['estado'] = usuario.estado
		return dict(value=kw, header_file=header_file,modelname='Usuario')

	@validate(usuario_edit_form, error_handler=edit)
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		usuario = Usuario(**kw)
		DBSession.merge(usuario)
		flash("El usuario "+usuario.__str__()+"ha sido modificado correctamente.")
		redirect("/administracion/usuario/list")


	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list(self, **kw):
		"""Lista todos los usuarios de la base de datos"""
		tmpl_context.widget = usuario_table
		value = usuario_filler.get_value()
		new_url = "/administracion/usuario/new"
		return dict(modelname='Usuarios',header_file=header_file,new_url=new_url,value=value)

	@expose()
	def post_delete(self, id_usuario, **kw):
		DBSession.delete(DBSession.query(Usuario).get(id_usuario))
		flash("El usuario ha sido "+ id_usuario +" eliminado correctamente.")
		redirect("/usuario/list")

