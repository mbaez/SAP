
from sprox.fillerbase import *
from sap.model import *

__author__ = "mbaez"
__date__ = "2011-05-28 04:18:55"

from sap.controllers.checker import *

class ExtendedTableList(TableFiller):
	entity_list = None
	__possible_field_names__ = ['nombre','descripcion']

	def _do_get_provider_count_and_objs(self, **kw):
		"""
		Sobre escribe el metodo de la clase padre para que al momento de
		retornar los registros al metodo get_value, se retorne los atributos
		de una lista previamente seteada en le metodo de get_value.

		@type   **kw :
		@param  **kw :

		@rtype  : Integer, __model__[]
		@return : Devuelve la cantidad de registros y los reguistros existentes
				  en el entity_list.
		"""
		if self.entity_list != None :
			return len(self.entity_list), self.entity_list

		objs = DBSession.query(self.__model__).all()
		count = len(objs)
		return count, objs

	def get_value(self,entity_list=None, values=None, **kw ):
		"""
		Sobre escribe el metodo de la clase padre para que al momento de
		de construir la tabla pueda ser construida en base a una lista que
		recibe como paramtero.

		@type   entity_list : __model__[]
		@param  entity_list : Lista de registros en base a los cuales se desea
							  construir la tabla.

		@type   values :
		@param  values :

		@type   **kw :
		@param  **kw :

		@rtype  : String
		@return : Devuelve una cadena que representa las filas de la tabla.
		"""
		self.entity_list = entity_list
		return super(ExtendedTableList, self).get_value(values, **kw)

###############################################################################
#Se trata de anhadir el patron decorator a los extended widgets para facilitar#
#la utilizacion de los mismos y obente un esquema mas entendible              #
###############################################################################

class ExtendedComponent():
	"""
	Componente principal
	"""
	def accion(self, obj):
		pass
	def check_permiso(self, id, permiso_name):
		pass
	def replace(self,action, url, id ,permiso_sufijo,check ):
		pass

class Decorator(ExtendedComponent):
	"""
	Debe ser un objeto que herede de la clase ExtendedComponet
	"""
	component = None
	"""
	Cadena de texto que representa el codigo html que sera anhadido
	"""
	__widget__= ""

	"""
	Clase que actua como proxy entre los componentes.
	"""
	def __init__(self, component=None):
		self.set_component(component)

	def set_component(self, component):
		self.component = component

	def accion(self, obj):
		if self.component != None :
			self.component.__widget__	 = self.__widget__
			return self.component.accion(obj)

	def check_permiso(self, id, permiso_name, has_permiso=None):
		if self.component != None :
			return self.component.check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id ,permiso_sufijo,check ):
		if self.component != None :
			return self.component.replace(action, url, id ,permiso_sufijo,check )

class AcctionDecorator (Decorator):
	"""
	Decorador encargado de anhadir el metodo accion y dibujar el codigo html
	dependiendo del decorador utilizado.
	"""
	def accion (self, obj):
		accion = ', '.join([self.__widget__])
		#print "AcctionDecorator: "+ self.__widget__
		return accion.join(('<div>', '</div>'))

	def check_permiso(self, id, permiso_name, has_permiso=None):

		if(has_permiso ==None):
			return 'visibility: hidden'
		return ''

	def replace(self,action, url, id ,permiso_sufijo,check ):
		pass
		#return super(ActionDecorator, self).replace(action, url,id,permiso_sufijo, check)


class EditActionDecorator(Decorator):
	__html__ = 	"""
				<a class= "edit-project" style= '##editstate##;' href='##url####id##/edit'>editar</a>
				<div>
					<form style= '##deletestate##;' method='POST'
							action='##id##' >
						<input type='hidden' name='_method'
							value='DELETE' >
						</input>
						<input class='delete-row'
							onclick="return confirm('Are you sure?');"
							value='eliminar' type='delete' ></input>
					</form>
				</div>
				"""

	def accion(self, obj):
		self.__widget__ = self.__html__
		accion = Decorator.accion(self,obj)
		return accion

	def replace(self, accion, url, id, permiso_sufijo, check):
		accion = accion.replace('##id##', str(id)).\
						replace('##url##', url).\
						replace('##editstate##', check(id,'editar_'+permiso_sufijo)).\
						replace('##deletestate##', check(id,'eliminar_'+permiso_sufijo))
		return accion


class VerActionDecorator(Decorator):

	__html__= "<a style='##verstate##' href='##url####id##'>ver</a>"

	def accion(self, obj):
		print "VerActionDecorator.accion"
		self.__widget__ = self.__html__
		accion = Decorator.accion(self,obj)
		print "VerActionDecorator.accion" +accion
		return accion

	def replace(self,accion, url, id ,permiso_sufijo,check ):
		return accion.replace('##url##', url).\
				replace('##verstate##', check(id,'ver_'+permiso_sufijo)).\
				replace('##id##', str(id))


class ProyectoDecorator(ExtendedTableList, Decorator):
	__model__ = Proyecto
	__add_fields__ = {'accion':None}
	__url__= "/administracion/proyecto/"
	def accion (self, obj):
		accion = super(ProyectoDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_proyecto)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = checker.check_proyecto_permiso(id,permiso_name,True)
		return super(ProyectoDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(ProyectoDecorator, self).replace( action, url,id,
														'proyecto',
														self.check_permiso
													  )

class ItemTableFiller(ExtendedTableList, Decorator):
	__model__ = Item
	__omit_fields__ = ['tipo_item','fase','id_item']
	__add_fields__ = {'accion':None}
	__url__ = "/miproyecto/fase/item/"
	

	def accion (self, obj):
		accion = super(ItemTableFiller, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_item)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(ItemTableFiller,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(ItemTableFiller, self).replace( action, url,id,
														'fase',
														self.check_permiso
													  )


#Tabla de proyecto con las opciones de eliminar y editar
accion = AcctionDecorator()
model  = ProyectoDecorator(DBSession)
editar = EditActionDecorator()

editar.set_component(accion)
model.set_component(editar)

proyecto_filler = model
#Tabla de proyecto con la opcion de ver

accion_ver = AcctionDecorator()
ProyectoDecorator.__url__ ="/miproyecto/ver/"
model_ver = ProyectoDecorator(DBSession)
ver = VerActionDecorator()

ver.set_component(accion_ver)
model_ver.set_component(ver)

admin_proyecto_filler = model_ver

#Tabla de items com la opcion de eliminar y ediar.
accion_ = AcctionDecorator()
model_ = ItemTableFiller(DBSession)
ver_ = EditActionDecorator()

ver_.set_component(accion_)
model_.set_component(ver_)

item_filler = model_
