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
from tw.forms import TableForm, SingleSelectField, TextField, TextArea, PasswordField, SubmitButton, Spacer, CheckBox
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

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'', 'cancelar_url':''}

	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_item'))
	def edit(self, id,**kw):
		kw['id_item_detalle'] = id

		tmpl_context.widget = detalle_item_edit_form

		value = detalle_item_edit_filler.get_value(kw)

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
		"""
		detalle =  DBSession.query(DetalleItem).get(id)
		detalle.valor = kw['valor']
		if kw ['adjunto'] != None:
			detalle.adjunto = kw ['adjunto'].file.read()
		detalle.observacion = kw ['observacion']

		DBSession.merge(detalle)
		DBSession.flush()
		item = DBSession.query(Item).get(detalle.id_item)
		item_util.audit_item(item)

		flash("El item atributo ha sido modificado correctamente.")
		redirect('/miproyecto/fase/item/poner_en_revision/'+str(detalle.id_item))
