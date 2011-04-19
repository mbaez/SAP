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

create_usuario_form = UsuarioForm("create_usuario_form", action='create_usuario')



