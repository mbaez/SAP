"""Create Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, TextField, TextArea, PasswordField, SubmitButton

from sprox.formbase import AddRecordForm
from sap.model import *

class NewUsuarioForm(AddRecordForm):
	__model__ = Usuario
	__omit_fields__ = ['id_usuario','proyectos']
	__require_fields__ = ['username','nombre','apellido','contrasenha']
	contrasenha = PasswordField

class NewProyectoForm(AddRecordForm):
	__model__ = Proyecto
	__omit_fields__ = ['id_proyecto','lider_id','estado_id']
	#__require_fields__ = ['username','nombre','apellido','contrasenha']

class NewRolForm(AddRecordForm):
	__model__ = Rol
	__omit_fields__ = ['id_rol']

new_usuario_form = NewUsuarioForm(DBSession)
new_proyecto_form = NewProyectoForm(DBSession)
new_rol_form = NewRolForm(DBSession)

