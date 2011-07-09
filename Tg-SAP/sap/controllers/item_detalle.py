# -*- coding: utf-8 -*-

from tg import expose, flash, require, redirect,response
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
from tw.forms import *
# imports del modelo
from sap.model import *
from tg import tmpl_context, redirect, validate
#import del checker de permisos
from sap.controllers.checker import *
from sap.controllers.item import *
#import del controlador
from tg.controllers import RestController

from sap.controllers.util import *
_widget = None


class ItemDetalleController(RestController):
	"""Controlador del detalle del item"""

	params = {'title':'', 'header_file':'', 'modelname':'', 'new_url':'',
			  'idfase':'', 'permiso':'', 'cancelar_url':'' , 'valor': ' ',
			  'observacion': '', 'id_item_detalle': ' '  }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.edit_atributo')
	@require(predicates.has_permission('editar_item'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del Detalle del item.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""
		kw['id_item_detalle'] = id
		
		detalle = DBSession.query(DetalleItem).get(id)

		tmpl_context.widget = detalle_item_edit_form

		value = detalle_item_edit_filler.get_value(kw)
		
		self.params['id_item_detalle'] = id
		self.params['valor'] = detalle.valor
		
		self.params['tipo_atributo'] = int(detalle.atributo_tipo_item.tipo_id)
		self.params['observacion'] = detalle.observacion
		
		self.params['modelname'] = 'Atributo de Item'
		self.params['header_file'] = 'abstract'
		return dict(value=value, params=self.params)

	@validate(detalle_item_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_item'))
	@expose()
	def put(self, id, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		encargado de persistir las modificaciones de las instancias.

		@type  id : Integer
		@param id : Identificador del Detalle del item.

		@type  kw : Hash
		@param kw : Keywords

		"""
		detalle =  DBSession.query(DetalleItem).get(id)
		detalle.valor = kw['valor']
		detalle.observacion = kw ['observacion']

		DBSession.merge(detalle)
		DBSession.flush()

		item = DBSession.query(Item).get(detalle.id_item)

		item_util.audit_item(item)
		item.version += 1
		DBSession.merge(item)

		flash("El item atributo ha sido modificado correctamente.")
		redirect('/miproyecto/fase/item/poner_en_revision/'+str(detalle.id_item))
