# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the Tg-SAP application,
though.

"""
import os
from datetime import datetime
import sys
try:
	from hashlib import sha1
except ImportError:
	sys.exit('ImportError: No module named hashlib\n'
			 'If you are on python2.4 this library is not part of python. '
			 'Please install it. Example: easy_install hashlib')

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relation, synonym, mapper

from sap.model import DeclarativeBase, metadata, DBSession, model

__all__ = ['Usuario', 'Rol', 'Permiso', 'RolPermisoProyecto', 'UsuarioPermisoFase','RolUsuario', 'RolPermiso']


#{ Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
rol_permiso_table = Table('rol_permiso', metadata,
	Column('rol_id', Integer, ForeignKey('rol.rol_id',
		onupdate="CASCADE", ondelete="CASCADE"),primary_key=True),

	Column('permiso_id', Integer, ForeignKey('permiso.permiso_id',
		onupdate="CASCADE", ondelete="CASCADE"),primary_key=True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
usuario_rol_table = Table('usuario_rol', metadata,
	Column('usuario_id', Integer, ForeignKey('usuario.usuario_id',
			onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
	Column('rol_id', Integer, ForeignKey('rol.rol_id',
			onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

#Relaciona a un rol y sus permisos a un proyecto
#
rol_permiso_proyecto_table = Table( 'rol_permiso_proyecto', metadata,

	Column('rol_id', Integer, ForeignKey('rol.rol_id',
		onupdate="CASCADE", ondelete="CASCADE"),primary_key=True),

	Column('permiso_id', Integer, ForeignKey('permiso.permiso_id',
		onupdate="CASCADE", ondelete="CASCADE"),primary_key=True),

	Column ('proyecto_id', Integer,ForeignKey('proyecto.id_proyecto',
			onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

usuario_permiso_fase_table = Table( 'rol_permiso_fase', metadata,

	Column('usuario_id', Integer, ForeignKey('usuario.usuario_id',
			onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),

	Column('permiso_id', Integer, ForeignKey('permiso.permiso_id',
		onupdate="CASCADE", ondelete="CASCADE"),primary_key=True),

	Column ('fase_id', Integer,ForeignKey('fase.id_fase',
			onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

class RolUsuario(object):
	pass

class RolPermiso(object):
	pass

class RolPermisoProyecto(object):
	pass

class UsuarioPermisoFase(object):
	pass

mapper(RolPermisoProyecto, rol_permiso_proyecto_table)

mapper(RolUsuario, usuario_rol_table)

mapper(RolPermiso , rol_permiso_table)

mapper(UsuarioPermisoFase, usuario_permiso_fase_table)
#} Association tables

#{ The auth* model itself


class Rol(DeclarativeBase):
	"""
	Rol definition for :mod:`repoze.what`.
	Only the ``group_name`` column is required by :mod:`repoze.what`.
	"""

	__tablename__ = 'rol'

	#{ Columns

	rol_id = Column(Integer, autoincrement=True, primary_key=True)

	codigo = Column(Unicode(16), unique=True, nullable=False)

	nombre = Column(Unicode(50), nullable=False)

	descripcion = Column(Unicode(255))

	created = Column(DateTime, default=datetime.now)

	is_template = Column (Boolean, default = False)

	#{ Relations

	usuarios = relation('Usuario', secondary=usuario_rol_table, backref='roles')

	#{ Special methods

	def __repr__(self):
		return '<Rol: name=%s>' % self.nombre

	def __unicode__(self):
		return self.nombre

	#}


# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class Usuario(DeclarativeBase):
	"""
	Usuario definition.

	This is the user definition used by :mod:`repoze.who`, which requires at
	least the ``user_name`` column.

	"""
	__tablename__ = 'usuario'

	#{ Columns

	usuario_id = Column(Integer, autoincrement=True, primary_key=True)

	user_name = Column(Unicode(16), unique=True, nullable=False)

	email_address = Column(Unicode(255), unique=True, nullable=False,
						   info={'rum': {'field':'Email'}})

	nombre = Column(Unicode(255))

	_password = Column('password', Unicode(80),
					   info={'rum': {'field':'Password'}})

	created = Column(DateTime, default=datetime.now)

	#{ Special methods

	def __repr__(self):
		return '<Usuario: email="%s", nombre="%s">' % (
				self.email_address, self.nombre)

	def __unicode__(self):
		return self.nombre or self.user_name

	#{ Getters and setters

	@property
	def permissions(self):
		"""Return a set of strings for the permissions granted."""
		perms = set()
		for g in self.roles:
			perms = perms | set(g.permisos)
		return perms

	@classmethod
	def by_email_address(cls, email):
		"""Return the user object whose email address is ``email``."""
		return DBSession.query(cls).filter(cls.email_address==email).first()

	@classmethod
	def by_user_name(cls, username):
		"""Return the user object whose user name is ``username``."""
		return DBSession.query(cls).filter(cls.user_name==username).first()

	def _set_password(self, password):
		"""Hash ``password`` on the fly and store its hashed version."""
		hashed_password = password

		if isinstance(password, unicode):
			password_8bit = password.encode('UTF-8')
		else:
			password_8bit = password

		salt = sha1()
		salt.update(os.urandom(60))
		hash = sha1()
		hash.update(password_8bit + salt.hexdigest())
		hashed_password = salt.hexdigest() + hash.hexdigest()

		# Make sure the hashed password is an UTF-8 object at the end of the
		# process because SQLAlchemy _wants_ a unicode object for Unicode
		# columns
		if not isinstance(hashed_password, unicode):
			hashed_password = hashed_password.decode('UTF-8')

		self._password = hashed_password

	def _get_password(self):
		"""Return the hashed version of the password."""
		return self._password

	password = synonym('_password', descriptor=property(_get_password,
														_set_password))

	#}

	def validate_password(self, password):
		"""
		Check the password against existing credentials.

		:param password: the password that was provided by the user to
			try and authenticate. This is the clear text version that we will
			need to match against the hashed one in the database.
		:type password: unicode object.
		:return: Whether the password is valid.
		:rtype: bool

		"""
		hashed_pass = sha1()
		hashed_pass.update(password + self.password[:40])
		return self.password[40:] == hashed_pass.hexdigest()


class Permiso(DeclarativeBase):
	"""
	Permiso definition for :mod:`repoze.what`.

	Only the ``permission_name`` column is required by :mod:`repoze.what`.

	"""

	__tablename__ = 'permiso'

	#{ Columns

	permiso_id = Column(Integer, autoincrement=True, primary_key=True)

	nombre = Column(Unicode(50), unique=True, nullable=False)

	descripcion = Column(Unicode(255))

	#{ Relations

	roles = relation(Rol, secondary=rol_permiso_table,
					  backref='permisos')

	#{ Special methods

	def __repr__(self):
		return '<Permiso: name=%s>' % self.nombre

	def __unicode__(self):
		return self.nombre
	#}


#}
