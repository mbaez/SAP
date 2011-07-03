
from sprox.fillerbase import *
from sap.model import *

__author__ = "mbaez"
__date__ = "2011-05-28 04:18:55"

from sap.controllers.checker import *
from sap.controllers.util import *

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
#la utilizacion de los mismos y obtener un esquema mas entendible              #
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
	Clase que actua como proxy entre los componentes.
	"""

	"""Debe ser un objeto que herede de la clase ExtendedComponet"""
	component = None

	"""Cadena de texto que representa el codigo html que sera anhadido"""
	__widget__= ""

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
		return accion.join(('<div>', '</div>'))

	def check_permiso(self, id, permiso_name, has_permiso=None):

		if(has_permiso == None or has_permiso == False):
			return 'visibility: hidden'
		return ''

	def replace(self,action, url, id ,permiso_sufijo,check ):
		pass

###############################################################################
# Decoradores de los actions, indican con que se va llenar el campo action
###############################################################################
class EditActionDecorator(Decorator):
	__html__ = 	"""
				<a class= "edit-row" style= '##editstate##;' href='##url####id##/edit'>editar</a>
				<div>
					<form style= '##deletestate##;' method='POST'
							action='##id##' >
						<input class='delete-row' type='hidden' name='_method'
							value='DELETE' >
						</input>
						<input class='delete-row'
							onclick="return confirm('Esta seguro que desea eliminar?');"
							value='eliminar' type='submit' ></input>
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

	__html__= "<a style='##verstate##' class='link' href='##url####id##'>Ver</a>"

	def accion(self, obj):
		self.__widget__ = self.__html__
		accion = Decorator.accion(self,obj)
		return accion

	def replace(self,accion, url, id ,permiso_sufijo,check ):
		return accion.replace('##url##', url).\
				replace('##verstate##', check(id,'ver_'+permiso_sufijo)).\
				replace('##id##', str(id))

class LabelActionDecorator(Decorator):
	__label__ = "Asignar"
	__html__= "<a style='##state##' class='link' href='##url####id####extra_url##'>##label##</a>"
	__extra_url__ = "/edit"

	params={'__extra_url__':__extra_url__, '__label__':__label__}

	def __init__(self, params=None):
		if params == None:
			return

		self.__extra_url__ = params['__extra_url__']
		self.__label__ = params['__label__']

	def accion(self, obj):
		self.__widget__ = self.__html__.replace("##label##", self.__label__)
		accion = Decorator.accion(self,obj)
		return accion

	def replace(self,accion, url, id ,permiso_sufijo,check ):
		return accion.replace('##url##', url).\
				replace('##state##', check(id,'ver_'+permiso_sufijo)).\
				replace('##id##', str(id)).\
				replace('##extra_url##', self.__extra_url__)

