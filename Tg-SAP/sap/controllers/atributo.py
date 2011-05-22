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
#import del checker de permisos
from sap.controllers.checker import *
#import del controlador
from tg.controllers import RestController

class AtributoController(RestController):
	
	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new(self, idtipo, modelname, **kw):
		tmpl_context.widget = new_atributo_form
		header_file='tipo_item'
		return dict(value=kw, modelname= "Atributos del Tipo de Item", idtipo=idtipo,
										header_file=header_file)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_atributo_form, error_handler=new)
	@require(predicates.has_permission('manage'))
	@expose()
	def post(self, idtipo, **kw):
		del kw['sprox_id']
		atributo_tipo_item = AtributoTipoItem()
		atributo_tipo_item.tipo_item = idtipo
		atributo_tipo_item.nombre = kw['nombre']
		atributo_tipo_item.tipo_id = kw['tipo']
		DBSession.add(atributo_tipo_item)
		flash("El Atributo del tipo de Item ha sido creado correctamente")
		redirect('/miproyecto/fase/tipo_item/atributos/'+idtipo+'/new')


	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	#@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		tipo_item =  DBSession.query(TipoItem).get(id)
		tmpl_context.widget = tipo_item_edit_form
		kw['id_tipo_item'] = tipo_item.id_tipo_item
		kw['fase'] = tipo_item.fase
		kw['nombre'] = tipo_item.nombre
		kw['descripcion'] = tipo_item.descripcion
		header_file="tipo_item"
		return dict(value=kw, modelname='TipoItem', header_file=header_file)

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(tipo_item_edit_form, error_handler=edit)
	#@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		tipo_item = TipoItem(**kw)
		DBSession.merge(tipo_item)
		flash("El tipo de item ha sido modificado correctamente.")
		redirect('/miproyecto/fase/tipo_item/list/'+str(tipo_item.fase))

	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente
	los usuarios que posena el permiso de ver, este widget se encuentra
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, idtipo, **kw):
		'''
		Lista todos tipos de items de la bd.
		Se debe modificar para que liste solo los
		de la fase actual
		'''
		tmpl_context.widget = atributo_table
		atributos = DBSession.query(AtributoTipoItem).filter(AtributoTipoItem.tipo_item==idtipo).all()
		value = atributo_filler.get_value(atributos)
		header_file = "tipo_item"
		new_url = "/miproyecto/fase/tipo_item/atributos/"+idtipo+"/new"
		return dict(modelname='Atributos',value=value, header_file=header_file,
												new_url=new_url,idtipo=idtipo)
		
	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_tipo_item, **kw):
		DBSession.delete(DBSession.query(TipoItem).get(id_tipo_item))
		flash("El tipo de item "+ id_tipo_item + "ha sido eliminado correctamente.")
		redirect('/miproyecto/fase/tipo_item/list/'+id_tipo_item)