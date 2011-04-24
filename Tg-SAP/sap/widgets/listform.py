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
	#__omit_fields__ = ['contrasenha','proyectos']
	__omit_fields__ = ['lider_id','estado_id']

class ProyectoTableFiller(TableFiller):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id']

class RolTable(TableBase):
	__model__ = Rol

class RolTableFiller(TableFiller):
	__model__ = Rol

usuario_filler = UsuarioTableFiller(DBSession)
usuario_table = UsuarioTable(DBSession);

proyecto_table = ProyectoTable(DBSession);
proyecto_filter = ProyectoTableFiller(DBSession);

rol_table = RolTable(DBSession);
rol_filter = RolTableFiller(DBSession);
