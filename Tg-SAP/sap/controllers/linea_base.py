# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect, response
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


#from reportlab.pdfgen import canvas
#from geraldo.generators import PDFGenerator
#from reporte import *

_widget = None

class LineaBaseController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'', 'cancelar_url':''}

	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('generar_lineabase'))
	def new(self, idfase, _method, **kw):
		NewLineaBaseForm.fields = []

		items = item_util.get_items_aprobados(idfase)
		if items == []:
			flash('No hay items aprobados en esta fase')
			redirect("/miproyecto/fase/linea_base/list/"+str(idfase))
			return
		for i in items:
			NewLineaBaseForm.fields.append( CheckBox(i.codigo.replace('-', '_')) )

		new_linea_base_form = NewLineaBaseForm("new_linea_base_form", action = 'post')
		tmpl_context.widget = new_linea_base_form

		self.params['title'] = 'Nueva Linea Base'
		self.params['modelname'] = 'LineaBase'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'generar_lineabase'
		self.params['cancelar_url'] = '/miproyecto/fase/linea_base/list/' + str(idfase)
		kw['id_fase'] = idfase
		return dict(value=kw, params = self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	#@validate(_widget, error_handler=new)
	@require(predicates.has_permission('generar_lineabase'))
	@expose()
	def post(self, idfase, _method, **kw):
		#del kw['sprox_id']
		#linea_base = LineaBase(**kw)
		lista_codigos = []
		dic = kw
		for d in dic:
			print 'dddddd = '+ d
			lista_codigos.append(d.replace('_', '-'))

		lista_items = DBSession.query(Item).filter( Item.codigo.in_(lista_codigos) ).\
											all()

		linea_base = LineaBase()
		linea_base.codigo = util.gen_codigo('linea_base')
		linea_base.estado = estado_linea_base_util.get_by_codigo('Cerrada')
		linea_base.fase = idfase

		for i in lista_items:
			linea_base.items.append(i)

		DBSession.add(linea_base)

		redirect("/miproyecto/fase/linea_base/list/"+str(idfase))

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
		kw['codigo'] = linea_base.codigo
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
	@expose('sap.templates.fase')
	#@require( predicates.has_permission('ver_proyecto'))
	def list(self, idfase, **kw):
		"""
		Lista todas lineas base de esta fase
		"""
		tmpl_context.widget = linea_base_table
		lineas = DBSession.query(LineaBase).filter(LineaBase.fase==idfase).all()
		value = linea_base_filler.get_value(lineas)

		self.init_params(idfase)

		self.params['title'] = 'Lineas Base de esta fase'
		self.params['modelname'] = 'Linea Base'
		self.params['header_file'] = 'fase'
		self.params['permiso'] = 'generar_lineabase'
		self.params['new_url'] = "/miproyecto/fase/linea_base/"+ str(idfase)+"/new/"
		self.params['label'] = 'Nuevo'
		return dict(value=value, params = self.params)

	def init_params(self, id):
		#para saber si mostrar o no el boton editar
		permiso_editar = fase_util.check_fase_permiso(id,
												'editar_fase')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = fase_util.check_fase_permiso(id,
											'administrar_participantes')
		usuarios = util.get_usuarios_by_fase(id)

		fase = fase_util.get_current(id)
		roles = util.get_roles_by_proyectos(fase.proyecto)
		value = participantes_fase_filler.get_value(roles)

		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		self.params['fase'] = fase
		self.params['idfase'] = id
		self.params['usuarios'] = usuarios

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
	def generarLineaBase(self, idfase, idlineabase, **kw):
		tmpl_context.widget = item_table
		items = util.get_aprobados_sin_lineas(idfase)

		self.params['title'] = 'Agregar Items a esta linea Base'
		self.params['modelname'] = 'Items aprobados'
		self.params['header_file'] = 'abstract'
		self.params['permiso'] = 'NO MOSTRAR BOTON NUEVO'
		self.params['new_url'] = ""
		value= item_filler.get_value(items)

		return dict(value = value, params = self.params)

	@expose()
	def abrir_linea_base(self, idlineabase, **kw):
		"""
		Metodo para abrir una linea base. Los de items de la linea base
		se marcan con estado de revision
		"""
		linea_base = DBSession.query(LineaBase).get(idlineabase)
		listaItems = DBSession.query(Item).\
								filter(Item.id_linea_base == idlineabase).all()
		if(listaItems==None):
			flash("La linea base no tiene items asociados")
			return

		for item in listaItems:
			item.estado = 3
			#item.id_linea_base = None
			DBSession.merge(item)
		self.params['idfase'] = linea_base.fase

		linea_base.estado = estado_linea_base_util.get_by_codigo('Abierta')
		DBSession.merge(linea_base)

		flash("La linea base ha sido abierta")
		redirect("/miproyecto/fase/linea_base/list/" + str(self.params['idfase']))

	@expose()
	def generar_reporte(self, **kW):
		"""
		Metodo para generar reporte de lineas base
		"""
		# Se setea el objeto response con el encabezado apropiado
		response.headers["Content-Type"] = "application/pdf"
		response.headers["Content-disposition"] = "attachment; filename=report.pdf"
		#res = HttpResponse(mimetype='application/pdf')
		#res['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

		# Se crea el objeto pdf utilizando el objeto response
		p = canvas.Canvas(response)

		# Se imprime un Hello world en el pdf utilizando la API de reportlab
		p.drawString(100, 100, "Hello world.")
		p.showPage()
		p.save()
		return response

	@expose()
	def reporte_linea_base(self, **kW):
		datos = [
			{'name': 'item001', 'age': 29, 'weight': 55.7, 'genre': 'female', 'status': 'parent'}
		]
		response.headers["Content-Type"] = "application/pdf"
		response.headers["Content-disposition"] = "attachment; filename=report.pdf"

		items = DBSession.query(Item).all()
		for item in items:
			item_params = {'name': item.codigo, 'age': item.complejidad, 'weight': 55.7, 'genre': 'female', 'status': 'parent'}
			datos.append(item_params)

		report = LineaBaseReport(queryset=datos)
		report.generate_by(PDFGenerator, filename=response)

		return response




