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

import transaction

header_file = "administracion"
new_url = "/administracion/proyecto/new"

class ProyectoController(RestController):
	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':''}
	
	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_proyecto'))
	def new(self, modelname='',**kw):
		tmpl_context.widget = new_proyecto_form
		self.params['title'] = 'Nuevo Proyecto'
		self.params['modelname'] = 'Proyecto'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'crear_proyecto'
		self.params['modelname'] = 'Proyecto'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'crear_proyecto'
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_proyecto_form, error_handler=new)
	@require(predicates.has_permission('crear_proyecto'))
	@expose()
	def post(self,**kw):
		del kw['sprox_id']
		kw['lider'] = DBSession.query(Usuario).get(kw['lider'])
		kw['estado'] = DBSession.query(EstadoProyecto).get(kw['estado'])
		proyecto = Proyecto(**kw)
		#persiste el proyecto
		DBSession.add(proyecto)
		#Se anhade el rol de lider
		proy=DBSession.query(Proyecto).filter(Proyecto.nombre==proyecto.nombre).first()

		util.asignar_lider(proy)

		flash("El proyecto ha sido creado correctamente.")
		redirect("/administracion/proyecto/list")

	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_proyecto'))
	def edit(self, id,**kw):
		proyecto =  DBSession.query(Proyecto).get(id)
		tmpl_context.widget = proyecto_edit_form
		kw['id_proyecto'] = proyecto.id_proyecto
		kw['nombre'] = proyecto.nombre
		kw['lider'] = proyecto.lider
		kw['estado'] = DBSession.query(EstadoProyecto).all()
		kw['lider_id'] = proyecto.lider_id
		kw['estado_id'] = proyecto.estado_id
		kw['nro_fases'] = proyecto.nro_fases
		kw['descripcion'] = proyecto.descripcion
		self.params['modelname'] = 'Proyecto'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'editar_proyecto'
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de editar
	ecargado de persistir las modificaciones de las instancias.
	"""
	@validate(proyecto_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_proyecto'))
	@expose()
	def put(self, _method, **kw):
		#Se obtiene de la base de datos el proyecto modifcado
		proyecto = DBSession.query(Proyecto).get(int(kw['id_proyecto']))
		#Se actualizan unicamente los campos actualizables
		proyecto.nombre=kw['nombre']
		proyecto.nro_fases = kw['nro_fases']
		proyecto.descripcion = kw['descripcion']
		proyecto.estado=DBSession.query(EstadoProyecto).get(int(kw['estado']))
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
		return dict(value=value, params=self.params)

	"""
	metodo para listar todos los proyectos al administrador
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('ver_proyecto'))
	def get_all(self, **kw):
		tmpl_context.widget = proyecto_table
		#se obtiene la lista de todos los proyectos
		value = proyecto_filler.get_value()
		self.params['title'] = 'Editar Proyecto'
		self.params['modelname'] = 'Proyectos'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/administracion/proyecto/new'
		self.params['permiso'] = 'ver_proyecto'
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
