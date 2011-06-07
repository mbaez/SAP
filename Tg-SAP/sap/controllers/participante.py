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


class ParticipanteFaseController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''}

	_current_fase = None

	@expose('sap.templates.fase')
	@require(predicates.has_permission('administrar_participantes'))
	def admin(self, id , **kw):
		"""
		@type  id : Integer
		@param id : Identificador de la fase.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		fase = self._get_current_fase(id)

		usuarios = util.get_usuarios_by_fase(id)

		tmpl_context.widget = participantes_table

		roles = util.get_roles_by_proyectos(fase.proyecto)
		value = participantes_fase_filler.get_value(roles)
				#para saber si mostrar o no el boton editar
		permiso_editar = checker.check_fase_permiso(id,
												'editar_fase')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = checker.check_fase_permiso(id,
											'administrar_participantes')

		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'
		self.params['fase'] = fase
		self.params['idfase'] = id
		self.params['usuarios'] = usuarios

		return dict(value=value, params=self.params)

	@expose('sap.templates.edit')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id,**kw):
		"""
		@type  id : Integer
		@param id : Identificador de la fase.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""

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
		usuarios = util.get_usuarios_by_fase(fase.id_fase)

		self.params['fase'] = fase
		self.params['usuarios'] = usuarios
		self.params['modelname'] = 'Participantes'
		self.params['header_file'] = 'proyecto'
		return dict(value=value, params=self.params)

	@validate(rol_usuario_edit_form, error_handler=edit)
	@expose()
	@require(predicates.has_permission('administrar_participantes'))
	def put(self, id, **kw):
		"""
		@type  id : Integer
		@param id : Identificador de la fase.

		@type  kw : Hash
		@param kw : Keywords
		"""

		fase = self._get_current_fase()
		for usuario_id in kw['usuarios'] :
			util.asociar_usuario_fase(usuario_id, fase.id_fase)

		flash("Los Usuarios <"+str(kw['usuarios'])+"> fueron asignados a la fase "+ str(fase.id_fase)+".")
		redirect("/miproyecto/fase/get_all/" + str(fase.id_fase) )

	@expose()
	def delete(self, id_fase ,id, **kw):
		"""
		@type  id_fase : Integer
		@param id_fase : Identificador de la fase.

		@type  id : Integer
		@param id : Identificador del usuario a desvincular.

		@type  kw : Hash
		@param kw : Keywords
		"""
		fase = self._get_current_fase()
		list = DBSession.query(UsuarioPermisoFase).\
				filter(UsuarioPermisoFase.usuario_id == id).\
				filter(UsuarioPermisoFase.fase_id == id_fase)

		for element in list :
			DBSession.delete(element)

		flash("El usuario '"+ str(id) +"' ha sido desvinculado de la fase.")
		redirect("/miproyecto/fase/get_all/"+ str(id_fase))

	def _get_current_fase(self, id=0):
		"""
		@type  id : Integer
		@param id : Identificador de la fase.

		@rtype  : Fase
		@return : La fase actual
		"""
		if self._current_fase == None or \
		   self._current_fase.id_fase != id  and id != 0:

				self._current_fase = DBSession.query(Fase).get(id)

		return self._current_fase



class ParticipanteProyectoController(RestController):

	_current_proyect = None

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''}

	@expose('sap.templates.miproyecto')
	@require(predicates.has_permission('administrar_participantes'))
	def admin(self, idproyecto , **kw):
		"""
		@type  idproyecto : Integer
		@param idproyecto : Identificador del proyecto.

		@type  kw : Hash
		@param kw : Keyword

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		proyecto = self._get_current_proyect(idproyecto)
		usuarios = util.get_usuarios_by_permiso(idproyecto)

		tmpl_context.widget = participantes_table

		roles = util.get_roles_by_proyectos(idproyecto)
		value = participantes_filler.get_value(roles)
		#para saber si mostrar o no el boton editar
		permiso_editar = checker.check_proyecto_permiso(idproyecto,
												'editar_proyecto')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = checker.check_proyecto_permiso(idproyecto,
											'administrar_participantes')

		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'
		self.params['proyecto'] = proyecto
		self.params['usuarios'] = usuarios
		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		return dict(value=value, params=self.params)

	@expose('sap.templates.edit')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id,**kw):
		"""
		@type  id : Integer
		@param id : Identificador del proyecto.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""

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

		self.params['modelname'] = 'Participantes'
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
		redirect("/miproyecto/ver/" + str(proyecto.id_proyecto))

	@expose()
	def delete(self, proyecto_id ,id, **kw):
		"""
		@type  proyecto_id : Integer
		@param proyecto_id : Identificador del proyecto

		@type  id : Integer
		@param id : Identificador del usuario a desvincular.

		@type  kw : Hash
		@param kw : Keywords
		"""
		#se obtienen las relaciones del usuario sobre las fases del proyecto
		list = DBSession.query(UsuarioPermisoFase).\
				filter(UsuarioPermisoFase.usuario_id == id).\
				filter(Fase.proyecto == proyecto_id).\
				filter(UsuarioPermisoFase.fase_id == Fase.id_fase)
		#Se eliminan las relaciones del usuario con las fases
		for element in list :
			DBSession.delete(element)
		#Se obtienen los roles del usuario en el proyecto
		list = DBSession.query(RolUsuario).\
				  filter(RolUsuario.usuario_id == id).\
				  filter(RolUsuario.rol_id == RolPermisoProyecto.rol_id).\
				  filter(RolPermisoProyecto.proyecto_id == proyecto_id)
		#Se eliminan los roles del usuario sobre el proyecto
		for element in list :
			DBSession.delete(element)

		flash("El usuario '"+ str(id) +"' ha sido desvinculado del proyecto.")
		redirect("/miproyecto/ver/"+str(proyecto_id))


	def _get_current_proyect(self, id=0):
		"""
		@type  id : Integer
		@param id : Identificador del proyecto.

		@rtype  : Proyecto
		@return : El proyecto actual
		"""
		if self._current_proyect == None or \
		   self._current_proyect.id_proyecto != id and id != 0:
				self._current_proyect = DBSession.query(Proyecto).get(id)

		return self._current_proyect