###############################################################################
# Model Decorators, Son las clases que indican con que datos se van a cargar
###############################################################################
class ProyectoModelDecorator(ExtendedTableList, Decorator):
	__model__ = Proyecto
	__add_fields__ = {'accion':None}
	__url__= "/administracion/proyecto/"
	__check_permiso__ = True

	def __init__(self, provider_hint=None, url=None, check_permiso=True ,**provider_hints):
		super(ProyectoModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url != None :
			self.__url__ = url
		if check_permiso !=True :
			self.__check_permiso__ = False;

	def accion (self, obj):
		accion = super(ProyectoModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_proyecto)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True

		if self.__check_permiso__ :
			has_permiso = checker.check_proyecto_permiso(id,permiso_name,True)

		return super(ProyectoModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(ProyectoModelDecorator, self).replace( action, url,id,
														'proyecto',
														self.check_permiso
													  )

class ItemModelDecorator(ExtendedTableList, Decorator):
	__model__ = Item
	__add_fields__ = {'accion':None}
	__url__ = "/miproyecto/fase/item/"

	def __init__(self, provider_hint=None, url=None, check_permiso=True ,**provider_hints):
		super(ItemModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(ItemModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_item)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(ItemModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(ItemModelDecorator, self).replace( action, url,id,
														'fase',
														self.check_permiso
													  )

class ParticipantesModelDecorator(ExtendedTableList, Decorator):
	__model__ = Rol
	__add_fields__ = {'accion':None}
	__url__ = "/miproyecto/fase/participantes/"

	def __init__(self, provider_hint=None, url=None, check_permiso=True ,**provider_hints):
		super(ParticipantesModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(ParticipantesModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.rol_id)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(ParticipantesModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(ParticipantesModelDecorator, self).replace( action, url,id,
														'participantes',
														self.check_permiso
													  )

class LineaBaseModelDecorator(ExtendedTableList, Decorator):
	__model__ = LineaBase
	__add_fields__ = {'accion':None}
	__url__ = "/miproyecto/fase/linea_base/"

	def __init__(self, provider_hint=None, url=None, check_permiso=True ,**provider_hints):
		super(LineaBaseModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(LineaBaseModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_linea_base)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		linea_base = DBSession.query(LineaBase).get(id)
		estado_linea_base = linea_base.estado
		if(estado_linea_base.nombre == 'Abierta'):
			has_permiso = False
		else:
			has_permiso = True
		return super(LineaBaseModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(LineaBaseModelDecorator, self).replace( action, url,id,
														'linea_base',
														self.check_permiso
													  )
class TipoItemModelDecorator(ExtendedTableList, Decorator):

	__model__ = TipoItem
	__add_fields__ = {'accion':None}
	__url__ = '/miproyecto/fase/tipo_item/atributos/'

	def __init__(self, provider_hint=None, url=None,check_permiso=True ,**provider_hints):
		super(TipoItemModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(TipoItemModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_tipo_item)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(TipoItemModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(TipoItemModelDecorator, self).replace( action, url,id,
														'tipo_item',
														self.check_permiso
													  )

class FaseModelDecorator(ExtendedTableList, Decorator):
	__model__ = Fase
	__add_fields__ = {'accion':None}
	__url__ = '/miproyecto/fase/get_all/'

	def __init__(self, provider_hint=None, url=None, check_permiso=True,**provider_hints):
		super(FaseModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(FaseModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_fase)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		has_permiso = checker.check_fase_permiso(id, permiso_name, True)
		return super(FaseModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(FaseModelDecorator, self).replace( action, url,id,
														'fase',
														self.check_permiso
													  )


class HistorialModelDecorator(ExtendedTableList, Decorator):

	__model__ = HistorialItem
	__add_fields__ = {'accion':None}
	__url__ = '/miproyecto/fase/item/revertir/'

	def __init__(self, provider_hint=None, url=None,  check_permiso=True ,**provider_hints):
		super(HistorialModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(HistorialModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_historial_item)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		hist_item = DBSession.query(HistorialItem).get(id)
		id_item = hist_item.id_item
		item = DBSession.query(Item).get(id_item)
		has_permiso = item_util.verificar_linea_base(item)
		print has_permiso
		return super(HistorialModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(HistorialModelDecorator, self).replace( action, url,id,
														'historial_item',
														self.check_permiso
													  )

class UsuarioModelDecorator(ExtendedTableList, Decorator):

	__model__ = Usuario
	__add_fields__ = {'accion':None}
	__url__ = '/administracion/usuario/'

	def __init__(self, provider_hint=None, url=None,  check_permiso=True ,**provider_hints):
		super(UsuarioModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(UsuarioModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.usuario_id)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(UsuarioModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(UsuarioModelDecorator, self).replace( action, url,id,
														'usuario',
														self.check_permiso
													  )

class RolModelDecorator(ExtendedTableList, Decorator):

	__model__ = Rol
	__add_fields__ = {'accion':None}
	__url__ = '/administracion/rol/'

	def __init__(self, provider_hint=None, url=None,  check_permiso=True ,**provider_hints):
		super(RolModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(RolModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.rol_id)
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		has_permiso = True
		return super(RolModelDecorator,self).check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(RolModelDecorator, self).replace( action, url,id,
														'rol',
														self.check_permiso
													  )


class DetalleItemModelDecorator(ExtendedTableList, Decorator):
	__model__ = DetalleItem
	__add_fields__ = {'accion':None}
	__url__ = "/miproyecto/fase/item/"

	def __init__(self, provider_hint=None, url=None, check_permiso=True ,**provider_hints):
		super(DetalleItemModelDecorator, self).__init__(provider_hint, **provider_hints)

		if url == None :
			return
		self.__url__ = url

	def accion (self, obj):
		accion = super(DetalleItemModelDecorator, self).accion(obj)
		accion = self.replace(accion,self.__url__, obj.id_item_detalle)
		if obj.adjunto != None :
			accion = "<div> " + accion
			accion +="<div><a class='link' href='/miproyecto/fase/item/item_detalle/descargar/"+\
					str(obj.id_item_detalle) + "'>Descargar</a></div></div>"
		return accion

	def check_permiso(self, id, permiso_name, has_permiso=None):
		detalle_item = DBSession.query(DetalleItem).get(id)
		item = detalle_item.item
		has_permiso = item_util.verificar_linea_base(item)

		print "HASTA ACA " + str(has_permiso)

		return super(DetalleItemModelDecorator,self).\
			check_permiso(id, permiso_name, has_permiso)

	def replace(self,action, url, id):
		return super(DetalleItemModelDecorator, self).replace( action, url,id,
														'detalle',
														self.check_permiso
													  )

###############################################################################
# Se crean los widgets utilizando los decoradores
###############################################################################
def create_widget(__base_model__, __decorator__, __url__=None,check_permiso=True, params=None):
	"""
	Crea un widget y le anhade los decoradores
	"""
	action = AcctionDecorator()
	action_decorator = __decorator__(params)

	model_component = __base_model__(DBSession, __url__,check_permiso)

	action_decorator.set_component(action)
	model_component.set_component(action_decorator)

	return model_component
