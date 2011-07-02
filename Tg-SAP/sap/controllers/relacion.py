# -*- coding: utf-8 -*-

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
	"""	Controlador de las relaciones del item"""

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':'', 'label': '', 'cancelar_url': ''
			 }
	"""
	parametro que contiene los valores de varios parametros y es enviado a
	los templates
	"""

	@expose('sap.templates.fase')
	@require(predicates.has_permission('editar_item'))
	def new(self, idfase, args={}, **kw):
		"""
		Encargado de cargar el widget para crear nuevas instancias,
		solo tienen acceso aquellos usuarios que posean el premiso de crear

		@type  idfase : Integer
		@param idfase : Identificador de la fase.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.

		"""

		new_relacion_form.item_1.idfase=idfase
		"""
		dentro del form un combo trae los items de la fase actual
		y el otro los items de la fase actual y la siguiente
		"""
		new_relacion_form.item_2.idfase=idfase
		tmpl_context.widget = new_relacion_form

		self.params['header_file'] = "abstract"
		self.params['idfase'] = idfase
		self.params['modelname'] = "Relacion"
		self.params['permiso'] = 'editar_item'
		self.params['cancelar_url'] = '/miproyecto/fase/relacion/list/'+str(idfase)
		self.init_params(idfase)
		return dict(value=kw, params=self.params)


	@validate(new_relacion_form, error_handler=new)
	@expose()
	@require(predicates.has_permission('editar_item'))
	def post(self, idfase, args={},**kw):
		"""
		Evento invocado luego de un evento post en el form de crear
		ecargado de persistir las nuevas instancias.

		@type  idfase : Integer
		@param idfase : Identificador de la fase.

		@type  args : Hash
		@param args : Argumentos de template

		@type  kw : Hash
		@param kw : Keywords

		"""
		del kw['sprox_id']
		"""
		se crea la nueva relacion y se le asignan los valores de los combos
		"""
		if kw['item_1'] != None and kw['item_2'] != None:
			relacion = RelacionItem()
			relacion.id_item_actual = kw['item_1']
			relacion.id_item_relacionado = kw['item_2']
			relacion.relacion_parentesco = 2

			DBSession.merge(relacion)

			#auditar items y aumentar su version
			item1 = DBSession.query(Item).get(kw['item_1'])
			item2 = DBSession.query(Item).get(kw['item_2'])

			item_util.audit_item(item1)
			item_util.audit_item(item2)

			item1.version += 1
			item2.version += 1

			DBSession.add(item1)
			DBSession.add(item2)

			#marcar en revision los relacionados
			fase = DBSession.query(Fase).get(item1.fase)
			grafo = item_util.proyectGraphConstructor(fase.proyecto)
			item_util.marcar_en_revision(grafo, item1.id_item)

			flash("La relacion se ha creado correctamente")
			redirect("/miproyecto/fase/relacion/list/"+idfase)

		flash("No se puede crear la relacion", 'warning')
		redirect("/miproyecto/fase/relacion/"+idfase+"/new/")

	@expose()
	@require(predicates.has_permission('editar_item'))
	def borrarRelacion(self, item1, item2, idfase, **kw):

		if not self.puede_borrar(item1, item2, idfase):
			flash ("No se peude borrar la relacion! deja huerfanos", 'warning')
			redirect("/miproyecto/fase/relacion/list/"+idfase)

		#auditar items y aumentar su version
		item_1 = DBSession.query(Item).get(item1)
		item_2 = DBSession.query(Item).get(item2)

		item_util.audit_item(item_1)
		item_util.audit_item(item_2)

		item_1.version += 1
		item_2.version += 1

		item_1.estado = 3
		item_2.estado = 3

		DBSession.add(item_1)
		DBSession.add(item_2)

		DBSession.delete(DBSession.query(RelacionItem).\
					filter(RelacionItem.id_item_actual==item1).\
					filter(RelacionItem.id_item_relacionado==item2).\
					one())

		#marcar en revision los relacionados
		fase = DBSession.query(Fase).get(item_1.fase)
		grafo = item_util.proyectGraphConstructor(fase.proyecto)
		item_util.marcar_en_revision(grafo, item_1.id_item)
		item_util.marcar_en_revision(grafo, item_2.id_item)

		flash("Se ha eliminado la relacion: "+item1+" <--> "+item2)
		redirect("/miproyecto/fase/relacion/list/"+idfase)

	def puede_borrar(self, item1, item2, idfase):
		item = DBSession.query(Item).get(item2)
		fase_actual = DBSession.query(Fase).get(item.fase)
		fases_de_proyecto = DBSession.query(Fase).\
								filter(Fase.proyecto == fase_actual.proyecto).\
								order_by(Fase.id_fase).\
								all()
		primera_fase = False
		if fase_actual.id_fase == fases_de_proyecto[0].id_fase:
			return True

		if len(item_util.get_incidentes(item2)) == 1:
			return False

		return True



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
