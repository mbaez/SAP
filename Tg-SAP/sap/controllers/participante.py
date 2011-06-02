# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from tg.controllers import RestController
from sap.model import *
from sap.model import DBSession, metadata
#from sap.controllers.fase import FaseController
#import de widgets
from sap.widgets.editform import *
#impot del checker de permisos
from sap.controllers.checker import *


class ParticipanteController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''}

	current_fase = None
	
	@expose('sap.templates.fase')
	@require(predicates.has_permission('administrar_participantes'))
	def get_all(self, id , **kw):
		"""
		
		@type  id : Integer
		@param id : Identificador del proyecto.
		
		@type  kw :
		@param kw : 
		
		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		fase = self._get_current_fase(idproyecto)
		usuarios = util.get_usuarios_by_permiso(idproyecto)

		tmpl_context.widget = participantes_table

		roles = util.get_roles_by_proyectos(idproyecto)
		value = participantes_filler.get_value(roles)
		
		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'
		self.params['fase'] = fase
		self.params['usuarios'] = usuarios
		
		return dict(value=value, params=self.params)

	@expose('sap.templates.edit')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id,**kw):
		tmpl_context.widget = rol_usuario_edit_form
		kw['rol_id'] = id

		value = rol_usuario_edit_filler.get_value(kw)

		proyecto = self._get_current_proyect()
		usuarios = util.get_usuarios_by_permiso(proyecto.id_proyecto)
		
		self.params['proyecto'] = proyecto
		self.params['usuarios'] = usuarios
		self.params['modelname'] = 'Rol'
		self.params['header_file'] = 'proyecto'
		return dict(value=value, params=self.params)

	@validate(rol_usuario_edit_form, error_handler=edit)
	@expose()
	@require(predicates.has_permission('administrar_participantes'))
	def put(self, id, **kw):
		rol = DBSession.query(Rol).get(int(kw['rol_id']))
		fase = self._get_current_fase()
		util.asociar_rol_fase(rol.codigo, fase.id_fase)

		flash("El rol ha sido"+rol.nombre+" modificado correctamente.")
		redirect("/miproyecto/participantes/" + str(proyecto.id_proyecto) )

	def _get_current_fase(self, id=0):
		if self._current_fase == None:
			self._current_fase = DBSession.query(Fase).get(id)

		return self._current_fase
