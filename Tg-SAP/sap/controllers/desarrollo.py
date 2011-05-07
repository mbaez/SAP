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

class DesarrolloController(BaseController):
	
	
	@expose('sap.templates.desarrollo.list')
	def list(self):
		return dict(modelname='Fase')
		
	@expose('sap.templates.desarrollo.reporte')	
	def reporte(self):
		return dict()
