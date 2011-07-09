# -*- coding: utf-8 -*-

from tg import expose, flash, require, redirect,response
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
#import de widgets
from sap.widgets.editform import *
from tw.forms import *
# imports del modelo
from sap.model import *
from tg import tmpl_context, redirect, validate
#import del controlador
from tg.controllers import RestController

from sap.controllers.util import *

class ArchivoController(RestController):
	"""Controlador del detalle del item"""

	params = {'title':'', 'header_file':'', 'modelname':'', 'new_url':'',
			  'idfase':'', 'permiso':'', 'cancelar_url':''
			 }

	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_item'))
	def edit(self, id,**kw):
		"""
		Encargado de cargar el widget para editar las instancias,solo tienen
		acceso aquellos usuarios que posean el premiso de editar

		@type  id : Integer
		@param id : Identificador del item.

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		kw ['id_item'] = id
		tmpl_context.widget = arhivo_edit_form

		value = kw

		self.params['modelname'] = 'Adjunto del item'
		self.params['header_file'] = 'abstract'

		return dict(value=value, params=self.params)

	@require(predicates.has_permission('editar_item'))
	@expose()
	def put(self, id, **kw):
		"""
		Evento invocado luego de un evento post en el form de editar
		encargado de persistir las modificaciones de las instancias.

		@type  id : Integer
		@param id : Identificador del item.

		@type  kw : Hash
		@param kw : Keywords

		"""
		archivo =  Archivo()
		archivo.id_item = int(kw['id_item'])

		if kw ['archivo'] != None:
			stream = True
			archivo.archivo = ""

			while stream :
				stream = kw ['archivo'].file.read(1024)
				archivo.archivo += stream

			archivo.file_name = kw ['archivo'].filename
			archivo.content_type = kw ['archivo'].type
			kw ['archivo'].file.close()


		DBSession.add(archivo)

		item = DBSession.query(Item).get(int(kw['id_item']))

		item_util.audit_item(item)
		item.version += 1
		DBSession.merge(item)

		flash("El item atributo ha sido modificado correctamente.")
		redirect('/miproyecto/fase/item/poner_en_revision/'+str(archivo.id_item))

	@expose()
	def descargar(self, id, **kw):
		"""
		Encargado de descargar los archivos adjuntos del detalle del tipo
		de item.

		@type  id : Integer
		@param id : Identificador del Detalle del item.

		@type  kw : Hash
		@param kw : Keywords

		"""
		archivo =  DBSession.query(Archivo).get(id)
		response.headers["Content-disposition"] = "attachment; filename="+archivo.file_name
		response.headers["Content-Type"] = archivo.content_type
		response.write(archivo.archivo)

		return response

	@expose()
	def eliminar(self, id, **kw):
		archivo = DBSession.query(Archivo).get(id)
		item_util.audit_item(archivo.item)
		archivo.item.version += 1
		DBSession.merge(archivo.item)
		id_item = archivo.id_item

		DBSession.delete(archivo)

		flash("El archivo ha sido eliminado correctamente.")
		redirect('/miproyecto/fase/item/poner_en_revision/'+str(id_item))
