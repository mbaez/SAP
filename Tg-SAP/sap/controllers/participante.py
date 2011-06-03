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
from sap.widgets.listform import *
from sap.widgets.editform import *
#impot del checker de permisos
from sap.controllers.checker import *


class ParticipanteController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''}

	_current_fase = None

	@expose('sap.templates.fase')
	@require(predicates.has_permission('administrar_participantes'))
	def admin(self, id , **kw):
		"""

		@type  id : Integer
		@param id : Identificador del proyecto.

		@type  kw :
		@param kw :

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		fase = self._get_current_fase(id)
		print "FASE: "+ str(fase)
		usuarios = util.get_usuarios_by_fase(fase.proyecto)
		print "USUARIOS: "+ str(usuarios)

		tmpl_context.widget = participantes_table

		roles = util.get_roles_by_proyectos(fase.proyecto)
		value = participantes_fase_filler.get_value(roles)

		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'
		self.params['fase'] = fase
		self.params['usuarios'] = usuarios

		return dict(value=value, params=self.params)

	@expose('sap.templates.edit')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id,**kw):
		tmpl_context.widget = rol_usuario_edit_form
		rol = DBSession.query(Rol).get(id)
		kw['rol_id'] = id
		if rol.is_template == True :
			kw['codigo'] = rol.codigo
			kw['nombre'] = rol.nombre
			value = kw
		else:
			value = rol_usuario_edit_filler.get_value(kw)

		fase = self._get_current_fase()
		usuarios = util.get_usuarios_by_fase(fase.proyecto)

		print "Usuarios "+ str(usuarios)

		#self.params['fase'] = fase
		self.params['usuarios'] = usuarios
		self.params['modelname'] = 'Participantes'
		self.params['header_file'] = 'proyecto'
		return dict(value=value, params=self.params)

	@validate(rol_usuario_edit_form, error_handler=edit)
	@expose()
	@require(predicates.has_permission('administrar_participantes'))
	def put(self, id, **kw):
		#rol = DBSession.query(Rol).get(int(kw['rol_id']))
		fase = self._get_current_fase()
		for usuario_id in kw['usuarios'] :
			util.asociar_usuario_fase(usuario_id, fase.id_fase)

		flash("Los Usuarios <"+str(kw['usuarios'])+"> fueron asignados a la fase "+ str(fase.id_fase)+".")
		redirect("/miproyecto/fase/participantes/admin/" + str(fase.proyecto) )

	def _get_current_fase(self, id=0):
		if self._current_fase == None:
			self._current_fase = DBSession.query(Fase).get(id)

		return self._current_fase
