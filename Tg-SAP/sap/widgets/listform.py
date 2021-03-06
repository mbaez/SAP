from sap.model import DBSession, metadata

from sprox.tablebase import TableBase
#from sprox.fillerbase import TableFiller
from sprox.fillerbase import *
from sap.controllers.checker import *

from sap.model import *
from sap.widgets.extended import ExtendedTableFiller
from sap.widgets.decorator import *

####################################################
# Widgets de los Usuarios
####################################################

class UsuarioTable(TableBase):
	__model__ = Usuario
	__omit_fields__ = ['_password','proyectos','password', 'roles', '__actions__' ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

usuario_table = UsuarioTable(DBSession);
usuario_filler = create_widget(UsuarioModelDecorator, EditActionDecorator, check_permiso=False)

####################################################
# Widgets de los Proyectos
####################################################
class ProyectoTable(TableBase):
	__model__ = Proyecto
	__omit_fields__ = ['lider_id','estado_id', '__actions__',  'roles_permisos']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

	def __init__(self, provider_hint=None, __omit_fields__=None ,**provider_hints):
		super(ProyectoTable, self).__init__(provider_hint, **provider_hints)

		if __omit_fields__ == None :
			return
		self.__omit_fields__ = __omit_fields__


proyecto_table = ProyectoTable(DBSession);
#Tabla de proyecto con las opciones de eliminar y editar
proyecto_filler = create_widget(ProyectoModelDecorator, EditActionDecorator, check_permiso=False)

#Crea la tabla de proyecto para el inicio
__admin_omit_fields__ = ['lider_id','estado_id', 'id_proyecto' ,
								  'nro_fases', '__actions__'  ]

admin_proyecto_table = ProyectoTable(DBSession,__admin_omit_fields__);
#Tabla de proyecto con la opcion de ver
admin_proyecto_filler = create_widget(ProyectoModelDecorator, VerActionDecorator, "/miproyecto/ver/")

####################################################
# Widgets de las Fases
####################################################
class FaseAdminTable(TableBase):
	__model__ = Fase
	__omit_fields__ = ['id_fase', '__actions__', 'items']
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}


fase_table = FaseAdminTable(DBSession);
#Tabla de fases con la opcion de ver
fase_filler = create_widget(FaseModelDecorator, VerActionDecorator)
####################################################
# Widgets de los Roles
####################################################
class RolTable(TableBase):
	__model__ = Rol
	__omit_fields__ = ['rol_id', 'permisos','usuarios','__actions__' ]
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}


rol_table = RolTable(DBSession);
rol_filler = create_widget(RolModelDecorator, EditActionDecorator, check_permiso=False)
####################################################
# Widgets de los Items
####################################################
class ItemTable(TableBase):
	__model__ = Item
	__omit_fields__ = ['tipo_item','fase','id_item','__actions__',
					   'id_linea_base','descripcion','detalles',
					   'tipo_item_relacion', 'linea_base',
					   'estado', 'relaciones','fase_actual', 'relaciones_id',
					   'archivos'
					  ]

	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

item_table = ItemTable(DBSession);
#Tabla de items com la opcion de eliminar y ediar.
item_filler = create_widget(ItemModelDecorator, VerActionDecorator,'/miproyecto/fase/item/ver/')

####################################################
# Widgets de los Tipos de Items
####################################################
class TipoItemTable(TableBase):
	__model__ = TipoItem
	__omit_fields__ = ['atributos','items',
						'id_tipo_item', 'fase','__actions__']

	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

tipo_item_table = TipoItemTable(DBSession);
#Crea el table filler de los tipos de items
tipo_item_filler = create_widget(TipoItemModelDecorator, LabelActionDecorator,
								params={'__label__':'Ver',
									'__extra_url__':'/new'})

####################################################
# Widgets de los Participantes
####################################################
class ParticipantesTable(TableBase):
	__model__ = Rol
	__omit_fields__ = ['__actions__','permisos', 'created', 'rol_id',
						'codigo','is_template']

	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}

participantes_table = ParticipantesTable(DBSession);
#Crea el table filler de los participantes por fase
participantes_fase_filler = create_widget(ParticipantesModelDecorator,
										  LabelActionDecorator
										 )

