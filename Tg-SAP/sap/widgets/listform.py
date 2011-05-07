from sap.model import DBSession, metadata

from sprox.tablebase import TableBase
#from sprox.fillerbase import TableFiller
from sprox.fillerbase import *
from sap.controllers.checker import *

'''
Esta clase sobreescirbe el metodo get_value para que este acepte
una lista de las entidades(entity_list) que se desean mostar
'''
class ExtendedTableFiller(TableFiller):
	'''
	Representa el codigo html que representa a los enlaces de eidtar y 
	eliminar
	'''
	__action__ = 	"<a style= '##editstate##;' href='##id##/edit'>editar</a>"+\
					"<div><form  style= '##deletestate##;' method='POST' action='##id##' class='button-to'>"+\
					"<input type='hidden' name='_method' value='DELETE' ></input>"+\
					"<input class='delete-button' onclick=\"return confirm('Are you sure?');\" "+\
					"value='eliminar' type='submit' ></input>"+\
					"</form>"+\
					"</div>"
	'''
	Representa al usuario que se encuentra logeado en el sistema
	'''
	
	def get_value(self,entity_list=None, values=None, **kw):
		if entity_list == None :
			objs = DBSession.query(self.__entity__).all()
			count = len(objs)
		else :
			count, objs = len(entity_list), entity_list
	
		self.__count__ = count
		rows = []
		
		for obj in objs:
			row = {}
			for field in self.__fields__:
				field_method = getattr(self, field, None)
				if inspect.ismethod(field_method):
					argspec = inspect.getargspec(field_method)
					if argspec and (len(argspec[0])-2>=len(kw) or argspec[2]):
						value = getattr(self, field)(obj, **kw)
					else:
						value = getattr(self, field)(obj)
				else:
					value = getattr(obj, field)
					if 'password' in field.lower():
						row[field] = '******'
						continue
					elif isinstance(value, list):
						value = self._get_list_data_value(field, value)
					elif self.__provider__.is_relation(self.__entity__, field) and value is not None:
						value = self._get_relation_value(field, value)
					elif self.__provider__.is_binary(self.__entity__, field) and value is not None:
						value = '<file>'
				row[field] = unicode(value)
			rows.append(row)
		return rows


from sap.model import *


class UsuarioTableFiller(ExtendedTableFiller):
	__model__ = Usuario
	__omit_fields__ = ['contrasenha','proyectos']
	

class UsuarioTable(TableBase):
	__model__ = Usuario
	__omit_fields__ = ['contrasenha','proyectos']

"""
"""
class ProyectoTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id', '__actions__']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class ProyectoTableFiller(ExtendedTableFiller):
	__model__ = Proyecto
	__add_fields__ = {'accion':None}
	
	def accion (self, obj):
		accion = ', '.join([self.__action__.replace('##id##', str(obj.id_proyecto)).
		replace('##editstate##', self.check_permiso(obj.id_proyecto,'editar_proyecto')).
		replace('##deletestate##', self.check_permiso(obj.id_proyecto,'eliminar_proyecto'))])
		return accion.join(('<div>', '</div>'))
	
	def check_permiso(self, id_proyecto, permiso_name):
		has_permiso = checker.check_proyecto_permiso(id_proyecto,permiso_name,True)
		
		if(has_permiso ==None):
			return 'visibility: hidden'
		return ''
		
"""
"""
class ProyectoAdminTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id', 'id_proyecto' ,
						'nro_fases', '__actions__'  ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class ProyectoAdminTableFiller(ExtendedTableFiller):
	__model__ = Proyecto
	__add_fields__ = {'accion':None}

	def accion (self, obj):
		
		accion = ', '.join(['<a href="/administracion/proyecto/' + 
							str(obj.id_proyecto) + '/edit">ver</a>'])
		return accion.join(('<div>', '</div>'))


class RolTable(TableBase):
	__model__ = Rol

class RolTableFiller(TableFiller):
	__model__ = Rol




usuario_filler = UsuarioTableFiller(DBSession)
usuario_table = UsuarioTable(DBSession);

proyecto_table = ProyectoTable(DBSession);
proyecto_filler = ProyectoTableFiller(DBSession);

rol_table = RolTable(DBSession);
rol_filler = RolTableFiller(DBSession);

admin_proyecto_table = ProyectoAdminTable(DBSession);
admin_proyecto_filler = ProyectoAdminTableFiller(DBSession);
