
from sap.model import *

from sprox.formbase import EditableForm
from sprox.fillerbase import EditFormFiller
from tw.forms import PasswordField

class UsuarioEditFiller(EditFormFiller):
	__model__ = Usuario

usuario_edit_filler = UsuarioEditFiller(DBSession)

class UsuarioEditForm(EditableForm):
	__model__ = Usuario
	__omit_fields__ = ['proyectos']
	contrasenha = PasswordField
	

usuario_edit_form = UsuarioEditForm(DBSession)

class ProyectoEditFiller(EditFormFiller):
	__model__ = Proyecto

proyecto_edit_filler = ProyectoEditFiller(DBSession)

class ProyectoEditForm(EditableForm):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id']
	
proyecto_edit_form = ProyectoEditForm(DBSession)

class RolEditFiller(EditFormFiller):
	__model__ = Rol

rol_edit_filler = RolEditFiller(DBSession)

class RolEditForm(EditableForm):
	__model__ = Rol
	
rol_edit_form = RolEditForm(DBSession)

class FaseEditFiller(EditFormFiller):
	__model__ = Fase

fase_edit_filler = RolEditFiller(DBSession)

class FaseEditForm(EditableForm):
	__model__ = Fase
	
fase_edit_form = RolEditForm(DBSession)
