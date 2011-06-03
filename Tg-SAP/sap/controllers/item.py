# -*- coding: utf-8 -*-
"""Main Controller"""


from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

#import de la libreria de grafo
from sap.lib.pygraph.classes.digraph import *
from sap.lib.pygraph.algorithms.cycles import *
from sap.lib.pygraph.readwrite.dot import write
# Import graphviz
"""
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv

from pygraphviz import *
"""
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
from tg.controllers import RestController

class ItemController(RestController):

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':''}

	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_item'))
	def new(self, idfase, modelname="", **kw):
		new_item_form.tipo_item_relacion.idfase = idfase
		tmpl_context.widget = new_item_form
		header_file = "abstract"
		self.params['title'] = 'Nuevo Item'
		self.params['modelname'] = 'Item'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/administracion/miproyecto/fase/item/'+idfase+'/new'
		self.params['permiso'] = 'crear_item'
		self.params['idfase'] = idfase
		self.params['cancelar_url'] = '/miproyecto/fase/get_all/'+str(idfase)
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_item_form, error_handler=new)
	@require(predicates.has_permission('crear_item'))
	@expose()
	def post(self, idfase, modelname='',**kw):
		del kw['sprox_id']
		item = Item()
		item.descripcion=kw['descripcion']
		item.complejidad=kw['complejidad']
		item.prioridad=kw['prioridad']
		item.observacion=kw['observacion']
		item.fase = idfase
		item.estado=1
		item.tipo_item= kw['tipo_item_relacion']
		item.version=1
		DBSession.add(item)
		flash("El item se ha creado correctamente")
		redirect('/miproyecto/fase/get_all/'+idfase)

	"""
	Encargado de carga el widget para editar las instancias,
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_item'))
	def edit(self, id,**kw):
		item =  DBSession.query(Item).get(id)
		tmpl_context.widget = item_edit_form
		kw['id_item'] = item.id_item
		kw['descripcion'] = item.descripcion
		kw['complejidad'] = item.complejidad
		kw['prioridad'] = item.prioridad
		kw['observacion'] = item.observacion
		self.params['modelname'] = 'Item'
		self.params['header_file'] = 'abstract'
		return dict(value=kw, params=self.params)

	"""
	Evento invocado luego de un evento post en el form de editar
	encargado de persistir las modificaciones de las instancias.
	"""
	@validate(item_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_item'))
	@expose()
	def put(self, idfase, **kw):
		item =  DBSession.query(Item).get(int(kw['id_item']))
		# Se registra en el historial el item antes de ser modificado
		util.audit_item(item)
		# Se modifica el item
		item.descripcion=kw['descripcion']
		item.complejidad = kw['complejidad']
		item.prioridad = kw['prioridad']
		item.observacion = kw['observacion']
		item.version=int(item.version) + 1
		#Se persiste el item
		DBSession.merge(item)

		flash("El item id= " +str(item.id_item)+ " ha sido modificado correctamente.")
		redirect('/miproyecto/fase/get_all/'+str(item.fase))

	"""
	metodo que retorna el padres de un item.
	parametros:
	- item Item
	retorna:
	- item Item
	"""
	def getPadre (self, item):
		#lista de padres
		padre
		#relaciones
		relacion

		#se obtienen todas las relaciones del item. Si el id de la relacion
		#hijo-padre es 1 se obtienen todas las relaciones de este tipo que
		#tiene el item actual
		relacion = DBSession.query(RelacionItem).\
			filter(RelacionItem.id_item_relacionado==item.id_item).\
			filter(RelacionItem.relacion_parentesco==1).\
			first()

		padre = DBSession.query(Item).get(relacion.id_item_actual)
		return padre

	"""
	metodo que retorna los items aprobados de una fase.
	parametros:
	- idfase Integer
	retorna:
	- List[] Item
	"""
	def getItemsAprobados (self, idfase):
		#lista de items aprobados de la fase. Suponiendo que el id del estado "aprobado"
		#sea 1
		itemsAprobados = DBSession.query(Item).filter(Item.fase==idfase).\
												filter(Item.estado_item==1).\
												all()
		return itemsAprobados

	"""
	Construye el grafo completo del proyecto con las todas las relaciones
	parametros:
	idproyecto: Integer
	retorna:
	grafo: digraph
	"""
	def proyectGraphConstructor(self, idproyecto):
		fases = DBSession.query(Fase).filter(Fase.proyecto==idproyecto).all()
		grafo = digraph()
		items = []
		itemsId = []

		#se "obtienen los items de cada fase
		for fase in fases:
			items = items + list(DBSession.query(Item).filter(Item.fase==fase.id_fase))

		for item in items:
			grafo.add_nodes([item.id_item])

		#guardar los ids de los items
		for item in items:
			itemsId = itemsId + [item.id_item]
 		"""
		Se busca en la tabla RelacionItem todas las relaciones
		que contengan a los items del proyecto
		"""
		relaciones = DBSession.query(RelacionItem).\
						filter((RelacionItem.id_item_actual).in_(itemsId)).\
						all()

		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id_item_actual,relacion.id_item_relacionado))


		return grafo

	"""
	construye el grafo "Padre-Hijo" dentro de una fase
	parametros:
	- idfase Integer
	retorna:
	- grafo digraph (grafo dirigido)
	"""
	def faseGraphConstructor(self, idfase):
		#lista de items para el grafo
		items = DBSession.query(Item).filter(Item.fase==idfase).all()
		itemsId = []

		"""
		Todos los items de la fase forman parte del grafo (item = nodo)
		"grafo" es un grafo dirigido que representa las relaciones padre-hijo
		en una fase.
		"""
		grafo = digraph()
		for item in items:
			grafo.add_nodes([item.id_item])

		"""
		Se busca en la tabla RelacionItem todas las relaciones de padre-hijo
		que contengan a los items de la fase
		"""
		#guardar los ids de los items
		for item in items:
			itemsId = itemsId + [item.id_item]

		relaciones = DBSession.query(RelacionItem).\
						filter(RelacionItem.relacion_parentesco==1).\
						filter(RelacionItem.id_item_actual.in_(itemsId)).\
						filter(RelacionItem.id_item_relacionado.in_(itemsId)).\
						all()

		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id_item_actual,relacion.id_item_relacionado))

		return grafo

	"""
	metodo para verificar si una nueva relacion provoca un ciclo
	parametros:
	- nuevaRelacion tipo RelacionItem
	- idfase tipo Integer
	retorna
		List [] si no tiene ciclo
		List [edges] los enlaces que forman el ciclo
	"""
	def ciclo (self, id1, id2, idfase):
		grafo = self.faseGraphConstructor(idfase)
		if(grafo.has_edge((id1,id2))):
			return []
		grafo.add_edge((id1,id2))
		return cycle(grafo)

	"""
	metodo que calcula el impacto de la modificacion de un item
	parametros:
	- itemId tipo Integer
	- grafo del proyecto
	retorna:
	- valorImpacto Tipo Integer
	"""
	def calcularImpacto(self, grafo, itemId):
		"""
		obtener la lista de todos antecesores directos e indirectos
		el list(set()) es para que elimine los repetidos
		los metodos listBackwards y listForward retornan listas con elementos
		repetidos.
		"""
		antecesores = list(set(self.listBackward(grafo, grafo.incidents(itemId))))
		"""
		se añade a la lista el propio item
		"""
		item = [itemId]
		"""
		obtener la lista de todos sucesores directos e indirectos
		"""
		sucesores = list(set(self.listForward(grafo, grafo.neighbors(itemId))))

		#suma de listas
		impactoList = antecesores + item + sucesores

		valorImpacto = 0;
		for idItem in impactoList:
			itemActual = DBSession.query(Item).get(idItem)
			valorImpacto = valorImpacto + itemActual.complejidad

		return valorImpacto

	"""
	metodo recursivo para obtener la lista de sucesores del item
	TODO que ya filtre los repetidos
	parametros:
	- grafo digraph
	- items List[Item]
	retorna
	List[Item]
	"""
	def listForward(self, grafo, items):
		if(len(items)==0):
			return []
		if(len(items)==1 and len(grafo.neighbors(items[0])) == 0):
			return [items[0]]
		lista = []
		for item in items:
			if(item in lista):
				lista = lista + listForward(grafo, grafo.neighbors(item))
			else:
				lista = lista + listForward(grafo, grafo.neighbors(item)) + [item]

		return lista

	"""
	metodo recursivo para obtener la lista de antecesores del item
	TODO que ya filtre los repetidos
	parametros:
	- grafo digraph
	- items List[Item]
	retorna
	List[Item]
	"""
	def listBackward(self, grafo, items):
		if(len(items)==0):
			return []
		if(len(items)==1 and len(grafo.incidents(items[0]))==0):
			return [items[0]]

		lista = []
		for item in items:
			if(item in lista):
				lista = lista + listBackward(grafo, grafo.incidents(item))
			else:
				lista = lista + listBackward(grafo, grafo.incidents(item)) + [item]

		return lista

	"""
	Si se quiere eliminar un item se verifica que esto no provoque que
	otro item, de la misma fase u otra quede huerfano
	parametros:
	grafo digraph -> grafo completo del proyecto
	retorna:
		True si es que deja huerfano a algun item
		False en caso contrario


		TODO
		no se si esto se aplica solo sobre items aprobados o que onda
	"""
	'''
	@expose('sap.templates.grafico')
	def dibujarGrafo(self):
		grafo = self.faseGraphConstructor(1)
		dot = write(grafo)
		gvv = gv.readstring(dot)
		gv.layout(gvv,'dot')
		gv.render(gvv,'svg',"fase.svg")
		return dict()
	'''
	
	def marcar_en_revision(self, grafo, itemId):
		"""
		obtener la lista de todos antecesores directos e indirectos
		el list(set()) es para que elimine los repetidos
		los metodos listBackwards y listForward retornan listas con elementos
		repetidos.
		"""
		antecesores = list(set(self.listBackward(grafo, grafo.incidents(itemId))))
		"""
		se añade a la lista el propio item
		"""
		item = [itemId]
		"""
		obtener la lista de todos sucesores directos e indirectos
		"""
		sucesores = list(set(self.listForward(grafo, grafo.neighbors(itemId))))

		#suma de listas
		items = antecesores + item + sucesores

		for idItem in items:
			itemActual = DBSession.query(Item).get(idItem)
			itemActual.estado = 3
			DBSession.merge(itemActual)

	"""
	Si se quiere eliminar un item se verifica que esto no provoque que
	otro item, de la misma fase u otra quede huerfano
	parametros:
	grafo digraph -> grafo completo del proyecto
	retorna:
		True si es que deja huerfano a algun item
		False en caso contrario


		TODO
		no se si esto se aplica solo sobre items aprobados o que onda
	"""
	@expose()
	def aprobar_item(self, iditem, **kw):
		"""
		Metodo para aprobar un item
		"""
		item = DBSession.query(Item).get(iditem)
		item.estado = 1
		idfase = item.fase
		DBSession.merge(item)
		flash("El item " + item.codigo+ " ha sido aprobado correctamente")
		redirect('/miproyecto/fase/get_all/'+idfase)
