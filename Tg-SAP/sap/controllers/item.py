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

import pygraphviz as pgv
"""
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata
#from sap.controllers.item_detalles import ItemDetallesController
from sap.controllers.item_detalle import *
from tg.controllers import RestController

class ItemController(RestController):
	
	item_detalle = ItemDetalleController()

	#item_detalles = ItemDetallesController()

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
	'idfase':'','permiso':'','progreso':0}


	@expose('sap.templates.item')
	@require(predicates.has_permission('ver_item'))
	def ver(self, id_item, **kw):

		self.params['item'] = DBSession.query(Item).get(id_item)
		progreso = self.params['item'].complejidad*10
		print "PROGRESO:"+str(progreso)
		self.params['progreso'] = progreso

		return dict(params=self.params)

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
		tipo = DBSession.query(TipoItem).get(item.tipo_item)
		atributos = tipo.atributos
		for atributo in atributos:
			detalle = DetalleItem()
			detalle.nombre = atributo.nombre
			detalle.valor = None
			detalle.recurso = None
			item.detalles.append(detalle)
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
		kw['nombre'] = item.nombre
		kw['codigo'] = item.codigo
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
	def put(self, id_item, **kw):
		item =  DBSession.query(Item).get(id_item)
		# Se registra en el historial el item antes de ser modificado
		util.audit_item(item)
		# Se modifica el item
		item.descripcion=kw['descripcion']
		item.codigo=kw['codigo']
		item.nombre=kw['nombre']
		item.complejidad = kw['complejidad']
		item.prioridad = kw['prioridad']
		item.observacion = kw['observacion']
		item.version=int(item.version) + 1
		#Se persiste el item
		DBSession.merge(item)

		flash("El item " +str(item.nombre)+ " ha sido modificado correctamente.")
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
	def calcular_impacto(self, grafo, itemId):
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

		return valorImpacto, impactoList

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
				lista = lista + self.listForward(grafo, grafo.neighbors(item))
			else:
				lista = lista + self.listForward(grafo, grafo.neighbors(item)) + [item]

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
				lista = lista + self.listBackward(grafo, grafo.incidents(item))
			else:
				lista = lista + self.listBackward(grafo, grafo.incidents(item)) + [item]

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
	
	@expose('sap.templates.list')
	@require(predicates.has_permission('editar_item'))
	def historial_versiones(self, id_item):
		versiones = DBSession.query(HistorialItem).\
								filter(HistorialItem.id_item==id_item).\
								all()
		tmpl_context.widget = historial_table
		value = historial_filler.get_value(versiones)
		self.params['title'] = 'Versiones Anteriores'
		self.params['modelname'] = 'Historial'
		self.params['header_file'] = 'abstract'
		self.params['new_url'] = '/'
		self.params['permiso'] = 'NONE'
		self.params['idfase'] = 'NONE'
		return dict (value=value, params=self.params)
	
	
	@expose()
	@require(predicates.has_permission('editar_item'))
	def revertir(self, id_historial):
		historial = DBSession.query(HistorialItem).get(id_historial)
		util.revertir_item(historial)
		redirect("/miproyecto/fase/item/ver/"+str(historial.id_item))

	@expose('sap.templates.impacto')
	@require(predicates.has_permission('editar_item'))
	def impacto(self, id_item,**kw):
		item = DBSession.query(Item).get(id_item)
		fase = DBSession.query(Fase).get(item.fase)
		grafo = self.proyectGraphConstructor(fase.proyecto)
		nodos = []
		impacto, nodos = self.calcular_impacto(grafo, item.id_item)
		flash(impacto)
		self.dibujarGrafo(nodos, item)
		return dict()

	def dibujarGrafo(self, nodos, item_impacto):
		fase = DBSession.query(Fase).get(item_impacto.fase)
		fases = DBSession.query(Fase).filter(Fase.proyecto==fase.proyecto).\
										all()
		desplazamiento_x = []
		for i in fases:
			desplazamiento_x.append(i.id_fase)
		
		desplazamiento_y = []
		for i in range(len(fases)):
			desplazamiento_y.append(0)
		
		gr = pgv.AGraph(directed=True)
		for nodo in nodos:
			item = DBSession.query(Item).get(nodo)
			valor = str(item.codigo)+" : "+str(item.complejidad)
			index = desplazamiento_x.index(item.fase)
			posicion =  str(index*2)+','+str(90-desplazamiento_y[index]*2)
			desplazamiento_y[index] = desplazamiento_y[index] + 1 
			if(nodo == item_impacto.id_item):
				gr.add_node(valor, color='red', pos=posicion, pin=True)
			else:
				gr.add_node(valor, color='black', pos=posicion, pin=True)
		
		#relaciones son aristas
		aristas = DBSession.query(RelacionItem).\
						filter(RelacionItem.id_item_actual.in_(nodos)).\
						filter(RelacionItem.id_item_relacionado.in_(nodos)).\
						all()
		for arista in aristas:
			if(gr.has_edge((arista.id_item_actual, arista.id_item_relacionado))==False):
				item1 = item = DBSession.query(Item).get(arista.id_item_actual)
				item2 = item = DBSession.query(Item).get(arista.id_item_relacionado)
				valor1 = str(item1.codigo)+" : "+str(item1.complejidad)
				valor2 = str(item2.codigo)+" : "+str(item2.complejidad)
				gr.add_edge((valor1, valor2))
				
		gr.layout()
		gr.draw('sap/public/img/calculo_impacto.png')
