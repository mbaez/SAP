# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.desarrollo import DesarrolloController
from sap.controllers.configuracion import ConfiguracionController

__all__ = ['RootController']


class ProyectosController(BaseController):
	
	
	modDesarrollo = DesarrolloController()
	
	modConfiguracion = ConfiguracionController()
	
	@expose('sap.templates.miproyecto')
	@require(predicates.has_permission('manage'))
	def ver(self, idproyecto):
		return dict(modelname='Proyecto', idproyecto=idproyecto)
	
	
	
	
