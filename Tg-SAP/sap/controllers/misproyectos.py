# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from tg.controllers import RestController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.fase import FaseController
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
#impot del checker de permisos
from sap.controllers.checker import *


class ProyectosController(RestController):

	fase = FaseController()

	_current_proyect = None

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''}

	@expose('sap.templates.miproyecto')
	@require(predicates.has_permission('ver_proyecto'))
	def ver(self, idproyecto):
		"""
		se obtiene la lista de las fases sobre las cuales el usurio
		tiene permisos de 'ver' y que pertenecen al proyecto que
		selecciono.

		@type  idproyecto : Integer
		@param idproyecto : Identificador del proyecto.

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		tmpl_context.widget = fase_table

		#listar todas las fases y mostrar unicamente el link de ver en aquellas
		#fases en los que posee permisos.
		fases = checker.get_fases_by_proyecto_list(idproyecto, 'ver_fase')
		value = fase_filler.get_value(fases)

		proyecto = self._get_current_proyect(idproyecto)
		usuarios = util.get_usuarios_by_permiso(idproyecto)
		text_header='Listado de Fases del Proyecto'

		self.params['modelname'] = 'Fases'
		self.params['text_header'] = 'Listado de Fases del Proyecto'
		self.params['idproyecto'] = idproyecto
		self.params['proyecto'] = proyecto
		self.params['usuarios'] = usuarios
		return dict(value=value, params=self.params)

	@expose('sap.templates.miproyecto')
	@require(predicates.has_permission('administrar_participantes'))
	def participantes(self, idproyecto , **kw):
		"""

		@type  idproyecto : Integer
		@param idproyecto : Identificador del proyecto.

		@type  kw :
		@param kw :

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		proyecto = self._get_current_proyect(idproyecto)
		usuarios = util.get_usuarios_by_permiso(idproyecto)

		tmpl_context.widget = participantes_table

		roles = util.get_roles_by_proyectos(idproyecto)
		value = participantes_filler.get_value(roles)

		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'
		self.params['proyecto'] = proyecto
		self.params['usuarios'] = usuarios
		return dict(value=value, params=self.params)

	@expose('sap.templates.edit')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id,**kw):
		tmpl_context.widget = rol_usuario_edit_form
		kw['rol_id'] = id
		rol = DBSession.query(Rol).get(id)
		if rol.is_template == True :
			kw['codigo'] = rol.codigo
			kw['nombre'] = rol.nombre
			value = kw
		else:
			value = rol_usuario_edit_filler.get_value(kw)

		proyecto = self._get_current_proyect()
		usuarios = util.get_usuarios_by_permiso(proyecto.id_proyecto)

		self.params['modelname'] = 'Rol'
		self.params['header_file'] = 'proyecto'
		return dict(value=value, params=self.params)

	@validate(rol_usuario_edit_form, error_handler=edit)
	@expose()
	@require(predicates.has_permission('administrar_participantes'))
	def put(self, id, **kw):
		rol = DBSession.query(Rol).get(int(kw['rol_id']))

		proyecto = self._get_current_proyect()

		rol.usuarios = []

		for user_id in kw['usuarios'] :
			util.asignar_participante(user_id,rol.codigo,proyecto.id_proyecto)

		flash("El rol ha sido "+rol.nombre+" modificado correctamente.")
		redirect("/miproyecto/participantes/" + str(proyecto.id_proyecto) )

	def _get_current_proyect(self, id=0):
		if self._current_proyect == None:
			self._current_proyect = DBSession.query(Proyecto).get(id)

		return self._current_proyect
