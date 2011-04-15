# -*- coding: utf-8 -*-
"""This module contains the data model of the application."""


import pkg_resources
pkg_resources.require("SQLAlchemy>=0.4.3")

from turbogears.database import get_engine, metadata, session
# import the standard SQLAlchemy mapper
from sqlalchemy.orm import mapper
# To use the session-aware mapper use this import instead
# from turbogears.database import session_mapper as mapper
# import some basic SQLAlchemy classes for declaring the data model
# (see http://www.sqlalchemy.org/docs/05/ormtutorial.html)
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relation

# import the postgres datatypes for table columns for SQLALchemy
from sqlalchemy.dialects.postgresql import *

# your data tables
# http://www.sqlalchemy.org/docs/05/metadata.html

__author__ = "mbaez"

# your_table = Table('yourtable', metadata,
#     Column('my_id', Integer, primary_key=True)
# )

permiso_table = Table( 'permiso', metadata,
		Column ('id_permiso', INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable=False),
		Column ('descripcion', VARCHAR(100))
)

usuario_table = Table( 'usuario', metadata,
		Column ('id_usuario', INTEGER, primary_key = True),
		Column ('username', VARCHAR(50), nullable=False),
		Column ('nombre', VARCHAR(50), nullable=False),
		Column ('apellido', VARCHAR(50), nullable=False),
		Column ('nro_ci', VARCHAR(20), nullable=False),
		Column ('contrasenha', VARCHAR(100), nullable=False),
		Column ('mail', VARCHAR(100)),
		Column ('observacion', VARCHAR(200)),
		Column ('estado', VARCHAR(10))
)

estado_proyecto_table = Table('estado_proyecto', metadata,
		Column ('id_estado_proyecto', INTEGER, primary_key = True),
		Column ('descripcion', VARCHAR(200), nullable=False),
		Column ('observacion', VARCHAR(100))
)

proyecto_table = Table('proyecto', metadata, 
		Column ('id_proyecto', INTEGER, primary_key = True),
		Column ('id_usuario_lider', INTEGER, ForeignKey('usuario.id_usuario')),
		Column ('id_estado_proyecto', INTEGER, ForeignKey('estado_proyecto.id_estado_proyecto')),
		Column ('nombre', VARCHAR(50), nullable=False),
		Column ('nro_fases', INTEGER, nullable =False),
		Column ('descripcion', VARCHAR(200))
)

fase_table = Table( 'fase', metadata,
		Column ('id_fase', INTEGER, primary_key = True),
		Column ('id_proyecto', INTEGER, ForeignKey('proyecto.id_proyecto'), nullable = False),
		Column ('nombre', VARCHAR(50), nullable = False),
		Column ('descripcion', VARCHAR(200))
)

rol_table = Table('rol', metadata,
		Column ('id_rol', INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable = False),
		Column ('descripcion', VARCHAR(200))
)

rol_proyecto_table = Table ('rol_proyecto', metadata,
		Column ('id_rol', INTEGER,  ForeignKey('rol.id_rol'), primary_key = True),
		Column ('id_proyecto', INTEGER, ForeignKey('proyecto.id_proyecto'), primary_key = True)
)

rol_permiso_table = Table( 'rol_permiso', metadata,
		Column ('id_permiso', INTEGER, ForeignKey('permiso.id_permiso'), primary_key = True),
		Column ('id_rol', INTEGER, ForeignKey('rol.id_rol'), primary_key = True)
)

rol_usuario_table = Table( 'rol_usuario', metadata,
		Column ('id_usuario', INTEGER, ForeignKey ('usuario.id_usuario'), primary_key = True),
		Column ('id_rol', INTEGER, ForeignKey('rol.id_rol'), primary_key = True)
)

rol_fase_table = Table( 'rol_fase', metadata,
		Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'), primary_key = True),
		Column ('id_rol', INTEGER,  ForeignKey('rol.id_rol'), primary_key = True),
)

estado_linea_base_table = Table('estado_linea_base', metadata,
		Column ('id_estado_linea_base',INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable = False)
)

linea_base_table = Table('linea_base', metadata,
		Column ('id_linea_base', INTEGER, primary_key = True),
		Column ('id_estado_lineabase',INTEGER, ForeignKey('estado_linea_base.id_estado_linea_base')),
		Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase'))
)

tipo_item_table =  Table ('tipo_item', metadata,
		Column ('id_tipo_item', INTEGER, primary_key = True),
		Column ('id_fase', INTEGER, ForeignKey ('fase.id_fase')),
		Column ('nombre', VARCHAR(50), nullable = False),
		Column ('descripcion', VARCHAR(200))
)

atributo_tipo_item_table = Table ( 'atributo_tipo_item', metadata,
		Column ('id_atributo_tipo_item', INTEGER, primary_key = True),
		Column ('id_tipo_item', INTEGER, ForeignKey ('tipo_item.id_tipo_item'), nullable = False),
		Column ('nombre', VARCHAR(50), nullable = False),
		Column ('tipo_atributo', VARCHAR(10))
)

