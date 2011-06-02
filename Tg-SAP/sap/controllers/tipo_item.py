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
from sap.controllers.atributo import AtributoController
#import del controlador
from tg.controllers import RestController

class TipoItemController(RestController):
	
	atributos = AtributoController()
	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':''}
	"""
	Encargado de carga el widget para crear nuevas instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_tipo_item'))
	def new(self, idfase, modelname, **kw):
		tmpl_context.widget = new_tipo_item_form
		self.params['modelname'] = "Tipo de Item"
		self.params['header_file'] = 'tipo_item'
		self.params['idfase'] = idfase
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_tipo_item_form, error_handler=new)
	@require(predicates.has_permission('crear_tipo_item'))
	@expose()
	def post(self, idfase, **kw):
		del kw['sprox_id']
		tipo_item = TipoItem(**kw)
		tipo_item.fase = idfase
		DBSession.add(tipo_item)
		flash("El tipo de Item ha sido creado correctamente")
		#traer el ultimo tipo insertado para pasarle su id al formulario de atributos
		tipo = DBSession.query(TipoItem).\
							filter(TipoItem.nombre==tipo_item.nombre).\
							filter(TipoItem.descripcion==tipo_item.descripcion).\
							first()
		redirect('/miproyecto/fase/tipo_item/atributos/'+tipo.id_tipo_item+'/new')
	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_tipo_item'))
	def edit(self, id,**kw):
		tipo_item =  DBSession.query(TipoItem).get(id)
		tmpl_context.widget = tipo_item_edit_form
		kw['id_tipo_item'] = tipo_item.id_tipo_item
		kw['fase'] = tipo_item.fase
		kw['nombre'] = tipo_item.nombre
		kw['descripcion'] = tipo_item.descripcion
		self.params['modelname'] = "Tipo de Item"
		self.params['header_file'] = 'tipo_item'
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
	@require( predicates.has_permission('editar_tipo_item'))
	def list(self, idfase, **kw):
		'''
		Lista todos tipos de items de la bd.
		Se debe modificar para que liste solo los
		de la fase actual
		'''
		tmpl_context.widget = tipo_item_table
		tipo_items = DBSession.query(TipoItem).filter(TipoItem.fase==idfase).all()
		value = tipo_item_filler.get_value(tipo_items)
		new_url = "/miproyecto/fase/tipo_item/"+idfase+"/new"
		self.params['modelname'] = "Tipos de Items"
		self.params['header_file'] = 'tipo_item'
		self.params['new_url'] = "/miproyecto/fase/tipo_item/"+idfase+"/new"
		self.params['idfase'] = idfase
		self.params['permiso'] = 'crear_tipo_item'
		return dict(value=value, params=self.params)

	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_tipo_item, **kw):
		DBSession.delete(DBSession.query(TipoItem).get(id_tipo_item))
		flash("El tipo de item "+ id_tipo_item + "ha sido eliminado correctamente.")
		redirect('/miproyecto/fase/tipo_item/list/'+id_tipo_item)

	"""
	importar items
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('editar_tipo_item'))
	def importar(self, idfase, **kw):
		"""
		Recuperar de la BD todas a las fases del proyecto actual  
		"""
		fase = DBSession.query(Fase).get(idfase)
		fases = DBSession.query(Fase).filter(Fase.proyecto!=fase.proyecto).\
										all()
		
		"""
		Copiar los ids de las fases a una lista
		"""
		fases_id = []
		for fase in fases: 
			fases_id.append(fase.id_fase)
		
		"""
		Se obtinene de la BD todos aquellos items que no sean de ninguna 
		de las fases de este proyecto
		""" 
		tmpl_context.widget = tipo_item_table
		tipo_items = DBSession.query(TipoItem).\
								filter(TipoItem.fase.in_(fases_id)).all()
		"""
		El value para la tabla son los items de las otras fases
		con un action que redirija "importarEsteItem"
		"""
		value=[]
		aux=[]
		for tipo in tipo_items:
			aux=[{'nombre': tipo.nombre, 'descripcion': tipo.descripcion,
			'accion': '<div><a href="/miproyecto/fase/tipo_item/importar_este_tipo/'
			+str(tipo.id_tipo_item)+'/'+idfase+'">Importar este Item</a></div>'}]
			value=value+aux
			
		self.params['header_file'] = "tipo_item"
		self.params['new_url'] = '/'
		self.params['idfase'] = idfase
		self.params['modelname'] = "Tipos de Items de Otros Proyectos" 
		self.params['permiso'] = 'NO SE MUESTRA EL BOTON NUEVO'
		return dict(value=value, params=self.params)
	
	@require( predicates.has_permission('editar_tipo_item'))
	@expose()
	def importar_este_tipo(self, idtipo, idfase):
		"""
		Se obtiene de la BD el tipo de item y sus atributos
		"""
		tipo = DBSession.query(TipoItem).get(idtipo)
		atributos = DBSession.query(AtributoTipoItem).\
						filter(AtributoTipoItem.tipo_item==tipo.id_tipo_item)
		"""
		Se settean los valores de la copia
		El nuevo tipo de item (copia_tipo )pertenecera a esta fase ahora
		"""
		copia_tipo = TipoItem()
		copia_tipo.nombre = tipo.nombre
		copia_tipo.descripcion = tipo.descripcion
		copia_tipo.fase = idfase
		
		"""
		Se settean los valores para cada copia_atributo
		
		for atributo in atributos:
			copia_atributo = AtributoTipoItem()
			copia_atributo.nombre = atributo.nombre
			copia_atributo.tipo_id = atributo.tipo_id
			copia_tipo.atributos.append(copia_atributo)
		"""
		DBSession.add(copia_tipo)
		flash("El tipo de item "+str(tipo.nombre)+
										" pertenece ahora a esta fase")
		redirect("/miproyecto/fase/tipo_item/importar/"+str(idfase))
