
from sap.model import *
from sap.widgets.extended import ExtendedEditableForm

from sprox.formbase import EditableForm
from sprox.fillerbase import EditFormFiller
from tw.forms import PasswordField, FileField

####################################################
# Widgets del Usuario
####################################################
class UsuarioEditFiller(EditFormFiller):
	__model__ = Usuario

usuario_edit_filler = UsuarioEditFiller(DBSession)

class UsuarioEditForm(EditableForm):
	__model__ = Usuario
	__omit_fields__ = ['proyectos','roles','created', '_password']
	__field_order__ = ['usuario_id','user_name','nombre','email_address',
					   'password']
	__field_attrs__ = {'nombre':{'rows':'2'},
					   'email_address':{'rows':'2'}}

	password = PasswordField
	

usuario_edit_form = UsuarioEditForm(DBSession)

####################################################
# Widgets del Proyecto
####################################################
class ProyectoEditFiller(EditFormFiller):
	__model__ = Proyecto

proyecto_edit_filler = ProyectoEditFiller(DBSession)

class ProyectoEditForm(EditableForm):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','lider','estado_id', 'permisos_proyectos','estado']

proyecto_edit_form = ProyectoEditForm(DBSession)

###################################################
# Widgets de los Roles
####################################################
class RolEditFiller(EditFormFiller):
	__model__ = Rol

rol_edit_filler = RolEditFiller(DBSession)

class RolEditForm(ExtendedEditableForm):
	__model__ = Rol
	__omit_fields__ = ['usuarios','permisos_poyectos']
	__dropdown_field_names__ = {'permisos':'nombre'}

rol_edit_form = RolEditForm(DBSession)

####################################################
# Widgets de las Fases
####################################################
class FaseEditFiller(EditFormFiller):
	__model__ = Fase

fase_edit_filler = RolEditFiller(DBSession)

class FaseEditForm(EditableForm):
	__model__ = Fase

fase_edit_form = RolEditForm(DBSession)

####################################################
# Widgets de los Items
####################################################
class TipoItemEditFiller(EditFormFiller):
	__model__ = TipoItem

tipo_item_edit_filler = TipoItemEditFiller(DBSession)

class TipoItemEditForm(ExtendedEditableForm):
	__model__ = TipoItem
	__omit_fields__ = ['atributos', 'items']

tipo_item_edit_form = TipoItemEditForm(DBSession)

####################################################
# Widgets de los Items
####################################################
class ItemEditFiller(EditFormFiller):
	__model__ = Item

item_edit_filler = ItemEditFiller(DBSession)

class ItemEditForm(ExtendedEditableForm):
	__model__ = Item
	__omit_fields__ = ['tipo_item_relacion','tipo_item', '__actions__',
					'id_item', 'fase', 'version','estado', 'linea_base',
					'estado_actual', 'id_linea_base' , 'detalles', 'relaciones_id',
					'relaciones']

item_edit_form = ItemEditForm(DBSession)

####################################################
# Widgets del RolUsuario
####################################################
class RolUsuarioEditFiller(EditFormFiller):
	__model__ = Rol

rol_usuario_edit_filler = RolUsuarioEditFiller(DBSession)

class RolUsuarioEditForm(ExtendedEditableForm):
	__model__ = Rol
	__omit_fields__ = [ 'permisos_poyectos','descripcion','permisos', 'created',
						 '_permisos','_proyectos','is_template', 'roles_permisos']

rol_usuario_edit_form = RolUsuarioEditForm(DBSession)

###################################################
# Widgets de los Roles
####################################################
class LineaBaseEditFiller(EditFormFiller):
	__model__ = LineaBase

linea_base_edit_filler = LineaBaseEditFiller(DBSession)

class LineaBaseEditForm(ExtendedEditableForm):
	__model__ = LineaBase

linea_base_edit_form = LineaBaseEditForm(DBSession)

###################################################
# Widgets de los Detalles de item
####################################################

class DetalleItemEditForm(EditableForm):
	__model__ = DetalleItem
	__omit_fields__ = ['id_item', 'id_atributo_tipo_item'
					   ,'atributo_tipo_item','item']

detalle_item_edit_form = DetalleItemEditForm(DBSession)

class DetalleItemEditFiller(EditFormFiller):
	__model__ = DetalleItem

detalle_item_edit_filler = DetalleItemEditFiller(DBSession)
