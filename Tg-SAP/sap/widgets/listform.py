from sap.model import DBSession, metadata

from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller

from sap.model import *

class UsuarioTableFiller(TableFiller):
	__model__ = Usuario
	__omit_fields__ = ['contrasenha','proyectos']


class UsuarioTable(TableBase):
	__model__ = Usuario
	__omit_fields__ = ['contrasenha','proyectos']


class ProyectoTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id']

class ProyectoTableFiller(TableFiller):
	__model__ = Proyecto


class ProyectoAdminTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id', 'id_proyecto' ,
						'nro_fases', '__actions__'  ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class ProyectoAdminTableFiller(TableFiller):
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
