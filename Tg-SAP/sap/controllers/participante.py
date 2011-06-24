# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates , authorize

from tg.controllers import RestController
from sap.model import *

#Se importan los widgets que van a ser utilizados
from sap.widgets.listform import *
from sap.widgets.editform import *
from sap.widgets.createform import *
#Import de util
from sap.controllers.util import *



class ParticipanteFaseController(RestController):
	""" Contorlador de los participantes de la fase"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	allow_only = authorize.has_permission('administrar_participantes' )
	"""
	Limita el acceso al controlador a aquellos que poseen el permiso de
	administrar participantes.
	"""

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
		has_permiso = session_util.authorize_fase('administrar_participantes',
													id)
		#se verifica si el usuario posee permisos sobre la fase actual
		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+str(id),'error')
			redirect('/miproyecto/fase/participantes/error')

		#se inicializa los parametros para el params
		fase = self.init_params(id)
		#se setea el widget a utilizar
		tmpl_context.widget = participantes_table
		#se obtienen la lista de los roles a desplegar en la lista
		roles = rol_util.get_roles_by_proyectos(fase.proyecto)
		#Instancia el filler, se le pasa como parametro el id la fase actual
		#para que este pueda ser utilizado en edit
		participantes_fase_filler = create_widget(ParticipantesModelDecorator,
										  LabelActionDecorator,
										  params={'__label__':'Asignar',
												  '__extra_url__':
													  "/edit?idfase=" + str(id)
												 }
										  )
		#se cargan los valores en el filler
		value = participantes_fase_filler.get_value(roles)

		self.params['modelname'] = 'Participantes'
		self.params['text_header'] = 'Lista de roles'

		return dict(value=value, params=self.params)

	def init_params(self, id):
		#para saber si mostrar o no el boton editar
		permiso_editar = fase_util.check_fase_permiso(id,
												'editar_fase')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = fase_util.check_fase_permiso(id,
											'administrar_participantes')
		usuarios = usuario_util.get_usuarios_by_fase(id)

		fase = fase_util.get_current(id)

		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		self.params['fase'] = fase
		self.params['idfase'] = id
		self.params['usuarios'] = usuarios

		return fase

	@expose('sap.templates.fase')
	@require(predicates.has_permission('administrar_participantes'))
	def edit(self, id, idfase=0,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del Rol

		@type  idfase : Integer
		@param idfase : Identificador de la fase

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		fase = fase_util.get_current(idfase)

		has_permiso = session_util.\
					  authorize_fase('administrar_participantes', fase=fase)
		#Se verifica si el usuario posee permisos sobre la fase actual
		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+str(idfase),'error')
			redirect('/miproyecto/fase/participantes/error')
		"""
		Se construye el widget, se obtiene la lista de todos los usuarios que se
		encuentran relacionados con el proyecto al cual pertenece la fase
		y se anaden los combos por cada participante del proyecto.
		"""
		_usuarios = usuario_util.get_usuarios_by_permiso(fase.proyecto)
		NewFaseParticipanteFrom.fields = []
		#Se construye los combobox por cada usuario
		for usuario in _usuarios :
			NewFaseParticipanteFrom.fields.append(CheckBox(usuario.user_name))

		new_participante_form = NewFaseParticipanteFrom("new_participante_form",
								action = 'post')

		tmpl_context.widget = new_participante_form
		"""
		Se marcan como seleccionados todos los usuarios que ya se encuentran
		asociados a la fase
		"""
		usuarios = usuario_util.get_usuarios_by_fase(fase.id_fase)
		for usuario in usuarios :
			kw[usuario.user_name] = True

		self.init_params(fase.id_fase)
		#self.params['fase'] = fase
		#self.params['usuarios'] = usuarios
		self.params['modelname'] = 'Participantes'
		self.params['header_file'] = 'proyecto'
		return dict(value=kw, params=self.params)


	@expose()
	def post(self, id, args={}, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		ecargado de asociar a los usuarios con las fases y sus permisos.

		@type  id : Integer
		@param id : Identificador de la fase.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""
		fase = fase_util.get_current()
		_usuarios = usuario_util.get_usuarios_by_fase(fase.id_fase)
		for usuario in _usuarios:
			self.delete(fase.id_fase ,usuario.usuario_id, False)

		usuarios = []
		for key in kw:
			usuarios.append(key)

		list = DBSession.query(Usuario).\
				filter(Usuario.user_name.in_(usuarios)).all()
		for usuario in list:
			usuario_util.asociar_usuario_fase(usuario.usuario_id, fase.id_fase)

		redirect("/miproyecto/fase/get_all/" + str(fase.id_fase) )

	@expose()
	def delete(self, id_fase ,id, show=True, **kw):
		"""
		@type  id_fase : Integer
		@param id_fase : Identificador del Rol

		@type  id : Integer
		@param id : Identificador del usuario a desvincular.

		@type  show : Boolean
		@param show : Indica si se despelgara el mensaje al culminar la operacion.

		@type  kw : Hash
		@param kw : Keywords
		"""
		fase = fase_util.get_current()
		list = DBSession.query(UsuarioPermisoFase).\
				filter(UsuarioPermisoFase.usuario_id == id).\
				filter(UsuarioPermisoFase.fase_id == id_fase)

		for element in list :
			DBSession.delete(element)
		"""
		Si es false no muestra el mensaje de sobre la operacion, esto es debido
		que este metodo es reutilizado a la hora de eliminar a un usuario del
		proyecto
		"""
		if show :
			flash("El usuario '"+ str(id) +"' ha sido desvinculado de la fase.")
			redirect("/miproyecto/fase/get_all/"+ str(id_fase))



class ParticipanteProyectoController(RestController):
	""" Contorlador de los participantes de la fase"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	allow_only = authorize.has_permission('administrar_participantes' )
	"""
	Limita el acceso al controlador a aquellos que poseen el permiso de
	administrar participantes.
	"""

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
		has_permiso = session_util.\
				authorize_proyecto('administrar_participantes', id=idproyecto)

		if ( has_permiso == None) :
			flash("No posee permisos sobre la fase #"+str(idproyecto),'error')
			redirect('/miproyecto/participantes/error')

		#para saber si mostrar o no el boton editar
		permiso_editar = proyecto_util.check_proyecto_permiso(idproyecto,
												'editar_proyecto')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = proyecto_util.check_proyecto_permiso(idproyecto,
											'administrar_participantes')

		usuarios = usuario_util.get_usuarios_by_permiso(idproyecto)

		tmpl_context.widget = participantes_table

		roles = rol_util.get_roles_by_proyectos(idproyecto)

		value = participantes_filler.get_value(roles)

		proyecto = proyecto_util.get_current(idproyecto)

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

		proyecto = proyecto_util.get_current()
		usuarios = usuario_util.get_usuarios_by_permiso(proyecto.id_proyecto)

		self.params['modelname'] = 'Participantes'
		self.params['header_file'] = 'proyecto'
		return dict(value=value, params=self.params)

	@validate(rol_usuario_edit_form, error_handler=edit)
	@expose()
	@require(predicates.has_permission('administrar_participantes'))
	def put(self, id, **kw):
		rol = DBSession.query(Rol).get(int(kw['rol_id']))

		proyecto = proyecto_util.get_current()

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


