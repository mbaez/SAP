
from sprox.widgets.dojo import SproxDojoSelectShuttleField
from sprox.widgetselector import SAWidgetSelector
from tw.dojo.selectshuttle import DojoSelectShuttleField
from sprox.widgets import PropertyMixin

from sprox.formbase import AddRecordForm
from sprox.formbase import EditableForm
from sprox.fillerbase import *
from sap.model import *

class ExtendedSelectShuttleField(DojoSelectShuttleField):
	template = "sap.templates.extended.selectshuttle"

class SproxExtendedSelectShuttleField(ExtendedSelectShuttleField, PropertyMixin):
	def update_params(self, d):
		self._my_update_params(d)
		super(SproxExtendedSelectShuttleField, self).update_params(d)


class ExtendedSAWidgetSelector (SAWidgetSelector):
	default_multiple_select_field_widget_type = SproxExtendedSelectShuttleField

class ExtendedAddRecordForm (AddRecordForm):
	__widget_selector_type__ = ExtendedSAWidgetSelector

class ExtendedEditableForm (EditableForm):
	__widget_selector_type__ = ExtendedSAWidgetSelector

'''
Esta clase sobreescirbe el metodo get_value para que este acepte
una lista de las entidades(entity_list) que se desean mostar
'''
class ExtendedTableFiller(TableFiller):
	'''
	Representa el codigo html que representa a los enlaces de eidtar y
	eliminar
	'''
	__action__ = 	"""
					<a style= '##editstate##;' href='##id##/edit'>editar</a>
					<div>
						<form  style= '##deletestate##;' method='POST'
								action='##id##' class='button-to'>
							<input type='hidden' name='_method'
								value='DELETE' ></input>
							<input class='delete-button'
								onclick="return confirm('Are you sure?');"
								value='eliminar' type='submit' ></input>
						</form>
					</div>
					"""

	'''
	Representa al usuario que se encuentra logeado en el sistema
	'''
	__possible_field_names__ = ['nombre','descripcion']

	def get_value(self,entity_list=None, values=None, **kw):
		if entity_list == None :
			objs = DBSession.query(self.__entity__).all()
			count = len(objs)
		else :
			count, objs = len(entity_list), entity_list

		self.__count__ = count
		rows = []

		for obj in objs:
			row = {}
			for field in self.__fields__:
				field_method = getattr(self, field, None)
				if inspect.ismethod(field_method):
					argspec = inspect.getargspec(field_method)
					if argspec and (len(argspec[0])-2>=len(kw) or argspec[2]):
						value = getattr(self, field)(obj, **kw)
					else:
						value = getattr(self, field)(obj)
				else:
					value = getattr(obj, field)
					if 'password' in field.lower():
						row[field] = '******'
						continue
					elif isinstance(value, list):
						value = self._get_list_data_value(field, value)
					elif self.__provider__.is_relation(self.__entity__, field) and value is not None:
						value = self._get_relation_value(field, value)
					elif self.__provider__.is_binary(self.__entity__, field) and value is not None:
						value = '<file>'
				row[field] = unicode(value)
			rows.append(row)
		return rows

from sprox.widgets import PropertySingleSelectField

class ExtendedItemDeFaseField(PropertySingleSelectField):

	idfase=0

	def _my_update_params(self, d, nullable=False):
		items = DBSession.query(Item).filter(Item.fase==self.idfase).all()
		options = [(item.id_item, '%s' %(item.id_item))
							for item in items]
		d['options']= options
		return d

class ExtendedItemDeFaseSiguienteField(PropertySingleSelectField):

	idfase=0

	def _my_update_params(self, d, nullable=False):
		items = DBSession.query(Item).filter(Item.fase==self.idfase).all()
		fase_actual = DBSession.query(Fase).get(self.idfase)
		proyectoid = fase_actual.proyecto
		fase_siguiente = DBSession.query(Fase).filter(Fase.id_fase>self.idfase).\
												filter(Fase.proyecto==proyectoid).\
												order_by(Fase.id_fase).\
												first() 
		items = items + DBSession.query(Item).filter(Item.fase==fase_siguiente.id_fase).all() 
		options = [(item.id_item, '%s' %(item.id_item))
							for item in items]
		d['options']= options
		return d

class ExtendedTipoItemField(PropertySingleSelectField):

	idfase=0

	def _my_update_params(self, d, nullable=False):
		tipo_items = DBSession.query(TipoItem).filter(TipoItem.fase==self.idfase).all()
		options = [(tipo_item.id_tipo_item, '%s' %(tipo_item.nombre))
							for tipo_item in tipo_items]
		d['options']= options
		return d

