
# -*- coding: utf-8 -*-
"""
Contien los modelos de las tablas correspondientes al proyecto SAP
"""

from sqlalchemy import *
from sqlalchemy.orm import relation, synonym, mapper
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.dialects.postgresql import *

from sap.model import DeclarativeBase, metadata, DBSession

#__all__ = ['Permiso', 'Usuario', 'Proyecto','EstadoProyecto', 'Fase', 'Rol','LineaBase', 'TipoItem', 'Item']


class EstadoProyecto(DeclarativeBase):

	__tablename__ = 'estado_proyecto'

	id_estado_proyecto = Column ('id_estado_proyecto', Integer,
								  autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), unique=True, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))

	def __str__(self):
		return '%s,%s,%s' % (self.id_estado_proyecto, self.nombre,
				self.descripcion)


class Proyecto(DeclarativeBase):

	__tablename__ = 'proyecto'

	id_proyecto = Column ('id_proyecto', Integer, autoincrement=True,
							primary_key=True)

	lider_id = Column ('id_usuario_lider', Integer,
					ForeignKey('usuario.usuario_id'))
	"""
	Se relaciona con una instnacia de una clase Usuario
	"""
	lider = relation ('Usuario', backref='proyectos')

	estado_id = Column ('id_estado_proyecto', Integer,
					ForeignKey('estado_proyecto.id_estado_proyecto'))
	"""
	Se relaciona con una instnacia de una clase EstadoProyecto
	"""
	estado = relation ('EstadoProyecto', backref='proyectos')

	nombre = Column ('nombre', Unicode(50), nullable=False)

	nro_fases = Column ('nro_fases', Integer, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))


	def __str__(self):
		return ' %s %s %s' % (self.nombre, self.nro_fases, self.descripcion)


class Fase(DeclarativeBase):

	__tablename__ = 'fase'

	id_fase = Column ('id_fase', Integer, autoincrement=True,
						primary_key=True)

	proyecto = Column ('id_proyecto', Integer,
						ForeignKey('proyecto.id_proyecto'),
						nullable=False)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))


class EstadoLineaBase(DeclarativeBase):

	__tablename__ = 'estado_linea_base'

	id_estado_linea_base = Column ('id_estado_linea_base',Integer, autoincrement=True,
					primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)


class TipoItem(DeclarativeBase) :

	__tablename__ = 'tipo_item'

	id_tipo_item = Column ('id_tipo_item', Integer, autoincrement=True,
							primary_key=True)

	codigo = Column ('codigo', Unicode(50), unique = True, nullable = False)

	fase = Column ('id_fase', Integer, ForeignKey ('fase.id_fase'))

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))



class AtributoTipoItem(DeclarativeBase):

	__tablename__ = 'atributo_tipo_item'

	id_atributo_tipo_item = Column ('id_atributo_tipo_item', Integer, autoincrement=True,
					primary_key=True)

	tipo_item = Column ('id_tipo_item', Integer,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)

	tipo_item_relacion = relation('TipoItem', backref='atributos')

	nombre = Column ('nombre', Unicode(50), nullable=False)

	tipo_id = Column ('tipo_atributo', Integer,
						ForeignKey ('tipo_atributo.id_tipo_atributo'),
						nullable=False)

	tipo = relation('TipoAtributo', backref='atributos')



class EstadoItem(DeclarativeBase):

	__tablename__ = 'estado_item'

	id_estado_item = Column ('id_estado_item', Integer, autoincrement=True,
					primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)


class Item(DeclarativeBase):

	__tablename__ = 'item'

	id_item = Column ('id_item', Integer, autoincrement=True,
						primary_key = True)

	estado = Column ('id_estado_item', Integer,
						ForeignKey('estado_item.id_estado_item'),
						nullable=False)

	estado_actual = relation('EstadoItem', backref = 'items')

	codigo = Column ('codigo', Unicode(50), unique = True, nullable = False)

	nombre = Column ('nombre', Unicode(50))

	tipo_item = Column ('id_tipo_item', Integer,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)

	tipo_item_relacion = relation('TipoItem', backref='items')

	fase = Column ('id_fase', Integer, ForeignKey('fase.id_fase'),
					nullable=False)

	version = Column ('version', Integer, nullable=False)

	prioridad = Column ('prioridad', Integer, nullable=False)

	complejidad = Column ('complejidad', Integer, nullable=False)

	descripcion = Column ('descripcion', Unicode(200))

	id_linea_base = Column ('id_linea_base', Integer,
					ForeignKey('linea_base.id_linea_base'))

	observacion = Column ('observacion', Unicode(100))
	detalles = relation ('DetalleItem', backref = 'item')


class RelacionParentesco(DeclarativeBase):

	__tablename__ = 'relacion_parentesco'

	relacion_parentesco = Column ('id_relacion_parentesco', Integer,
								autoincrement=True, primary_key=True)

	nombre = Column ('nombre', Unicode(50), nullable=False)

	descripcion = Column ('descripcion', Unicode(200))


class RelacionItem(DeclarativeBase):

	__tablename__ ='relacion_item'

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

class Recurso(DeclarativeBase):

	__tablename__ = 'recurso'

	id= Column ('id_recurso', Integer, autoincrement=True,
				primary_key = True)

	adjunto = Column ('adjunto', Binary, nullable = False)
	
	observacion = Column ('observacion', Unicode(100))

class TipoAtributo(DeclarativeBase):

	__tablename__ = 'tipo_atributo'

	id_tipo_atributo = Column('id_tipo_atributo', Integer, autoincrement=True, primary_key=True)

	nombre = Column('nombre', Unicode(100))

	descripcion = Column('descripcion', Unicode(200))

	def __str__(self):
		return '%s' % (self.nombre)

	def __unicode__(self):
		return self.nombre or self.descripcion


class DetalleItem(DeclarativeBase):

	__tablename__ = 'detalle_item'

	id_item = Column ('id_item', Integer, ForeignKey ('item.id_item'),
				primary_key=True)

	id_item_detalle = Column ('id_item_detalle', Integer,
				autoincrement=True, primary_key=True)

	recurso = Column ('id_recurso', Integer,
				ForeignKey('recurso.id_recurso'), nullable=False)

	valor = Column('valor', Unicode(200))

class LineaBase (DeclarativeBase):

	__tablename__ = 'linea_base'

	id_linea_base = Column ('id_linea_base', Integer, autoincrement=True,
								primary_key=True)

	codigo = Column ('codigo', Unicode(50), unique = True, nullable = False)

	estado = Column ('id_estado_lineabase',Integer,
				ForeignKey('estado_linea_base.id_estado_linea_base'))

	fase = Column ('id_fase', Integer, ForeignKey ('fase.id_fase'))

	items = relation(Item, backref='linea_base')


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

	linea_base = Column ('id_linea', Integer)

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

	recurso = Column ('id_recurso', Integer)

	valor = Column('valor', Unicode(200))

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
