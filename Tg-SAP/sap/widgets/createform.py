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

class NewRolForm(AddRecordForm):
	__model__ = Rol
	__omit_fields__ = ['id_rol']

class NewFaseForm(AddRecordForm):
	__model__ = Fase
	__omit_fields__ = ['id_fase']
	
class NewEstadoProyectoForm(AddRecordForm):
	__model__ = EstadoProyecto
	__omit_fields__ = ['id_estado_proyecto']
	__require_fields__ = ['nombre','descripcion']


new_usuario_form = NewUsuarioForm(DBSession)
new_proyecto_form = NewProyectoForm(DBSession)
new_rol_form = NewRolForm(DBSession)
new_fase_form = NewFaseForm(DBSession)
