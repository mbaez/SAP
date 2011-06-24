# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
# imports del modelo
from sap.model import *
from tg import tmpl_context, redirect, validate
#impot del checker de permisos
from sap.controllers.checker import *
#import del controlador
from tg.controllers import RestController

from sap.controllers.util import *

import transaction

header_file = "administracion"
new_url = "/administracion/proyecto/new"

class ProyectoController(RestController):
	"""
	Encargado de cargar el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'', 'label': '', 'cancelar_url':''}
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_proyecto'))
	def new(self, args={},**kw):
		"""
		Encargado de cargar el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""
		tmpl_context.widget = new_proyecto_form
		self.params['title'] = 'Nuevo Proyecto'
		self.params['modelname'] = 'Proyecto'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'crear_proyecto'
		self.params['cancelar_url'] = '/administracion/proyecto'
		return dict(value=kw, params=self.params)


	@validate(new_proyecto_form, error_handler=new)
	@require(predicates.has_permission('crear_proyecto'))
	@expose()
	def post(self,**kw):
		"""
		Evento invocado luego de un evento post en el form de crear
		ecargado de persistir las nuevas instancias.

		@type  kw : Hash
		@param kw : Keywords
		"""

		del kw['sprox_id']
		kw['lider'] = DBSession.query(Usuario).get(kw['lider'])
		kw['estado'] = estado_proyecto_util.get_by_codigo('Inicial')
		proyecto = Proyecto(**kw)
		#persiste el proyecto
		DBSession.add(proyecto)
		#Se anhade el rol de lider
		proy=DBSession.query(Proyecto).filter(Proyecto.nombre==proyecto.nombre).first()

		util.asignar_lider(proy)

		flash("El proyecto ha sido creado correctamente.")
		redirect("/administracion/proyecto/")


	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_proyecto'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del Proyecto.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		proyecto =  DBSession.query(Proyecto).get(id)
		tmpl_context.widget = proyecto_edit_form

		kw['id_proyecto'] = proyecto.id_proyecto
		kw['nombre'] = proyecto.nombre
		kw['lider'] = proyecto.lider
		kw['lider_id'] = proyecto.lider_id
		kw['estado_id'] = proyecto.estado_id
		kw['nro_fases'] = proyecto.nro_fases
		kw['descripcion'] = proyecto.descripcion
		self.params['modelname'] = 'Proyecto'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'editar_proyecto'
		return dict(value=kw, params=self.params)


	@validate(proyecto_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_proyecto'))
	@expose()
	def put(self, args={}, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		ecargado de persistir las modificaciones de las instancias.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""
		#Se obtiene de la base de datos el proyecto modifcado
		proyecto = DBSession.query(Proyecto).get(int(kw['id_proyecto']))
		#Se actualizan unicamente los campos actualizables
		proyecto.nombre=kw['nombre']
		proyecto.nro_fases = kw['nro_fases']
		proyecto.descripcion = kw['descripcion']

		#asignar lider
		proyecto.lider = DBSession.query(Usuario).get(kw['lider'])
		util.asignar_lider(proyecto)

		DBSession.merge(proyecto)
		flash("El proyecto ha sido '" +proyecto.nombre+ "' modificado correctamente.")
		redirect("/administracion/proyecto/list")

	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente
	los usuarios que posena el permiso de ver, este widget se encuentra
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('ver_proyecto'))
	def list(self, **kw):
		tmpl_context.widget = proyecto_table
		'''
		se obtiene la lista de los proyectos en los cuales pose el
		permiso de ver_proyecto
		'''
		proyectos = checker.get_poyect_list('ver_proyecto')
		value = proyecto_filler.get_value(proyectos)

		self.params['title'] = 'Editar Proyecto'
		self.params['modelname'] = 'Proyectos'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/administracion/proyecto/new'
		self.params['permiso'] = 'ver_proyecto'
		self.params['label'] = 'Nuevo Proyeco'
		return dict(value=value, params=self.params)

	"""
	metodo para listar todos los proyectos al administrador
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('admin_proyecto'))
	def get_all(self, **kw):
		tmpl_context.widget = proyecto_table
		#se obtiene la lista de todos los proyectos
		value = proyecto_filler.get_value()
		self.params['title'] = 'Editar Proyecto'
		self.params['modelname'] = 'Proyectos'
		self.params['header_file'] = 'administracion'
		self.params['new_url'] = '/administracion/proyecto/new'
		self.params['permiso'] = 'ver_proyecto'
		self.params['label'] = 'Nuevo Proyecto'
		return dict(value=value, params=self.params)


	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_proyecto, **kw):
		DBSession.delete(DBSession.query(RolPermisoProyecto).\
				  filter(RolPermisoProyecto.proyecto_id == id_proyecto))
		DBSession.delete(DBSession.query(Proyecto).get(id_proyecto))
		flash("El proyecto ha sido "+ id_proyecto +" eliminado correctamente.")
		redirect("/administracion/proyecto/")
