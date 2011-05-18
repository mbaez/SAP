# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
# project specific imports
from sap.lib.base import BaseController
from sap.model import DBSession, metadata


"""

"""
from tg import tmpl_context

from sap.model import *
from tg import tmpl_context, redirect, validate

from tg.controllers import RestController

class CheckerController(RestController):
	@expose()
	def check_proyecto_permiso(self, id_proyecto, permiso_name,nuleable=False):
		"""
		Controla si el usuario logeado posee permisos sobre el proyecto
		"""
		current_user = self.get_current_user()
		rol_permiso_proyecto = DBSession.query(RolPermisoProyecto).\
								filter(RolPermisoProyecto.rol_id ==
									RolUsuario.rol_id).\
								filter(RolPermisoProyecto.proyecto_id ==
									id_proyecto).\
								filter(Permiso.permiso_id ==
									RolPermisoProyecto.permiso_id).\
								filter(Permiso.nombre ==
									permiso_name).\
								filter(RolUsuario.usuario_id ==
									current_user.id_usuario).\
								all()

		if (len(rol_permiso_proyecto) != 0):
			return predicates.has_permission(permiso_name)
		elif nuleable == False:
			return predicates.has_permission(permiso_name+' '+str(id_proyecto))
		else:
			return None


	def get_current_user(self):
		identity = request.environ.get('repoze.who.identity')
		username = identity['repoze.who.userid']

		current_user = DBSession.query(Usuario).\
				filter(Usuario.user_name == username ).\
				first()
		return current_user


	def get_poyect_list(self, permiso_name):
		current_user = self.get_current_user()

		proyectos = DBSession.query(Proyecto).\
					filter(RolPermisoProyecto.rol_id ==
						RolUsuario.rol_id).\
					filter(RolPermisoProyecto.proyecto_id ==
						Proyecto.id_proyecto).\
					filter(Permiso.permiso_id ==
						RolPermisoProyecto.permiso_id).\
					filter(Permiso.nombre ==
						permiso_name).\
					filter(RolUsuario.usuario_id ==
						current_user.usuario_id).\
					all()
		return proyectos
	"""
	metodo para listar las fases sobre las cuales el usuario tiene permiso "permiso_name"
	y pertenecen al proyecto seleccionado "idproyecto"
	"""
	def get_fases_by_proyecto_list(self, idproyecto, permiso_name):
		current_user = self.get_current_user()

		fases = DBSession.query(Fase).\
					filter(RolPermisoFase.rol_id ==
						RolUsuario.rol_id).\
					filter(RolPermisoFase.fase_id ==
						Fase.id_fase).\
					filter(Permiso.permiso_id ==
						RolPermisoFase.permiso_id).\
					filter(Permiso.nombre ==
						permiso_name).\
					filter(RolUsuario.usuario_id ==
						current_user.usuario_id).\
					filter(Fase.proyecto ==
						idproyecto).\
					all()
		return fases


checker =  CheckerController()

class UtilController(RestController) :

	"""
	En este proceso se crear un nuevo rol denominado lider_(proyecto_id)
	y se copian los permisos del rol lider que viene a ser como un template.
	Este rol y sus permisos son vinculados al proyecto mendiante
	la tabla, rol_permisos_proyecto
	"""
	def asignar_lider(self, proyecto):
		#Se obtiene el template de lider
		rol_lider = DBSession.query(Rol).filter(Rol.nombre == 'lider').first()
		#Se copia el template en un rol nuevo
		rol = Rol()
		rol.group_name = 'lider_'+str(proyecto.id_proyecto)
		rol.display_name = 'Lider del proyecto '+ proyecto.nombre
		DBSession.add(rol)
		#Se obtiene el id de rol
		new_rol = DBSession.query(Rol).filter(Rol.nombre == rol.nombre).all()
		rol = new_rol[0]
		#Se obtienen los permisos del template
		permisos_rol = DBSession.query(RolPermiso).\
						filter(RolPermiso.rol_id == rol_lider.rol_id)
		#Se copian los permisos del template a rol nuevo
		for permiso in permisos_rol:
			new_permiso = RolPermiso()

			new_permiso.rol_id = rol.rol_id
			new_permiso.permiso_id = permiso.permiso_id
			DBSession.add(new_permiso)
		#Se asigna el rol al usuario
		self.asignar_participante (proyecto.lider.usuario_id,
									rol.nombre,
									proyecto.id_proyecto)
		DBSession.flush()
		transaction.commit()

	"""
	Se encarga de asignar un rol a un usuario
	"""
	def asignar_rol_usuario(self,user_id , rol_name, id_proyecto):

		#Se obtiene el rol con el nombre correspondiente
		rol = DBSession.query(Rol).filter(Rol.nombre == rol_name).all()
		#Se verifica si el usuario posee el rol
		rol_usuario = DBSession.query(RolUsuario).\
					filter(RolUsuario.usuario_id == usuario_id).\
					filter(RolUsuario.rol_id == rol[0].rol_id).all()

		#si no posee el rol, se le asigna
		if(len(rol_usuario) == 0):
			rol_usuario = RolUsuario()
			rol_usuario.usuario_id = usuario_id
			rol_usuario.group_id = rol[0].group_id
			DBSession.add(rol_usuario)

		return rol[0]
	"""
	Asigna un el rol al participante y de asociar los permisos del rol
	al proyecto especificado
	"""
	def asignar_participante(self, user_id, rol_name, proyecto_id, ):
		rol = self.asignar_rol_usuario(user_id, rol_name, proyecto_id)
		#Se obtiene los permisos que posee el rol
		permisos_rol = DBSession.query(RolPermiso).\
						filter(RolPermiso.rol_id == rol.rol_id)

		#Se asocian los permisos de los roles a los proyectos
		for permiso in permisos_rol :
			rol_permiso_proyecto = RolPermisoProyecto()

			rol_permiso_proyecto.rol_id = rol.rol_id
			rol_permiso_proyecto.proyecto_id = proyecto_id
			rol_permiso_proyecto.permiso_id = permiso.permiso_id

			DBSession.add(rol_permiso_proyecto)

	def __get_usuarios_proyecto__(self, idproyecto, permiso_name='ver_proyecto'):
		usuarios = DBSession.query(Usuario).\
					filter(RolUsuario.usuario_id == Usuario.usuario_id).\
					filter(RolPermisoProyecto.rol_id == RolUsuario.rol_id).\
					filter(RolPermisoProyecto.proyecto_id == idproyecto).\
					filter(RolPermisoProyecto.permiso_id == Permiso.permiso_id).\
					filter(Permiso.nombre == permiso_name)
		return usuarios

util = UtilController()
