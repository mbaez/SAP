"""Create Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, TextField, TextArea, PasswordField, SubmitButton, Spacer,CheckBox
from sprox.formbase import AddRecordForm
from sap.model import *
from sprox.widgets import *
from sap.widgets.extended import *

from sap.controllers.util import *

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
	__omit_fields__ = ['id_proyecto','lider_id','estado_id','estado']
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
	__omit_fields__ = ['id_fase', 'proyecto', 'items']

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
class NewAtributoForm(ExtendedAddRecordForm):
	__model__ = AtributoTipoItem
	__omit_fields__ = ['id_atributo_tipo_item', 'tipo_item_relacion',
					   'tipo_id', 'tipo_item', 'detalle_item']
	__dropdown_field_names__ = {'tipo':'nombre'}

new_atributo_form = NewAtributoForm(DBSession)

####################################################
# Widgets de los Items
####################################################
class NewItemForm(ExtendedAddRecordForm):
	__model__ = Item
	__omit_fields__ = ['__actions__','id_item', 'tipo_item', 'fase', 'version',
					   'estado', 'linea_base', 'detalles', 'estado_actual',
					   'relaciones_id','id_linea_base', 'codigo', 'fase_actual',
					   'archivos']

	__dropdown_field_names__ = {'tipo_item_relacion':'nombre',
								'estado_actual':'nombre'}
	tipo_item_relacion = ExtendedTipoItemField
	relaciones = ExtendedItemDeFaseAnteriorField

	opciones_prioridad = ((1,"Muy Baja"),
						 (2,"Baja"),
						 (3,"Media"),
						 (4,"Alta"),
						 (5,"Muy alta"))

	prioridad = SingleSelectField('prioridad', options=opciones_prioridad)

	opciones_complejidad = ((1,"1"),
						 (2,"2"),
						 (3,"3"),
						 (4,"4"),
						 (5,"5"),
						 (6,"6"),
						 (7,"7"),
						 (8,"8"),
						 (9,"9"),
						 (10,"10"))

	complejidad = SingleSelectField('complejidad',options=opciones_complejidad)

new_item_form = NewItemForm(DBSession)

####################################################
# Widgets de los Participantes
####################################################
class NewParticipanteForm(ExtendedAddRecordForm):
	__model__ = Rol
	__omit_fields__ = ['__actions__','nombre','descripcion','permisos', 'created']

new_participante_form = NewParticipanteForm(DBSession)

class NewFaseParticipanteFrom(TableForm):
	fields = []

	submit_text = 'Guardar'

def add_usuarios_combobox(id):
		usuarios = usuario_util.get_usuarios_by_permiso(id)
		NewFaseParticipanteFrom.fields = []
		for usuario in usuarios :
			NewFaseParticipanteFrom.fields.append(CheckBox(usuario.nombre, value=True))


####################################################
# Widgets de las Relaciones
####################################################
class NewRelacionForm(ExtendedAddRecordForm):
	__model__ = RelacionItem
	__omit_fields__ = ['id_item_actual', 'id_item_relacionado', 'relacion_parentesco']
	__dropdown_field_names__ = {'item1':'id_item', 'item2':'id_item'}
	item_1 = ExtendedItemDeFaseField
	item_2 = ExtendedItemDeFaseSiguienteField

new_relacion_form = NewRelacionForm(DBSession)

from tw.forms.datagrid import DataGrid
from tw.forms.fields import CheckBox
####################################################
# Widgets para creacion de Lineas Base
####################################################
class NewLineaBaseForm(TableForm):
	fields = [
		TextField('cod_usuario', label_text='Codigo'),
		Spacer()]


	submit_text = 'Generar'

####################################################
# Widgets para creacion detalles de item
####################################################
class NewItemDetalleForm(TableForm):
	fields = []
	submit_text = 'Guardar'
