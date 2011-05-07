# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""

"""
from tg import tmpl_context

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

class CheckerController(RestController):
	@expose()
	def check_proyecto_permiso(self, id_proyecto, permiso_name,nuleable=False):
		"""
		Controla si el usuario logeado posee permisos sobre el proyecto
		"""
		current_user = self.get_current_user()
		rol_permiso_proyecto = DBSession.query(RolPermisoProyecto).\
								filter(RolPermisoProyecto.group_id ==
									RolUsuario.group_id).\
								filter(RolPermisoProyecto.proyecto_id ==
									id_proyecto).\
								filter(Permiso.permission_id ==
									RolPermisoProyecto.permission_id).\
								filter(Permiso.permission_name ==
									permiso_name).\
								filter(RolUsuario.user_id == 
									current_user.user_id).\
								all()
								
		if (len(rol_permiso_proyecto) != 0):
			return predicates.has_permission(permiso_name)
		elif nuleable == False:
			return predicates.has_permission(permiso_name+' '+str(id_proyecto))
		else:
			return None
	
	
	def get_current_user(self):
		identity = request.environ.get('repoze.who.identity')
		username = identity['repoze.who.userid']
		
		current_user = DBSession.query(Usuario).\
				filter(Usuario.user_name == username ).\
				first()
		return current_user
	
	
	def get_poyect_list(self, permiso_name):
		current_user = self.get_current_user()
		
		proyectos = DBSession.query(Proyecto).\
					filter(RolPermisoProyecto.group_id ==
						RolUsuario.group_id).\
					filter(RolPermisoProyecto.proyecto_id ==
						Proyecto.id_proyecto).\
					filter(Permiso.permission_id ==
						RolPermisoProyecto.permission_id).\
					filter(Permiso.permission_name ==
						permiso_name).\
					filter(RolUsuario.user_id == 
						current_user.user_id).\
					all()
		return proyectos

checker =  CheckerController()
