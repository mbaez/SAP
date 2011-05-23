from sap.model import DBSession, metadata

from sprox.tablebase import TableBase
#from sprox.fillerbase import TableFiller
from sprox.fillerbase import *
from sap.controllers.checker import *

from sap.model import *
from sap.widgets.extended import ExtendedTableFiller

####################################################
# Widgets de los Usuarios
####################################################
class UsuarioTableFiller(ExtendedTableFiller):
	__model__ = Usuario


class UsuarioTable(TableBase):
	__model__ = Usuario
	__omit_fields__ = ['_password','proyectos','password', 'roles']

usuario_filler = UsuarioTableFiller(DBSession)
usuario_table = UsuarioTable(DBSession);

####################################################
# Widgets de los Proyectos
####################################################
class ProyectoTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id', '__actions__',  'roles_permisos']
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

proyecto_table = ProyectoTable(DBSession);
proyecto_filler = ProyectoTableFiller(DBSession);
####################################################
# Widgets de los
####################################################
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

admin_proyecto_table = ProyectoAdminTable(DBSession);
admin_proyecto_filler = ProyectoAdminTableFiller(DBSession);
####################################################
# Widgets de las Fases
####################################################
class FaseAdminTable(TableBase):
	__model__ = Fase
	__omit_fields__ = ['id_fase', '__actions__'  ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class FaseAdminTableFiller(ExtendedTableFiller):
	__model__ = Fase
	__add_fields__ = {'accion':None}

	def accion (self, obj):

		accion = ', '.join(['<a href="/miproyecto/fase/get_all/' +str(obj.id_fase)+'">ver</a>'])
		return accion.join(('<div>', '</div>'))

fase_table = FaseAdminTable(DBSession);
fase_filler = FaseAdminTableFiller(DBSession);
####################################################
# Widgets de los Roles
####################################################
class RolTable(TableBase):
	__model__ = Rol
	__omit_fields__ = ['rol_id', 'permisos','usuarios'  ]

class RolTableFiller(ExtendedTableFiller):
	__model__ = Rol

rol_table = RolTable(DBSession);
rol_filler = RolTableFiller(DBSession);
####################################################
# Widgets de los Items
####################################################
class ItemTable(TableBase):
	__model__ = Item
	__omit_fields__ = ['tipo_item','fase','id_item']

class ItemTableFiller(TableFiller):
	__model__ = Item
	__omit_fields__ = ['tipo_item','fase','id_item']


item_table = ItemTable(DBSession);
item_filler = ItemTableFiller(DBSession);
####################################################
# Widgets de los Tipos de Items
####################################################
class TipoItemTable(TableBase):
	__model__ = TipoItem
	__omit_fields__ = ['atributos','items', 'fase']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

class TipoItemTableFiller(ExtendedTableFiller):
	__model__ = TipoItem
	__add_fields__ = {'accion':None}
	
	def accion (self, obj):
		html_widget = "<a href='/miproyecto/fase/tipo_item/atributos/list/##id##'>ver atributos</a>"
		accion = ', '.join([self.__action__.replace('##id##/edit','/miproyecto/fase/tipo_item/##id##/edit').
		replace('##id##', str(obj.id_tipo_item))+ html_widget.replace('##id##',  str(obj.id_tipo_item))])
		#replace('##editstate##', predicates.has_permission('editar_tipo_item'))])
		#accion = ', '.join()
		return accion.join(('<div>', '</div>'))

tipo_item_table = TipoItemTable(DBSession);
tipo_item_filler = TipoItemTableFiller(DBSession);

####################################################
# Widgets de los Participantes
####################################################
class ParticipantesTable(TableBase):
	__model__ = Rol
	__omit_fields__ = ['__actions__','permisos', 'created',
						'codigo','is_template']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}


class ParticipantesFiller(ExtendedTableFiller):
	__model__ = Rol
	__add_fields__ = {'accion':None}

	def accion (self, obj):

		html_widget = "<a href='/miproyecto/##id##/edit'>Asignar</a>"
		accion = ', '.join([html_widget.replace ('##id##', str(obj.rol_id))])
		return accion.join(('<div>', '</div>'))

participantes_table = ParticipantesTable(DBSession);
participantes_filler = ParticipantesFiller(DBSession);

####################################################
# Widgets de los atributos del tipo de item
####################################################

class AtributoTable(TableBase):
	__model__ = AtributoTipoItem
	__omit_fields__ = ['id_atributo_tipo_item', 'tipo_item_relacion', 'tipo_id', 'tipo_item']

class AtributoTableFiller(ExtendedTableFiller):
	__model__ = AtributoTipoItem

atributo_table = AtributoTable(DBSession);
atributo_filler = AtributoTableFiller(DBSession);

####################################################
# Widgets de las relaciones
####################################################

class RelacionTable(TableBase):
	__model__ = RelacionItem
	__omit_fields__ = ['__actions__']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	#__omit_fields__ = ['id_atributo_tipo_item', 'tipo_item_relacion', 'tipo_id', 'tipo_item']

class RelacionTableFiller(ExtendedTableFiller):
	__model__ = RelacionItem
	__add_fields__ = {'accion':None}


relacion_table = RelacionTable(DBSession);
relacion_filler = RelacionTableFiller(DBSession);

