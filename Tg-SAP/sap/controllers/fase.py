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

class FaseController(RestController):

	"""
	Encargado de carga el widget para crear nuevas instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_fase'))
	def new(self, idproyecto, modelname, **kw):
		tmpl_context.widget = new_fase_form
		return dict(value=kw, modelname= "Fase")
	
	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_fase_form, error_handler=new)
	@require(predicates.has_permission('manage'))
	@expose()
	def post(self, idproyecto, **kw):
		del kw['sprox_id']
		fase = Fase(**kw)
		fase.proyecto = idproyecto
		DBSession.add(fase)
		redirect("/miproyecto/ver/"+idproyecto)
	
	"""
	Encargado de carga el widget para editar las instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	#@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		fase =  DBSession.query(Fase).get(id)
		tmpl_context.widget = fase_edit_form
		kw['id_fase'] = fase.id_fase
		kw['nombre'] = fase.nombre
		kw['descripcion'] = fase.descripcion
		return dict(value=kw, modelname='Fase')

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(fase_edit_form, error_handler=edit)
	#@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		fase = Fase(**kw)
		DBSession.merge(fase)
		flash("La fase '" + fase.nombre+ "'ha sido modificado correctamente.")
		redirect("/miproyecto/fase/list")
	
	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente 
	los usuarios que posena el permiso de ver, este widget se encuentra 
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, **kw):
		"""
		tmpl_context.widget = proyecto_table
		
		se obtiene la lista de los proyectos en los cuales pose el
		permiso de ver_proyecto
		
		proyectos = checker.get_poyect_list('ver_proyecto')
		value = proyecto_filler.get_value(proyectos)
		"""
		return dict(modelname='Fases')
		
	"""	
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_fase, **kw):
		DBSession.delete(DBSession.query(Fase).get(id_fase))
		flash("La fase "+ id_proyecto + "ha sido eliminada correctamente.")
		redirect("/miproyecto/fase/list")

		
	
		