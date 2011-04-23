# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""
Import the usuario widget
"""
from tg import tmpl_context
from sap.widgets.createform import *

from sap.model import *
from tg import tmpl_context, redirect, validate

class ProyectoController(BaseController):
	"""
	prueba de abm y de visibilidad de datos en el template master.html
	anhadi py:if="tg.predicates.has_permission('manage')" para que solo
	muestre el link a los usuarios que posean el permiso 'manage'
	ademas los metodos de new_usuario, create_usuario y list_usuario estan
	anotados con @require(predicates.has_permission('manage')) esto es para que 
	no se pueda acceder a al formulario atravez de la url.
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def new (self, **kw):
		"""
		Despliega en pantalla el widget ProyectoForm que se encuentra
		en la carpeta widget
		"""
		tmpl_context.form = create_proyecto_form
		
		return dict(modelname='Proyecto',
			genre_options=DBSession.query(Proyecto.id_proyecto),
			page='Nuevo Proyecto')


	@validate(create_proyecto_form, error_handler=new)
	@expose('sap.templates.new')
	@require(predicates.has_permission('manage'))
	def create(self, **kw):
		"""
		El formulario envia los argumentos del formulario 
		a este metodo en la variable kw y estos seteados a una variable
		del tipo Proyecto.
		"""
		proyecto = Proyecto()
		proyecto.nombre = kw['nombre']
		proyecto.lider_id = kw['lider_id']
		proyecto.estado = kw['estado']
		proyecto.nro_fases = kw['nro_fases']
		proyecto.descripcion = kw['descripcion']
		#guarda el usuario registrado en el formulario
		DBSession.add(proyecto)
		#emite un mensaje y redirecciona a la pagina de listado
		flash("El Proyecto ha sido creado correctamente.")
		redirect("list")
		

	@expose('sap.templates.list')
	@require(predicates.has_permission('manage'))
	def list(self, **kw):
		"""Lista todos los proyectos de la base de datos"""
		list = DBSession.query(Proyecto)
		items = [] 
		head = []
		'''
		Se anhade el nombre de las columnas
		'''
		head.append(['ID', 'Nombre'] )
					
		'''
		Se formatea la entidad como una matriz para ser visualizada en la tabla
		'''
		for item in list:
			items.append([item.id_proyecto, item.nombre])
		
		return dict(array=items, headers=head, modelname='proyecto',
					page='Lista de Proyectos')
