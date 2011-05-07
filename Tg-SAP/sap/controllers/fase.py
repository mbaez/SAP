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
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

__all__ = ['RootController']

class FaseController(BaseController):
	
	@expose('sap.templates.desarrollo.fase.list')
	@require(predicates.has_permission('manage'))
	def ver(self, idfase):
		return dict(modelname='Fase')
		
		
