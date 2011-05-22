"""Create Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, TextField, TextArea, PasswordField, SubmitButton
from sprox.formbase import AddRecordForm
from sap.model import *
from sprox.widgets import *
from sap.widgets.extended import *
##Form definition

####################################################
# Widgets de los Usuarios
####################################################
class NewUsuarioForm(AddRecordForm):
	__model__ = Usuario
	__omit_fields__ = ['roles','proyectos']
	__field_order__ = ['usuario_id','user_name','nombre','email_address','password','_password']
	__field_attrs__ = {'nombre':{'rows':'2'}, 'email_address':{'rows':'2'}}
	password = PasswordField
	password.label_text = 'Constrasena'

new_usuario_form = NewUsuarioForm(DBSession)

####################################################
# Widgets de los Proyectos
####################################################
class NewProyectoForm(AddRecordForm):
	__model__ = Proyecto
	__omit_fields__ = ['id_proyecto','lider_id','estado_id']
	__dropdown_field_names__ = {'estado':'nombre'}

new_proyecto_form = NewProyectoForm(DBSession)
####################################################
# Widgets de los Roles
####################################################
class NewRolForm(ExtendedAddRecordForm):
	__model__ = Rol
	__omit_fields__ = ['rol_id','usuarios']
	__dropdown_field_names__ = {'permisos':'nombre'}

new_rol_form = NewRolForm(DBSession)
####################################################
# Widgets de las Fases
####################################################
class NewFaseForm(AddRecordForm):
	__model__ = Fase
	__omit_fields__ = ['id_fase', 'proyecto']

new_fase_form = NewFaseForm(DBSession)

####################################################
# Widgets de los Items
####################################################
class NewTipoItemForm(ExtendedAddRecordForm):
	__model__ = TipoItem
	__omit_fields__ = ['id_tipo_item', 'fase', 'atributos', 'items']

new_tipo_item_form = NewTipoItemForm(DBSession)

####################################################
# Widgets de los Items
####################################################
class NewItemForm(ExtendedAddRecordForm):
	__model__ = Item
	__omit_fields__ = ['id_item', 'tipo_item', 'fase']
	__dropdown_field_names__ = {'tipo_item_relacion':'nombre'}
	tipo_item_relacion = ExtendedTipoItemField

new_item_form = NewItemForm(DBSession)
####################################################
# Widgets de los Participantes
####################################################
class NewParticipanteForm(ExtendedAddRecordForm):
	__model__ = Rol
	__omit_fields__ = ['__actions__','nombre','descripcion','permisos', 'created']

new_participante_form = NewParticipanteForm(DBSession)
