
# -*- coding: utf-8 -*-
"""
Contien los modelos de las tablas correspondientes al proyecto SAP
"""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.dialects.postgresql import *

from sap.model import DeclarativeBase, metadata, DBSession

__all__ = ['Permiso']


class Permiso(DeclarativeBase):
	"""
	Representacion de la tabla permiso
	"""
	__tablename__ = 'permiso'
	
	id = Column ('id_permiso', INTEGER, primary_key=True)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	descripcion = Column ('descripcion', VARCHAR(100))


class Usuario(DeclarativeBase):
	"""
	Representacion de la tabla usuario
	"""
	__tablename__ = 'usuario'
	
	id = Column ('id_usuario', INTEGER, primary_key=True)
	
	username = Column ('username', VARCHAR(50), nullable=False)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	apellido = Column ('apellido', VARCHAR(50), nullable=False)
	
	nro_documento = Column ('nro_documento', VARCHAR(20), nullable=False)
	
	contrasenha = Column ('contrasenha', VARCHAR(100), nullable=False)
	
	mail = Column ('mail', VARCHAR(100))
	
	observacion = Column ('observacion', VARCHAR(200))
	
	estado = Column ('estado', VARCHAR(10))



class EstadoProyecto(DeclarativeBase):

	__tablename__ = 'estado_proyecto'
	
	id = Column ('id_estado_proyecto', INTEGER, primary_key=True)
	
	descripcion = Column ('descripcion', VARCHAR(200), nullable=False)
	
	observacion = Column ('observacion', VARCHAR(100))


class Proyecto(DeclarativeBase):
	
	__tablename__ = 'proyecto'
	
	id = Column ('id_proyecto', INTEGER, primary_key=True)
	
	lider = Column ('id_usuario_lider', INTEGER, 
					ForeignKey('usuario.id_usuario'))
	
	estado = Column ('id_estado_proyecto', INTEGER, 
					ForeignKey('estado_proyecto.id_estado_proyecto'))
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	nro_fases = Column ('nro_fases', INTEGER, nullable=False)
	
	descripcion = Column ('descripcion', VARCHAR(200))


class Fase(DeclarativeBase):
	
	__tablename__ = 'fase'
	
	id = Column ('id_fase', INTEGER, primary_key=True)
	
	proyecto = Column ('id_proyecto', INTEGER, 
						ForeignKey('proyecto.id_proyecto'), 
						nullable=False)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	descripcion = Column ('descripcion', VARCHAR(200))


class Rol(DeclarativeBase):
	
	__tablename__ = 'rol'
	
	id = Column ('id_rol', INTEGER, primary_key=True)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	descripcion = Column ('descripcion', VARCHAR(200))


class RolProyecto(DeclarativeBase):
	
	__tablename__ = 'rol_proyecto'
	
	id = Column ('id_rol', INTEGER,  ForeignKey('rol.id_rol'),
				primary_key=True)
	
	proyecto = Column ('id_proyecto', INTEGER,
				ForeignKey('proyecto.id_proyecto'),primary_key=True)


class RolPermiso (DeclarativeBase):
	
	__tablename__ = 'rol_permiso'
	
	id = Column ('id_permiso', INTEGER, 
					ForeignKey('permiso.id_permiso'), primary_key=True)
	
	rol = Column ('id_rol', INTEGER, ForeignKey('rol.id_rol'), 
					primary_key=True)


class RolUsuario(DeclarativeBase):
	
	__tablename__ = 'rol_usuario'
	
	id = Column ('id_usuario', INTEGER, 
					ForeignKey ('usuario.id_usuario'), primary_key=True)
	
	rol = Column ('id_rol', INTEGER, ForeignKey('rol.id_rol'),
					primary_key=True)


class RolFase (DeclarativeBase):
	
	__tablename__ = 'rol_fase'
	
	id = Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'), 
					primary_key=True)
	
	rol = Column ('id_rol', INTEGER,  ForeignKey('rol.id_rol'),
					primary_key=True)


class EstadoLineaBase(DeclarativeBase):
	
	__tablename__ = 'estado_linea_base'
	
	id = Column ('id_estado_linea_base',INTEGER, primary_key=True)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)


class LineaBase (DeclarativeBase):
	
	__tablename__ = 'linea_base'
	
	id = Column ('id_linea_base', INTEGER, primary_key=True)
	
	estado = Column ('id_estado_lineabase',INTEGER, 
				ForeignKey('estado_linea_base.id_estado_linea_base'))
	
	fase = Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'))


class TipoItem(DeclarativeBase) :
	
	__tablename__ = 'tipo_item'
	
	id = Column ('id_tipo_item', INTEGER, primary_key=True)
	
	fase = Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'))
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	descripcion = Column ('descripcion', VARCHAR(200))


class AtributoTipoItem(DeclarativeBase):
	
	__tablename__ = 'atributo_tipo_item'
	
	id = Column ('id_atributo_tipo_item', INTEGER, primary_key=True)
	
	tipo_item = Column ('id_tipo_item', INTEGER, 
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)
	
	tipo_atributo = Column ('tipo_atributo', VARCHAR(10))



class EstadoItem(DeclarativeBase):
	
	__tablename__ = 'estado_item'
	
	id = Column ('id_estado_item', INTEGER, primary_key=True)
	
	nombre = Column ('nombre', VARCHAR(50), nullable=False)


class Item(DeclarativeBase):
	
	__tablename__ = 'item'
	
	id = Column ('id_item', INTEGER, primary_key = True)
	
	estado = Column ('id_estado_item', INTEGER,
						ForeignKey('estado_item.id_estado_item'),
						nullable=False)
	
	tipo_item = Column ('id_tipo_item', INTEGER,
						ForeignKey ('tipo_item.id_tipo_item'),
						nullable=False)
	
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
								primary_key=True)
	
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

	id= Column ('id_recurso', INTEGER, primary_key = True)

	adjunto = Column ('adjunto', BYTEA, nullable = False)

	observacion = Column ('observacion', VARCHAR(100))
