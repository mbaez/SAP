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

from sap.model import *
from tg import tmpl_context, redirect, validate

class UsuarioContoller(BaseController):
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
	def new (self, **kw):
		"""
		Despliega en pantalla el widget UsuarioForm que se encuentra
		en la carpeta widget
		"""
		tmpl_context.form = create_usuario_form
		
		return dict(modelname='Usuario',
			genre_options=DBSession.query(Usuario.id_usuario),
			page='Nuevo Usuario')


	@validate(create_usuario_form, error_handler=new)
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def create(self, **kw):
		"""
		El formulario envia los argumentos del formulario 
		a este metodo en la variable kw y estos seteados a una variable
		del tipo Usuario.
		"""
		usuario = Usuario()
		usuario.username = kw['username']
		usuario.nombre = kw['nombre']
		usuario.apellido = kw['apellido']
		usuario.contrasenha = kw['contrasenha']
		usuario.mail = kw['mail']
		usuario.observacion = kw['descripcion']
		usuario.estado = kw['estado']
		#guarda el usuario registrado en el formulario
		DBSession.add(usuario)
		#emite un mensaje y redirecciona a la pagina de listado
		flash("El usuario ha sido creado correctamente.")
		redirect("list")
		

	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list(self, **kw):
		"""Lista todos los usuarios de la base de datos"""
		list = DBSession.query(Usuario)
		items = [] 
		head = []
		'''
		Se anhade el nombre de las columnas
		'''
		head.append(['ID', 'Username', 'Nombre','Apellido', 'Contrasenha',
					'Mail','Observacion','Estado'] )
					
		'''
		Se formatea la entidad como una matriz para ser visualizada en la tabla
		'''
		for item in list:
			items.append([item.id_usuario, item.username, item.nombre,
							item.apellido, item.contrasenha, item.mail,
							item.observacion, item.estado]
						)
		
		return dict(array=items, headers=head, modelname='usuario',
					page='Lista de Usuarios')
