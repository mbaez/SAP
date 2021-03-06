
# -*- coding: utf-8 -*-
"""
Contien los modelos de las tablas correspondientes al proyecto SAP
"""

from sqlalchemy import *
from sqlalchemy.orm import relation, mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Binary

from sap.model import DeclarativeBase, metadata, DBSession


class EstadoProyecto(DeclarativeBase):

	__tablename__ = 'estado_proyecto'

	#{ Columnas
	id_estado_proyecto = Column ('id_estado_proyecto', Integer,
								  autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), unique=True, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))
	#Metodos{

	def __str__(self):
		return '%s,%s,%s' % (self.id_estado_proyecto, self.nombre,
				self.descripcion)
	#}

class Proyecto(DeclarativeBase):

	__tablename__ = 'proyecto'

	#{ Columnas
	id_proyecto = Column ('id_proyecto', Integer, autoincrement=True,
							primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	nro_fases = Column ('nro_fases', Integer, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))
	#{ Relaciones

	#Se relaciona con una instnacia de una clase Usuario
	lider = relation ('Usuario', backref='proyectos')

	estado_id = Column ('id_estado_proyecto', Integer,
					ForeignKey('estado_proyecto.id_estado_proyecto'), default=1)

	lider_id = Column ('id_usuario_lider', Integer,
					ForeignKey('usuario.usuario_id'))
	"""
	Se relaciona con una instnacia de una clase EstadoProyecto
	"""
	estado = relation ('EstadoProyecto', backref='proyectos')

	#{ Metodos
	def __str__(self):
		return ' %s %s %s' % (self.nombre, self.nro_fases, self.descripcion)
	#}

class Fase(DeclarativeBase):

	__tablename__ = 'fase'

	#{Columnas
	id_fase = Column ('id_fase', Integer, autoincrement=True,
						primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))
	#{ Metodos
	proyecto = Column ('id_proyecto', Integer,
						ForeignKey('proyecto.id_proyecto'),
						nullable=False)
	#}

class EstadoLineaBase(DeclarativeBase):

	__tablename__ = 'estado_linea_base'

	#{Columnas
	id_estado_linea_base = Column ('id_estado_linea_base',Integer,
							autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)
	#}

class TipoItem(DeclarativeBase) :

	__tablename__ = 'tipo_item'

	#{Columnas
	id_tipo_item = Column ('id_tipo_item', Integer, autoincrement=True,
							primary_key=True)

	codigo = Column ('codigo', Unicode(50), nullable = False)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))
	#{ Metodos
	fase = Column ('id_fase', Integer, ForeignKey ('fase.id_fase'))
	#}

class AtributoTipoItem(DeclarativeBase):

	__tablename__ = 'atributo_tipo_item'

	#{Columnas
	id_atributo_tipo_item = Column ('id_atributo_tipo_item', Integer,
								autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	#{ForeignKey
	tipo_item = Column ('id_tipo_item', Integer,
						ForeignKey ('tipo_item.id_tipo_item'), nullable=False)

	tipo_id = Column ('tipo_atributo', Integer,
						ForeignKey ('tipo_atributo.id_tipo_atributo'),
						nullable=False)

	#{Relaciones
	tipo_item_relacion = relation('TipoItem', backref='atributos')

	tipo = relation('TipoAtributo', backref='atributos')
	#}


class EstadoItem(DeclarativeBase):

	__tablename__ = 'estado_item'

	#{Columnas
	id_estado_item = Column ('id_estado_item', Integer, autoincrement=True,
					primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)
	#}

class Item(DeclarativeBase):

	__tablename__ = 'item'

	#{Columnas
	id_item = Column ('id_item', Integer, autoincrement=True,
						primary_key = True)

	codigo = Column ('codigo', Unicode(50), unique = True, nullable = False)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	version = Column ('version', Integer, nullable=False)

	prioridad = Column ('prioridad', Integer, nullable=False)

	complejidad = Column ('complejidad', Integer, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))

	observacion = Column ('observacion', Unicode(100))

	#{ForeignKey
	id_linea_base = Column ('id_linea_base', Integer,
					ForeignKey('linea_base.id_linea_base'))

	tipo_item = Column ('id_tipo_item', Integer,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)

	fase = Column ('id_fase', Integer, ForeignKey('fase.id_fase'),
					nullable=False)

	estado = Column ('id_estado_item', Integer,
						ForeignKey('estado_item.id_estado_item'),
						nullable=False)

	relaciones_id = Column ('id_item_relacion', Integer,
						ForeignKey('item.id_item'),
						nullable=True)
	#{Relaciones
	tipo_item_relacion = relation('TipoItem', backref='items')

	estado_actual = relation('EstadoItem', backref='items')

	detalles = relation ('DetalleItem', backref='item')

	archivos = relation ('Archivo', backref='item')

	relaciones = relation('Item')

	fase_actual = relation ('Fase', backref = 'items')
	#}
	"""
	relacion = relation('RelacionItem', primaryjoin = and_(relacion == Item.id,\
	 version_item_1 == Item.version), backref = backref('relaciones_a', cascade="all,delete,delete-orphan"))
    """

class RelacionParentesco(DeclarativeBase):

	__tablename__ = 'relacion_parentesco'
	#{Columnas
	relacion_parentesco = Column ('id_relacion_parentesco', Integer,
								autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))
	#}

