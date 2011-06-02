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

class LineaBaseController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':''}

	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('generar_lineabase'))
	def new(self, idfase, _method, **kw):
		tmpl_context.widget = new_linea_base_form
		self.params['title'] = 'Nueva Linea Base'
		self.params['modelname'] = 'LineaBase'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'generar_lineabase'
		kw['id_fase'] = idfase
		return dict(value=kw, params = self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_linea_base_form, error_handler=new)
	@require(predicates.has_permission('generar_lineabase'))
	@expose()
	def post(self, idfase, _method, **kw):
		del kw['sprox_id']
		linea_base = LineaBase(**kw)
		DBSession.add(linea_base)
		linea = DBSession.query(LineaBase).\
							filter(LineaBase.codigo==linea_base.codigo).\
							first()
		redirect("/miproyecto/fase/linea_base/generarLineaBase/"+
								str(idfase)+'/'+str(linea.id_linea_base))

	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	#@require(predicates.has_permission('editar_fase'))
	def edit(self, id,**kw):
		linea_base =  DBSession.query(LineaBase).get(id)
		tmpl_context.widget = linea_base_edit_form
		kw['id_linea_base'] = linea_base.id_linea_base
		kw['fase'] = linea_base.fase
		kw['estado'] = linea_base.estado
		return dict(value=kw, modelname='LineaBase')

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(linea_base_edit_form, error_handler=edit)
	#@require(predicates.has_permission('editar_fase'))
	@expose()
	def put(self, _method, **kw):
		del kw['sprox_id']
		linea_base = LineaBase(**kw)
		DBSession.merge(linea_base)
		flash("La LB ha sido modificado correctamente.")
		redirect("/miproyecto/fase/linea_base/generarLineaBase/" + str(idfase))

	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente
	los usuarios que posena el permiso de ver, este widget se encuentra
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, idfase, **kw):
		"""
		Lista todas lineas base de esta fase
		"""
		tmpl_context.widget = linea_base_table
		lineas = DBSession.query(LineaBase).filter(LineaBase.fase==idfase).all()
		value = linea_base_filler.get_value(lineas)
		header_file = "abstract"
		self.params['title'] = 'Lineas Base de esta fase'
		self.params['modelname'] = 'Linea Base'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'generar_lineabase'
		self.params['new_url'] = "/miproyecto/fase/linea_base/"+ str(idfase)+"/new/"
		return dict(value=value, params = self.params)

	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_linea_base, **kw):
		lb = DBSession.query(LineaBase).get(id_linea_base)
		#guardar el id de la fase de la linea base para el redirect
		idfase = lb.fase
		#borrar la linea base
		DBSession.delete(lb)
		flash("La linea base ha sido eliminada correctamente.")
		redirect("/miproyecto/fase/linea_base/list/"+str(idfase))

	@expose('sap.templates.list')
	#@require( predicates.has_permission('ver_proyecto'))
	def ver(self, idfase, id_linea_base, **kw):
		tmpl_context.widget = item_table
		# Se obtienen los items de que pertenecen a la linea base de la
		# fase actual.
		items = DBSession.query(Item).filter(Item.id_item == LineaBaseItem.id_item).\
									filter(Item.fase == idfase).\
									filter(LineaBaseItem.id_linea_base == id_linea_base).all()
		
		value = item_filler.get_value(items)
		header_file = "abstract"
		new_url = "/miproyecto/fase/linea_base/" + str(idfase) + "/new"
		return dict(modelname='LineaBases', header_file=header_file, new_url=new_url, value=value)

	@expose('sap.templates.list')
	def generarLineaBase(self, idfase, idtipo, **kw):
		tmpl_context.widget = item_table
		items = util.get_aprobados_sin_lineas(idfase)

		self.params['title'] = 'Agregar Items a esta linea Base'
		self.params['modelname'] = 'Items aprobados'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'NO MOSTRAR BOTON NUEVO'
		self.params['new_url'] = ""
		value= item_filler.get_value(items)
		"""
		aux=[]
		for item in items:
			aux=[{'nombre': item.nombre, 'estado_actual': item.estado_actual,
			'accion': '<div><a href="/miproyecto/fase/linea_base/agregarItem/'
			+str(item.id_item)+'/'+str(idtipo)+'">Agregar Item a linea Base</a></div>'}]
			value=value+aux
		"""
		return dict(value = value, params = self.params)
