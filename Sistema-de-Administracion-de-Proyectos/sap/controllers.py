# -*- coding: utf-8 -*-
"""This module contains the controller classes of the application."""

# symbols which are imported by "from sap.controllers import *"
__all__ = ['Root']

# standard library imports
# import logging
import datetime

# third-party imports
from turbogears import controllers, expose, flash

# project specific imports
from model import *
# from sap import json
#
from sqlalchemy.orm import sessionmaker

from turbogears.widgets import DataGrid
# log = logging.getLogger("sap.controllers")


class Root(controllers.RootController):
	"""The root controller of the application."""
	@expose(template="sap.templates.welcome")
	def index(self):
		""""Show the welcome page."""
		flash(_(u"Your application is now running now!!"))
		return dict(now=datetime.datetime.now())

	@expose(template = "sap.templates.permisos")
	def permisos(self):
		Session = sessionmaker(bind = get_engine())
		session = Session()
		permisos = session.query(Permiso).all()
		permiso_campos =[ ('Id Permiso', 'id_permiso'), 
						  ('Nombre','nombre'), 
						  ('Descripcion','descripcion')
						]
		permiso_widget = DataGrid(fields = permiso_campos)
		widget_permiso = permiso_widget.display(permisos)
		
		return dict (widget_permiso=widget_permiso)