class RelacionItem(DeclarativeBase):

	__tablename__ ='relacion_item'
	#{Columnas
	id_item_actual = Column ('id_item_actual', Integer, ForeignKey ('item.id_item'),
				primary_key=True)

	id_item_relacionado = Column ('id_item_relacionado', Integer,
				ForeignKey ('item.id_item'), primary_key=True)


	relacion_parentesco = Column ('id_relacion_parentesco', Integer,
				ForeignKey('relacion_parentesco.id_relacion_parentesco'),
				nullable=False)
	#relaciones ficticias a la tabla parentesco.
	#Puse solo para que anden los combobox
	item_1=relation('RelacionParentesco')
	item_2=relation('RelacionParentesco')
	#}

class TipoAtributo(DeclarativeBase):

	__tablename__ = 'tipo_atributo'
	#{Columnas
	id_tipo_atributo = Column('id_tipo_atributo', Integer, autoincrement=True, primary_key=True)

	nombre = Column('nombre', Unicode(100))

	descripcion = Column('descripcion', Unicode(200))

	def __str__(self):
		return '%s' % (self.nombre)

	def __unicode__(self):
		return self.nombre or self.descripcion
	#}

class Archivo(DeclarativeBase):

	__tablename__ = 'archivo'

	#{Columnas
	id_archivo = Column ('id_archivo', Integer, autoincrement=True,
								primary_key=True)

	archivo = Column ('archivo', Binary)

	file_name = Column (Unicode(100))

	content_type = Column (Unicode(100))
	#{ForeignKey

	id_item = Column ('id_item', Integer, ForeignKey ('item.id_item'))

	#}

class DetalleItem(DeclarativeBase):

	__tablename__ = 'detalle_item'

	#{Columnas
	id_item_detalle = Column ('id_item_detalle', Integer, autoincrement=True,
								primary_key=True)

	valor = Column('valor', Unicode(200))

	observacion = Column ('observacion', Unicode(100))

	#{ForeignKey
	id_item = Column ('id_item', Integer, ForeignKey ('item.id_item'))

	id_atributo_tipo_item = Column( 'id_atributo_tipo_item', Integer,
							ForeignKey ('atributo_tipo_item.id_atributo_tipo_item'),
							nullable=False)

	#{Relation

	atributo_tipo_item = relation (AtributoTipoItem, backref='detalle_item')

	#}

class LineaBase (DeclarativeBase):

	__tablename__ = 'linea_base'

	id_linea_base = Column ('id_linea_base', Integer, autoincrement=True,
								primary_key=True)

	codigo = Column ('codigo', Unicode(50), unique = True, nullable = False)

	id_estado_linea_base = Column ('id_estado_lineabase',Integer,
				ForeignKey('estado_linea_base.id_estado_linea_base'))

	fase = Column ('id_fase', Integer, ForeignKey ('fase.id_fase'))

	items = relation(Item, backref='linea_base')

	estado = relation(EstadoLineaBase, backref='linea_base')


###############################################################################
# Tablas de historial/auditoria
###############################################################################

class HistorialItem(DeclarativeBase):

	__tablename__ = 'historial_item'

	id_historial_item = Column ('id_historial_item', Integer, autoincrement=True,
						primary_key = True)

	id_item = Column ('id_item', Integer, nullable=False)

	codigo = Column ('codigo', Unicode(50),nullable=False)

	nombre = Column ('nombre', Unicode(200))

	estado = Column ('id_estado_item', Integer, ForeignKey ('estado_item.id_estado_item'),
										nullable=False)

	estado_historial = relation('EstadoItem')

	tipo_item = Column ('id_tipo_item', Integer, nullable=False)

	id_linea_base = Column ('id_linea_base', Integer)

	fase = Column ('id_fase', Integer, nullable=False)

	version = Column ('version', Integer, nullable=False)

	prioridad = Column ('prioridad', Integer, nullable=False)

	complejidad = Column ('complejidad', Integer, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))

	observacion = Column ('observacion', Unicode(100))


class HistorialDetalleItem(DeclarativeBase):
	__tablename__ = 'historial_detalle_item'

	id_historial_detalle = Column ('id_historial_detalle', Integer,
							autoincrement=True, primary_key = True)

	id_historial = Column ('id_historial_item', Integer,
				ForeignKey('historial_item.id_historial_item'))

	item = relation("HistorialItem", backref="detalles")

	id_detalle = Column ('id_detalle', Integer, nullable=False)

	id_item = Column ('id_item', Integer, nullable=False)


	observacion = Column ('observacion', Unicode(100))

	valor = Column('valor', Unicode(200))

	id_atributo_tipo_item = Column('id_atributo_tipo_item', Integer, nullable=False)

class HistorialRelacion(DeclarativeBase):
	__tablename__ = 'historial_relacion'

	id_historial_relacion = Column ('id_historial_relacion', Integer,
							autoincrement=True, primary_key = True)

	id_historial = Column ('id_historial_item', Integer,
				ForeignKey('historial_item.id_historial_item'))

	items = relation("HistorialItem", backref="relaciones")

	id_item_1 = Column ('id_item_1', Integer, nullable=False)

	id_item_2 = Column ('id_item_2', Integer, nullable=False)

	id_tipo_relacion = Column ('id_tipo_relacion', Integer, nullable=False)


class HistorialArchivo(DeclarativeBase):

	__tablename__ = 'historial_archivo'

	#{Columnas
	id_historial_archivo = Column ('id_historial_archivo', Integer,
							autoincrement=True, primary_key=True)

	archivo = Column ('archivo', Binary)

	file_name = Column (Unicode(100))

	content_type = Column (Unicode(100))

	#{Relaciones
	id_item = Column ('id_item', Integer)

	id_historial = Column ('id_historial_item', Integer,
				ForeignKey('historial_item.id_historial_item'))

	historial_item = relation("HistorialItem", backref="archivos")

	#}
