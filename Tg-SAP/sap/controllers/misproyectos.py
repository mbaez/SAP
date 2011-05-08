# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

#import de widget
from sap.widgets.listform import *
from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.fase import FaseController
from sap.controllers.configuracion import ConfiguracionController

__all__ = ['RootController']


class ProyectosController(BaseController):
	
	
	fase = FaseController()
	modConfiguracion = ConfiguracionController()
	
	@expose('sap.templates.miproyecto')
	#@require(predicates.has_permission('manage'))
	def ver(self, idproyecto):
		tmpl_context.widget = fase_table
		"""
		se obtiene la lista de las fases sobre las cuales el usurio 
		tiene permisos de 'ver' y que pertenecen al proyecto que 
		selecciono
		"""
		fases = checker.get_fases_by_proyecto_list(idproyecto, 'ver_fase')
		value = fase_filler.get_value(fases)
		return dict(modelname='Fases', idproyecto=idproyecto, value=value)
	
	
	
	