estado_item_table = Table('estado_item', metadata,
		Column ('id_estado_item', INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable = False)
)

item_table = Table( 'item', metadata,
		Column ('id_item', INTEGER, primary_key = True),
		Column ('id_estado_item', INTEGER, ForeignKey('estado_item.id_estado_item'), nullable = False),
		Column ('id_tipo_item', INTEGER, ForeignKey ('tipo_item.id_tipo_item'), nullable = False),
		Column ('id_fase', INTEGER, ForeignKey('fase.id_fase'), nullable = False),
		Column ('version', INTEGER, nullable = False),
		Column ('prioridad', INTEGER, nullable = False),
		Column ('complejidad', INTEGER, nullable = False),
		Column ('descripcion', VARCHAR(200)),
		Column ('observacion', VARCHAR(100))
)

linea_base_item_table = Table( 'linea_base_item', metadata,
		Column ('id_item', INTEGER, ForeignKey('item.id_item'), primary_key = True),
		Column ('id_linea_base', INTEGER, ForeignKey('linea_base.id_linea_base'), primary_key = True)
)

relacion_parentesco_table = Table('relacion_parentesco', metadata,
		Column ('id_relacion_parentesco', INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable = False),
		Column ('descripcion', VARCHAR(200)),
)

relacion_item_table = Table( 'relacion_item', metadata,
		Column ('id_item_actual', INTEGER, ForeignKey ('item.id_item'), primary_key = True),
		Column ('id_item_relacionado', INTEGER, ForeignKey ('item.id_item'), primary_key = True),
		Column ('id_relacion_parentesco', INTEGER, ForeignKey('relacion_parentesco.id_relacion_parentesco'), nullable = False)
)

recurso_table = Table( 'recurso', metadata,
		Column ('id_recurso', INTEGER, primary_key = True),
		Column ('adjunto', BYTEA, nullable = True),
		Column ('observacion', VARCHAR(100))
)

item_detalle_table = Table ('item_table', metadata,
		Column ('id_detalle', INTEGER, primary_key = True),
		Column ('id_item', INTEGER, ForeignKey('item.id_item')),
		Column ('id_recurso', INTEGER, ForeignKey('recurso.id_recurso'))
)

# your model classes
# http://www.sqlalchemy.org/docs/05/ormtutorial.html#define-a-python-class-to-be-mapped

# class YourDataClass(object):
#     pass

class Permiso(object):
	pass

class Usuario(object):
	pass

class EstadoProyecto(object):
	pass

class Proyecto(object):
	pass

class Rol(object):
	pass

class RolProyecto(object):
	pass

class RolUsuario(object):
	pass

class Fase (object):
	pass

class RolFase(object):
	pass

class EstadoLineaBase (object):
	pass

class LineaBase(object):
	pass

class TipoItem (object):
	pass

class AtributoTipoItem(object) :
	pass

class EstadoItem(object):
	pass

class Item(object):
	pass

class LineaBaseItem(object):
	pass

class RelacionParentesco(object):
	pass

class RelacionItem(object):
	pass

# set up mappers between your data tables and classes
# http://www.sqlalchemy.org/docs/05/mappers.html

# mapper(YourDataClass, your_table)
mapper (Permiso, permiso_table)

mapper (Usuario, usuario_table)

mapper (EstadoProyecto, estado_proyecto_table)

mapper (Proyecto, proyecto_table)

mapper (Rol, rol_table)

mapper (RolProyecto, rol_proyecto_table)

mapper (RolUsuario, rol_usuario_table)

mapper (Fase, fase_table)

mapper (RolFase, rol_fase_table)

mapper (EstadoLineaBase, estado_linea_base_table)

mapper (LineaBase, linea_base_table)

mapper (TipoItem, tipo_item_table)

mapper (AtributoTipoItem, atributo_tipo_item_table)

mapper (EstadoItem, estado_item_table)

mapper (Item, item_table)

mapper (LineaBaseItem, linea_base_item_table)

mapper (RelacionParentesco, relacion_parentesco_table)

mapper (RelacionItem, relacion_item_table)

# functions for populating the database
def bootstrap_model(clean=False):
    """Create all database tables and fill them with default data.

    This function is run by the 'bootstrap' function from the command module.
    By default it creates all database tables for your model.

    You can add more functions as you like to add more boostrap data to the
    database or enhance the function below.

    If 'clean' is True, all tables defined by your model will be dropped before
    creating them again.

    """
    create_tables(clean)

def create_tables(drop_all=False):
    """Create all tables defined in the model in the database.

    Optionally drop existing tables before creating them.

    """
    get_engine()
    if drop_all:
        print "Dropping all database tables defined in model."
        metadata.drop_all()
    metadata.create_all()

    print "All database tables defined in model created."

