# -*- coding: utf-8 -*-
"""Main Controller"""


from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from tg.controllers import RestController

from sap.controllers.item import *

class RelacionController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'', 'label': '', 'cancelar_url': ''}

	@expose('sap.templates.fase')
	@require(predicates.has_permission('editar_item'))
	def new(self, idfase, modelname='', **kw):
		"""
		dentro del form un combo trae los items de la fase actual
		y el otro los items de la fase actual y la siguiente
		"""
		new_relacion_form.item_1.idfase=idfase
		new_relacion_form.item_2.idfase=idfase
		tmpl_context.widget = new_relacion_form
		self.params['header_file'] = "abstract"
		self.params['idfase'] = idfase
		self.params['modelname'] = "Relacion"
		self.params['permiso'] = 'editar_item'
		self.params['cancelar_url'] = '/miproyecto/fase/relacion/list/'+str(idfase)
		self.init_params(idfase)
		return dict(value=kw, params=self.params)
	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_relacion_form, error_handler=new)
	@expose()
	@require(predicates.has_permission('editar_item'))
	def post(self, idfase, modelname='',**kw):
		del kw['sprox_id']
		"""
		el item controller es para usar los metodos de esa clase
		"""
		item = ItemController()
		"""
		se crea la nueva relacion y se le asignan los valores de los combos
		"""
		relacion = RelacionItem()
		relacion.id_item_actual = kw['item_1']
		relacion.id_item_relacionado = kw['item_2']

		#VALIDACION: relacion consigo mismo
		if(relacion.id_item_actual==relacion.id_item_relacionado):
			flash("No se puede establecer una relacion consigo mismo", 'error')
			redirect('/miproyecto/fase/relacion/'+idfase+'/new/')
		#VALIDACION: si los items son o no de la misma fase
		item1=DBSession.query(Item).get(relacion.id_item_actual)
		item2=DBSession.query(Item).get(relacion.id_item_relacionado)

		#Validar que el item antecesor (item1) pertenezca a una linea base
		if(item1.id_linea_base == None):
			flash('El item antecesor no pertenece a ninguna linea base', 'error')
			redirect("/miproyecto/fase/relacion/list/"+idfase)
			return

		if(item1.fase==item2.fase):
			relacion.relacion_parentesco=1
			#VALIDACION: que no formen un ciclo en el caso de ser relacion dentro
			#de la misma fase
			ciclo=item.ciclo(item1.id_item, item2.id_item, idfase)
			if(ciclo!=[]):
				flash("La nueva relacion provoca un ciclo: " + str(ciclo))
				redirect('/miproyecto/fase/relacion/'+idfase+'/new/')
		else:
			relacion.relacion_parentesco=2

		DBSession.merge(relacion)
		flash("La relacion se ha creado correctamente")
		redirect("/miproyecto/fase/relacion/list/"+idfase)

	@expose()
	@require(predicates.has_permission('editar_item'))
	def borrarRelacion(self, item1, item2, idfase, **kw):
		DBSession.delete(DBSession.query(RelacionItem).\
					filter(RelacionItem.id_item_actual==item1).\
					filter(RelacionItem.id_item_relacionado==item2).\
					one())
		flash("Se ha eliminado la relacion: "+item1+" <--> "+item2)
		redirect("/miproyecto/fase/relacion/list/"+idfase)

	@expose('sap.templates.fase')
	@require(predicates.has_permission('editar_item'))
	def list(self, idfase, **kw):
		items = DBSession.query(Item).filter(Item.fase==idfase)
		items_id = []
		for item in items:
			items_id.append(item.id_item)

		relaciones = list(DBSession.query(RelacionItem).\
							filter(RelacionItem.id_item_actual.in_(items_id)).\
							all())
		tmpl_context.widget = relacion_table

		"""
		cree el value para rellenar la tabla por cuestiones de implementacion
		no pude hacer usando el filler "normal"
		El relleno es igual, lo unico diferente es el "boton" eliminar que pasa 3
		parametros al metodo que elimina.
		Los id's de los items relacionados y el id de la fase
		"""
		value=[]
		aux=[]
		for rel in relaciones:
			if(rel.relacion_parentesco==1):
				aux=[{'relacion_parentesco': 'Padre - Hijo',
				'id_item_actual': rel.id_item_actual,'id_item_relacionado': rel.id_item_relacionado,
				'accion': '<div><a href="/miproyecto/fase/relacion/borrarRelacion/'
				+str(rel.id_item_actual)+'/'+str(rel.id_item_relacionado)+
				'/'+idfase+'">Eliminar Relacion</a></div>'}]
			else:
				aux=[{'relacion_parentesco': 'Antecesor - Sucesor',
				'id_item_actual': rel.id_item_actual,'id_item_relacionado': rel.id_item_relacionado,
				'accion': '<div><a href="/miproyecto/fase/relacion/borrarRelacion/'
				+str(rel.id_item_actual)+'/'+str(rel.id_item_relacionado)+
				'/'+idfase+'">Eliminar Relacion</a></div>'}]
			value=value+aux
		self.params['header_file'] = "abstract"
		self.params['new_url'] = '/miproyecto/fase/relacion/'+idfase+'/new/'
		self.params['idfase'] = idfase
		self.params['modelname'] = "Relaciones"
		self.params['permiso'] = 'editar_item'
		self.params['label'] = 'Nueva Relacion'
		self.init_params(idfase)
		return dict(value=value, params=self.params)

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
