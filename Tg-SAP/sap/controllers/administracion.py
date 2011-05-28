# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.usuario import UsuarioContoller
from sap.controllers.proyecto import ProyectoController
from sap.controllers.rol import RolController




class AdministracionController(BaseController):

	usuario = UsuarioContoller()

	proyecto = ProyectoController()

	rol = RolController()

	@expose('sap.templates.administracion.index')
	def index(self):
		"""Handle the front-page."""
		return dict(page='index')

