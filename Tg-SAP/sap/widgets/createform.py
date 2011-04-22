"""Create Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea

class UsuarioForm(TableForm):

	class fields(WidgetsList):
		username = TextField()
		nombre = TextField()
		apellido = TextField()
		contrasenha = TextField(label_text='Contrasenha')
		mail = TextField()
		estado = TextField()
		descripcion = TextArea()

class ProyectoForm(TableForm):
	class fields(WidgetsList):
		nombre = TextField()
		lider = TextField()
		estado = TextField()
		nro_fases = TextField(label_text='Numero de Fases')
		descripcion = TextArea()
			
create_usuario_form = UsuarioForm("create_usuario_form", action='create_usuario')

create_proyecto_form = ProyectoForm("create_proyecto_form", action='create_proyecto')



