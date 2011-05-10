from sap.model import DBSession, metadata

from sprox.tablebase import TableBase
#from sprox.fillerbase import TableFiller
from sprox.fillerbase import *
from sap.controllers.checker import *

from sap.model import *
from sap.widgets.extended import ExtendedTableFiller


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
		
		accion = ', '.join(['<a href="/miproyecto/ver/' +str(obj.id_proyecto)+'">ver</a>'])
		return accion.join(('<div>', '</div>'))

class FaseAdminTable(TableBase):
	__model__ = Fase
	__omit_fields__ = ['id_fase', '__actions__'  ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class FaseAdminTableFiller(ExtendedTableFiller):
	__model__ = Fase
	__add_fields__ = {'accion':None}

	def accion (self, obj):
		
		accion = ', '.join(['<a href="/miproyecto/fase/' +str(obj.id_fase)+'">ver</a>'])
		return accion.join(('<div>', '</div>'))

class RolTable(TableBase):
	__model__ = Rol

class RolTableFiller(TableFiller):
	__model__ = Rol




usuario_filler = UsuarioTableFiller(DBSession)
usuario_table = UsuarioTable(DBSession);

proyecto_table = ProyectoTable(DBSession);
proyecto_filler = ProyectoTableFiller(DBSession);

fase_table = FaseAdminTable(DBSession);
fase_filler = FaseAdminTableFiller(DBSession);

rol_table = RolTable(DBSession);
rol_filler = RolTableFiller(DBSession);

admin_proyecto_table = ProyectoAdminTable(DBSession);
admin_proyecto_filler = ProyectoAdminTableFiller(DBSession);
