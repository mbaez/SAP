# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.fase import FaseController
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
#impot del checker de permisos
from sap.controllers.checker import *

__all__ = ['RootController']

class ProyectosController(BaseController):


	fase = FaseController()

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
		new_url = "/miproyecto/fase/" +idproyecto+ "/new"

		proyecto = DBSession.query(Proyecto).get(idproyecto)
		usuarios = util.__get_usuarios_proyecto__(idproyecto)

		return dict(modelname='Fases', idproyecto=idproyecto,
						proyecto=proyecto, usuarios=usuarios,
						new_url=new_url, value=value)




