# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

"""
solo para probar libreria y metodos
"""
from sap.controllers.item import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.error import ErrorController
from sap.controllers.secure import SecureController
from sap.controllers.administracion import AdministracionController
from sap.controllers.misproyectos import ProyectosController
from sap.controllers.proyecto import ProyectoController
from sap.controllers.checker import *

from tg import tmpl_context
from sap.widgets.listform import *

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

	administracion = AdministracionController()

	error = ErrorController()
	
	miproyecto = ProyectosController()
	
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
					came_from=url('/proyectos'))

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
		redirect('/proyectos')

	@expose()
	def post_logout(self, came_from=url('/')):
		"""
		Redirect the user to the initially requested page on logout and say
		goodbye as well.
		
		"""
		#flash(_('We hope to see you soon!'))
		redirect(url('/login'))
	
	@expose('sap.templates.list')
	@require(predicates.has_permission('ver_proyecto'))
	def proyectos(self, **kw):
		tmpl_context.widget = admin_proyecto_table
		proyectos = checker.get_poyect_list('ver_proyecto')
		value = admin_proyecto_filler.get_value(proyectos)
		header_file="administracion"
		new_url = "/proyecto/new"
		return dict(modelname='Proyectos', header_file=header_file, new_url=new_url, value=value)
	"""
	metodo para probar el calculo de impacto
	"""
	@expose('sap.templates.index')
	def prueba(self):
		#contruye el grafo del proyecto 1 en este caso
		grafo = item.proyectGraphConstructor(1)
		#construye el grafo de la fase 1 del proyecto 1
		grafo2 = item.faseGraphConstructor(1)
		#construye el grafo de la fase 2 del proyecto 1
		grafo3 = item.faseGraphConstructor(2)
		
		impacto = item.calcularImpacto(grafo, 2)
		
		flash("Grafo de la fase 1 " + str(grafo2)+\
					" Grafo de la fase 2 "+ str(grafo3)+\
					" Grafo del proyecto 1 "+ str(grafo)+\
					" calculo de impacto del item 2 = "+ str(impacto))
		
		redirect('/')
