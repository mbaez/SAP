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
		Column('id_permiso', INTEGER, primary_key = True),
		Column ('nombre', VARCHAR(50), nullable=False),
		Column ('descripcion', VARCHAR(100))
)

usuario_table = Table( 'usuario', metadata,
		Column('id_usuario', INTEGER, primary_key = True),
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
		Column('id_estado_proyecto', INTEGER, primary_key = True),
		Column ('descripcion', VARCHAR(200), nullable=False),
		Column ('observacion', VARCHAR(100)
)

proyecto_table = ('proyecto', meadata, 
		Column('id_proyecto', INTEGER, primary_key = True),
		Column('id_usuario_lider', INTEGER, ForeignKey('usuario.id_usuario')),
		Column('id_estado_proyecto', INTEGER, ForeignKey('estado_proyecto.id_estado_proyecto')),
		Column('nombre', VARCHAR(50), nullable=False),
		Column('nro_fases', INTEGER, nullable =False),
		Column ('descripcion', VARCHAR(200))
)
# your model classes
# http://www.sqlalchemy.org/docs/05/ormtutorial.html#define-a-python-class-to-be-mapped

# class YourDataClass(object):
#     pass

class Permiso(object):
	pass

class Usuario(object):
	pass

class Estado_Proyecto(object):
	pass

class Proyecto(object):
	pass
# set up mappers between your data tables and classes
# http://www.sqlalchemy.org/docs/05/mappers.html

# mapper(YourDataClass, your_table)
mapper(Permiso, permiso_table)

mapper (Usuario, usuario_table)

mapper (Estado_Proyecto, estado_proyecto_table)

mapper (Proyecto, proyecto_table)

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

