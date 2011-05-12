# -*- coding: utf-8 -*-
"""Main Controller"""


from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

#import de la libreria de grafo
from sap.lib.pygraph.classes.digraph import *
from sap.lib.pygraph.algorithms.cycles import *

from sap.lib.base import BaseController
from sap.model import *
from sap.model import DBSession, metadata

class ItemController(BaseController):
	
	@expose('sap.templates.pruebas.pruebas')
	def prueba(self):
		
		
		return dict('/prueba')
		
	"""
	metodo que retorna el padres de un item.
	parametros:
	- item Item
	retorna:
	- item Item
	"""
	def getPadre (item):
		#lista de padres
		padre
		#relaciones
		relacion
		
		#se obtienen todas las relaciones del item. Si el id de la relacion
		#hijo-padre es 1 se obtienen todas las relaciones de este tipo que
		#tiene el item actual	
		relacion = DBSession.query(RelacionItem).\
			filter(RelacionItem.item_realcionado==item.id_item).\
			filter(RelacionItem.relacion_parentesco==1).\
			first()
		
		padre = DBSession.query(Item).get(relacion.id)
		return padre
	
	"""
	metodo que retorna los items aprobados de una fase.
	parametros:
	- idfase Integer
	retorna:
	- List[] Item
	"""
	def getItemsAprobados (idfase):
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
	def proyectGraphConstructor(idproyecto):
		fases = DBSession.query(Fase).filter(Fase.proyecto==idproyecto)
		grafo = digraph()
		items = []
		#se "obtienen los items de cada fase
		for fase in fases
			items = items + DBSession.query(Item).filter(Item.fase==fase.id_fase)
		
		for item in items:
			grafo.add_nodes([item.id_item])
		
		"""
		Se busca en la tabla RelacionItem todas las relaciones 
		que contengan a los items del proyecto
		"""
		relaciones = DBSession.query(RelacionItem).\
						filter(RelacionItem.id.in_(items)).\
						all()
		
		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id,relacion.item_realcionado))
		
			
		return grafo
	
	"""
	construye el grafo "Padre-Hijo" dentro de una fase
	parametros:
	- idfase Integer
	retorna:
	- grafo digraph (grafo dirigido)
	"""	
	def faseGraphConstructor(idfase):
		#lista de items para el grafo
		items = DBSession.query(Item).filter(Item.fase==idfase).all()
		
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
		relaciones = DBSession.query(RelacionItem).\
						#filtro de acuerdo al tipo de relacion
						filter(RelacionItem.relacion_parentesco==1).\
						#filtro para que solo traiga las relaciones de los 
						#items de esta fase.
						filter(RelacionItem.id.in_(items)).\
						all()
		
		#Se añaden las aristas entre los items relacionados
		for relacion in relaciones:
			grafo.add_edge((relacion.id,relacion.item_realcionado))
		
		return grafo
	
	"""
	metodo para verificar si una nueva relacion provoca un ciclo
	parametros:
	- nuevaRelacion tipo RelacionItem
	- idfase tipo Integer
	retorna
		Boolean:
			True si es que se forma un ciclo con la nueva relacion
			False en caso contrario
	"""		
	def ciclo (nuevaRelacion, idfase):
		grafo = graphConstructor(idfase) 
		grafo.add_edges(nuevaRelacion.id, nuevaRelacion.item_realcionado)
		if(find_cycle(grafo)!= [])
			return True
		return False
	
	"""
	metodo que calcula el impacto de la modificacion de un item
	parametros:
	- itemId tipo Integer 
	- grafo del proyecto
	retorna:
	- valorImpacto Tipo Integer
	""" 
	def calcularImpacto(grafo, itemId):
		"""
		obtener la lista de todos antecesores directos e indirectos
		el list(set()) es para que elimine los repetidos
		los metodos listBackwards y listForward retornan listas con elementos
		repetidos.
		"""
		antecesores = list(set(listBackward(grafo, grafo.incidents(itemId))))
		"""
		se añade a la lista el propio item
		"""
		item = [itemId]
		"""
		obtener la lista de todos sucesores directos e indirectos
		"""
		sucesores = list(set(listForward(grafo, grafo.neighbors(itemId))))
		
		#suma de listas
		impactoList = antecesores + item + sucesores
		
		for idItem in impactoList
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
	def listForward(grafo, items):
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
	def listBackward(grafo, items):
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
	"""
	def huerfano(grafo, idItem)
		"""
		TODO
		no se si esto se aplica solo sobre items aprobados o que onda
		"""
	
	
		
