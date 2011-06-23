"""
27-05-11
cambiar los pasos de parametros a params[]
modifacion de metodos edit, delete, new, list
"""
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

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idtipo':'','permiso':'', 'label':'', 'cancelar_url': '', 'idfase':''}

	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.tipo_item')
	@require(predicates.has_permission('crear_tipo_item'))
	def new(self, idtipo, modelname, **kw):
		tmpl_context.widget = new_atributo_form
		self.params['modelname'] = "Atributos del Tipo de Item"
		self.params['idtipo'] = idtipo
		self.params['tipo_item'] = DBSession.query(TipoItem).get(idtipo)
		self.params['current_name'] = self.params['tipo_item'].nombre
		id_fase = self.params['tipo_item'].fase
		self.params['fase'] = DBSession.query(Fase).get(id_fase)
		self.params['idfase'] = id_fase
		self.params['header_file'] = 'tipo_item'
		self.params['cancelar_url'] = '/miproyecto/fase/tipo_item/atributos/list/'+str(idtipo)
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_atributo_form, error_handler=new)
	@require(predicates.has_permission('crear_tipo_item'))
	@expose()
	def post(self, idtipo,params={}, **kw):
		del kw['sprox_id']
		atributo_tipo_item = AtributoTipoItem()
		atributo_tipo_item.tipo_item = idtipo
		atributo_tipo_item.nombre = kw['nombre']
		atributo_tipo_item.tipo_id = kw['tipo']
		DBSession.add(atributo_tipo_item)

		items = DBSession.query(Item).filter(Item.tipo_item==idtipo)

		for item in items :
			detalle = DetalleItem()
			detalle.nombre = atributo_tipo_item.nombre
			detalle.id_atributo_tipo_item = atributo_tipo_item.id_atributo_tipo_item
			detalle.valor = None
			detalle.recurso = None
			item.detalles.append(detalle)
			DBSession.merge(item)
		DBSession.flush()

		flash("El Atributo del tipo de Item ha sido creado correctamente")
		redirect('/miproyecto/fase/tipo_item/atributos/'+idtipo+'/new')


	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_tipo_item'))
	def edit(self, id,**kw):
		atributo_tipo_item = DBSession.query(AtributoTipoItem).get(id)
		tmpl_context.widget = tipo_item_edit_form
		kw['nombre'] = atributo_tipo_item.nombre
		kw['tipo'] = atributo_tipo_item.tipo
		self.params['header_file'] = "tipo_item"
		self.params['modelname'] = "Tipo de Item"
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(tipo_item_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_tipo_item'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		atributo = AtributoTipoItem(**kw)
		DBSession.merge(atributo)
		tipo_item = DBSession.query(TipoItem).get(atributo.id_tipo_item)
		flash("El tipo de item ha sido modificado correctamente.")
		redirect('/miproyecto/fase/tipo_item/list/'+str(tipo_item.fase))

	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente
	los usuarios que posena el permiso de ver, este widget se encuentra
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('editar_tipo_item'))
	def list(self, idtipo, **kw):
		tmpl_context.widget = atributo_table
		atributos = DBSession.query(AtributoTipoItem).\
							filter(AtributoTipoItem.tipo_item==idtipo).\
							all()
		value = atributo_filler.get_value(atributos)
		self.params['label'] = 'Agregar Atributo'
		self.params['header_file'] = "tipo_item"
		self.params['modelname'] = "Atributos"
		self.params['permiso'] = "crear_tipo_item"
		self.params['new_url'] = "/miproyecto/fase/tipo_item/atributos/"+idtipo+"/new"
		return dict(value=value, params=self.params)

	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id, **kw):
		atributo = DBSession.query(AtributoTipoItem).get(id)
		id_tipo_item = atributo.id_tipo_item
		DBSession.delete(atributo)
		flash("El atributo "+ id + "ha sido eliminado correctamente.")
		redirect('/miproyecto/fase/tipo_item/atributos/list/'+id_tipo_item)
