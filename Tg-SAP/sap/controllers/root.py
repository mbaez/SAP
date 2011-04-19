# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata
from sap.controllers.error import ErrorController
from sap.controllers.secure import SecureController

"""
Import the usuario widget
"""
from tg import tmpl_context
from sap.widgets.createform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

__all__ = ['RootController']


class RootController(BaseController):
	"""
	The root controller for the Tg-SAP application.

	All the other controllers and WSGI applications should be mounted on this
	controller. For example::

		panel = ControlPanelController()
		another_app = AnotherWSGIApplication()

	Keep in mind that WSGI applications shouldn't be mounted directly: They
	must be wrapped around with :class:`tg.controllers.WSGIAppController`.

	"""
	secc = SecureController()

	admin = Catwalk(model, DBSession)

	error = ErrorController()

	@expose('sap.templates.index')
	def index(self):
		"""Handle the front-page."""
		return dict(page='index')

	@expose('sap.templates.about')
	def about(self):
		"""Handle the 'about' page."""
		return dict(page='about')
	"""
	Solamente el usuario con el permiso de modificacion puede visualizar 
	el link ver master.html
	"""
	@expose('sap.templates.authentication')
	def auth(self):
		"""Display some information about auth* on this application."""
		return dict(page='auth')

	@expose('sap.templates.index')
	@require(predicates.has_permission('manage', msg=l_('Only for managers')))
	def manage_permission_only(self, **kw):
		"""Illustrate how a page for managers only works."""
		return dict(page='managers stuff')

	@expose('sap.templates.index')
	@require(predicates.is_user('editor', msg=l_('Only for the editor')))
	def editor_user_only(self, **kw):
		"""Illustrate how a page exclusive for the editor works."""
		return dict(page='editor stuff')

	@expose('sap.templates.login')
	def login(self, came_from=url('/')):
		"""Start the user login."""
		login_counter = request.environ['repoze.who.logins']
		if login_counter > 0:
			flash(_('Wrong credentials'), 'warning')
		return dict(page='login', login_counter=str(login_counter),
					came_from=came_from)

	@expose()
	def post_login(self, came_from=url('/')):
		"""
		Redirect the user to the initially requested page on successful
		authentication or redirect her back to the login page if login failed.
		
		"""
		if not request.identity:
			login_counter = request.environ['repoze.who.logins'] + 1
			redirect(url('/login', came_from=came_from, __logins=login_counter))
		userid = request.identity['repoze.who.userid']
		flash(_('Welcome back, %s!') % userid)
		redirect(came_from)

	@expose()
	def post_logout(self, came_from=url('/')):
		"""
		Redirect the user to the initially requested page on logout and say
		goodbye as well.
		
		"""
		flash(_('We hope to see you soon!'))
		redirect(url('/'))
	
	"""
	prueba de abm y de visibilidad de datos en el template master.html
	anhadi py:if="tg.predicates.has_permission('manage')" para que solo
	muestre el link a los usuarios que posean el permiso 'manage'
	ademas los metodos de new_usuario, create_usuario y list_usuario estan
	anotados con @require(predicates.has_permission('manage')) esto es para que 
	no se pueda acceder a al formulario atravez de la url.
	"""
	@expose('sap.templates.new_form')
	@require(predicates.has_permission('manage'))
	def new_usuario (self, **kw):
		"""
		Despliega en pantalla el widget UsuarioForm que se encuentra
		en la carpeta widget
		"""
		tmpl_context.form = create_usuario_form
		
		return dict(modelname='Usuario',
			genre_options=DBSession.query(Usuario.id_usuario),
			page='Nuevo Usuario')
	
	
	@validate(create_usuario_form, error_handler=new_usuario)
	@expose('sap.templates.new_form')
	@require(predicates.has_permission('manage'))
	def create_usuario(self, **kw):
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
		#usuario.observacion = kw['observacion']
		usuario.estado = kw['estado']
		#guarda el usuario registrado en el formulario
		DBSession.add(usuario)
		#emite un mensaje y redirecciona a la pagina de listado
		flash("Movie was successfully created.")
		redirect("list_usuarios")
		

	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list_usuarios(self, **kw):
		"""Lista todos los usuarios de la base de datos"""
		return dict(array=DBSession.query(Usuario), modelname='usuario',
					page='Lista de Usuarios')
