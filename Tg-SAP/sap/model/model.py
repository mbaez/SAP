
# -*- coding: utf-8 -*-
"""
Contien los modelos de las tablas correspondientes al proyecto SAP
"""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.dialects.postgresql import *

from sap.model import DeclarativeBase, metadata, DBSession

#__all__ = ['Permiso', 'Usuario', 'Proyecto','EstadoProyecto', 'Fase', 'Rol','LineaBase', 'TipoItem', 'Item']


class EstadoProyecto(DeclarativeBase):

	__tablename__ = 'estado_proyecto'

	id_estado_proyecto = Column ('id_estado_proyecto', INTEGER,
								  autoincrement=True, primary_key=True)

	nombre = Column ('nombre', VARCHAR(50), unique=True, nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))

	def __str__(self):
		return '%s,%s,%s' % (self.id_estado_proyecto, self.nombre,
				self.descripcion)


class Proyecto(DeclarativeBase):

	__tablename__ = 'proyecto'

	id_proyecto = Column ('id_proyecto', INTEGER, autoincrement=True,
							primary_key=True)

	lider_id = Column ('id_usuario_lider', INTEGER,
					ForeignKey('usuario.usuario_id'))
	"""
	Se relaciona con una instnacia de una clase Usuario
	"""
	lider = relation ('Usuario', backref='proyectos')

	estado_id = Column ('id_estado_proyecto', INTEGER,
					ForeignKey('estado_proyecto.id_estado_proyecto'))
	"""
	Se relaciona con una instnacia de una clase EstadoProyecto
	"""
	estado = relation ('EstadoProyecto', backref='proyectos')

	nombre = Column ('nombre', VARCHAR(50), nullable=False)

	nro_fases = Column ('nro_fases', INTEGER, nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))

	def __str__(self):
		return ' %s %s %s' % (self.nombre, self.nro_fases, self.descripcion)


class Fase(DeclarativeBase):

	__tablename__ = 'fase'

	id_fase = Column ('id_fase', INTEGER, autoincrement=True,
						primary_key=True)

	proyecto = Column ('id_proyecto', INTEGER,
						ForeignKey('proyecto.id_proyecto'),
						nullable=False)

	nombre = Column ('nombre', VARCHAR(50), nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))


class EstadoLineaBase(DeclarativeBase):

	__tablename__ = 'estado_linea_base'

	id = Column ('id_estado_linea_base',INTEGER, autoincrement=True,
					primary_key=True)

	nombre = Column ('nombre', VARCHAR(50), nullable=False)


class LineaBase (DeclarativeBase):

	__tablename__ = 'linea_base'

	id_linea_base = Column ('id_linea_base', INTEGER, autoincrement=True,
								primary_key=True)

	estado = Column ('id_estado_lineabase',INTEGER,
				ForeignKey('estado_linea_base.id_estado_linea_base'))

	fase = Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'))


class TipoItem(DeclarativeBase) :

	__tablename__ = 'tipo_item'

	id_tipo_item = Column ('id_tipo_item', INTEGER, autoincrement=True,
							primary_key=True)

	fase = Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'))

	nombre = Column ('nombre', VARCHAR(50), nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))


class AtributoTipoItem(DeclarativeBase):

	__tablename__ = 'atributo_tipo_item'

	id = Column ('id_atributo_tipo_item', INTEGER, autoincrement=True,
					primary_key=True)

	tipo_item = Column ('id_tipo_item', INTEGER,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)

	nombre = Column ('nombre', VARCHAR(50), nullable=False)

	tipo_atributo = Column ('tipo_atributo', VARCHAR(10))



class EstadoItem(DeclarativeBase):

	__tablename__ = 'estado_item'

	id = Column ('id_estado_item', INTEGER, autoincrement=True,
					primary_key=True)

	nombre = Column ('nombre', VARCHAR(50), nullable=False)


class Item(DeclarativeBase):

	__tablename__ = 'item'

	id_item = Column ('id_item', INTEGER, autoincrement=True,
						primary_key = True)

	estado = Column ('id_estado_item', INTEGER,
						ForeignKey('estado_item.id_estado_item'),
						nullable=False)

	tipo_item = Column ('id_tipo_item', INTEGER,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)

	tipo_item_relacion = relation('TipoItem', backref='items')

	fase = Column ('id_fase', INTEGER, ForeignKey('fase.id_fase'),
					nullable=False)

	version = Column ('version', INTEGER, nullable=False)

	prioridad = Column ('prioridad', INTEGER, nullable=False)

	complejidad = Column ('complejidad', INTEGER, nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))

	observacion = Column ('observacion', VARCHAR(100))


class LineaBaseItem(DeclarativeBase):

	__tablename__ = 'linea_base_item'

	id = Column ('id_item', INTEGER,
				ForeignKey('item.id_item'), primary_key=True)

	linea_base = Column ('id_linea_base', INTEGER,
						ForeignKey('linea_base.id_linea_base'),
						primary_key=True)


class RelacionParentesco(DeclarativeBase):

	__tablename__ = 'relacion_parentesco'

	relacion_parentesco = Column ('id_relacion_parentesco', INTEGER,
								autoincrement=True, primary_key=True)

	nombre = Column ('nombre', VARCHAR(50), nullable=False)

	descripcion = Column ('descripcion', VARCHAR(200))


class RelacionItem(DeclarativeBase):

	__tablename__ ='relacion_item'

	id = Column ('id_item_actual', INTEGER, ForeignKey ('item.id_item'),
				primary_key=True)

	item_realcionado = Column ('id_item_relacionado', INTEGER,
				ForeignKey ('item.id_item'), primary_key=True)

	relacion_parentesco = Column ('id_relacion_parentesco', INTEGER,
				ForeignKey('relacion_parentesco.id_relacion_parentesco'),
				nullable=False)



class Recurso(DeclarativeBase):

	__tablename__ = 'recurso'

	id= Column ('id_recurso', INTEGER, autoincrement=True,
				primary_key = True)

	adjunto = Column ('adjunto', BYTEA, nullable = False)

	observacion = Column ('observacion', VARCHAR(100))


class TipoAtributo(DeclarativeBase):

	__tablename__ = 'tipo_atributo'

	id_tipo_atributo = Column('id_tipo_atributo', INTEGER, autoincrement=True, primary_key=True)

	nombre = Column('nombre', VARCHAR(100))

	descripcion = Column('descripcion', VARCHAR(200))

	def __str__(self):
		return '%s' % (self.nombre)

	def __unicode__(self):
		return self.nombre or self.descripcion


class DetalleItem(DeclarativeBase):
	__tablename__ = 'detalle_item'

	id_item = Column ('id_item', INTEGER, ForeignKey ('item.id_item'),
				primary_key=True)

	id = Column ('id_item_detalle', INTEGER,
				autoincrement=True, primary_key=True)

	recurso = Column ('id_recurso', INTEGER,
				ForeignKey('recurso.id_recurso'), nullable=False)

	valor = Column('valor', VARCHAR(200))