#Crea el table filler de los participantes por proyecto
participantes_filler = create_widget(ParticipantesModelDecorator,
									 LabelActionDecorator,
									 '/miproyecto/participantes/')

####################################################
# Widgets de los atributos del tipo de item
####################################################

class AtributoTable(TableBase):
	__model__ = AtributoTipoItem
	__omit_fields__ = ['id_atributo_tipo_item', 'tipo_item_relacion',
					   'tipo_id', 'tipo_item']

class AtributoTableFiller(ExtendedTableFiller):
	__model__ = AtributoTipoItem

atributo_table = AtributoTable(DBSession);
atributo_filler = AtributoTableFiller(DBSession);

####################################################
# Widgets de las relaciones
####################################################

class RelacionTable(TableBase):
	__model__ = RelacionItem
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	__omit_fields__ = ['__actions__','item_1', 'item_2']

class RelacionTableFiller(ExtendedTableFiller):
	__model__ = RelacionItem
	__add_fields__ = {'accion':None}


relacion_table = RelacionTable(DBSession);
relacion_filler = RelacionTableFiller(DBSession);

####################################################
# Widgets Lineas Base
####################################################
class LineaBaseTable(TableBase):
	__model__ = LineaBase
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	__omit_fields__ = ['__actions__','fase', 'id_linea_base', 'id_estado_linea_base']

linea_base_table = LineaBaseTable(DBSession);
#
linea_base_filler = create_widget(LineaBaseModelDecorator, LabelActionDecorator,
									'/miproyecto/fase/linea_base/abrir_linea_base/',
									params={'__label__':'Abrir','__extra_url__': ''})
####################################################
# Widgets del historial
####################################################

class HistorialTable(TableBase):
	__model__ = HistorialItem
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	__omit_fields__ = ['__actions__', 'fase', 'tipo_item', 'observacion',
						'id_historial_item', 'id_item', 'linea_base', 'relaciones',
						'detalles','estado']


historial_table = HistorialTable(DBSession);
historial_filler = create_widget(HistorialModelDecorator, LabelActionDecorator,
								params={'__label__':'revertir',
											'__extra_url__':''})

class HistorialRevivirTable(TableBase):
	__model__ = HistorialItem
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	__omit_fields__ = ['__actions__', 'fase', 'tipo_item', 'observacion',
						'id_historial_item', 'id_item', 'linea_base',
						'relaciones', 'detalles','estado']


historial_revivir_table = HistorialRevivirTable(DBSession);
historial_revivir_filler = create_widget(HistorialModelDecorator,
								LabelActionDecorator,
								'/miproyecto/fase/item/revivir/',
								params={'__label__':'revivir', '__extra_url__':''}
							)

####################################################
# Widgets de los detalles de los items
####################################################
class DetalleItemTable(TableBase):
	__model__ = DetalleItem
	__xml_fields__ = ['accion']
	__add_fields__ = {'accion':None}
	__omit_fields__ = ['__actions__','id_item_detalle','id_item', 'item',
					   'id_atributo_tipo_item'
					  ]

	__field_order__ = ['atributo_tipo_item', 'valor', 'observacion', 'accion']

	__headers__ = {'atributo_tipo_item':'Nombre',
					'valor':'Valor',
				  }

detalle_item_table = DetalleItemTable(DBSession)

detalle_item_filler = create_widget(DetalleItemModelDecorator,
							LabelActionDecorator,
							'/miproyecto/fase/item/item_detalle/',
							params={'__label__':'Editar',
								'__extra_url__':'/edit'})

class ReporteLineaBaseTable(TableBase):
	__model__ = Item
	__omit_fields__ = ['tipo_item','fase','id_item','__actions__',
					   'id_linea_base','descripcion','detalles',
					   'tipo_item_relacion',
					   'estado', 'relaciones','fase_actual', 'relaciones_id',
					   'archivos'
					  ]
class ReporteLineaBaseFiller(TableFiller) :
	__model__ = Item

linea_base_reporte = ReporteLineaBaseTable(DBSession)
linea_base_reporte_filler = create_widget(ItemModelDecorator, VerActionDecorator,'/miproyecto/fase/item/ver/')
