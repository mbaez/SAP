# -*- coding: utf-8 -*-

from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates

from sap.lib.base import BaseController
from sap.model import DBSession, metadata

from tg import tmpl_context
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
# imports del modelo
from sap.model import *
from tg import tmpl_context, redirect, validate
#impot del checker de permisos
from sap.controllers.checker import *
#import del controlador
from tg.controllers import RestController

import transaction

class ProyectoController(RestController):
	"""
	Encargado de carga el widget para crear nuevas instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de crear
	"""
	@expose('sap.templates.new')
	@require(predicates.has_permission('crear_proyecto'))
	def new(self, modelname='',**kw):
		tmpl_context.widget = new_proyecto_form
		header_file="administracion"
		return dict(value=kw,header_file=header_file,modelname='Proyecto')
	
	"""
	Evento invocado luego de un evento post en el form de crear
	ecargado de persistir las nuevas instancias.
	"""
	@validate(new_proyecto_form, error_handler=new)
	@require(predicates.has_permission('crear_proyecto'))
	@expose()
	def post(self,modelname ,**kw):
		del kw['sprox_id']
		kw['lider'] = DBSession.query(Usuario).get(kw['lider'])
		kw['estado'] = DBSession.query(EstadoProyecto).get(kw['estado'])
		proyecto = Proyecto(**kw)
		#persiste el proyecto
		DBSession.add(proyecto)
		#Se anhade el rol de lider
		proy=DBSession.query(Proyecto).filter(Proyecto.nombre==proyecto.nombre).first()
		
		self.asignar_lider(proy)
		
		flash("El proyecto ha sido creado correctamente.")
		redirect("/administracion/proyecto/list")
	"""
	En este proceso se crear un nuevo rol denominado lider_(proyecto_id) 
	y se copian los permisos del rol lider que viene a ser como un template. 
	Este rol y sus permisos son vinculados al proyecto mendiante 
	la tabla, rol_permisos_proyecto
	"""
	def asignar_lider(self, proyecto):
		#Se obtiene el template de lider
		rol_lider = DBSession.query(Rol).filter(Rol.group_name == 'lider').first()
		#rol_lider = rol_lider[0]
		#Se copia el template en un rol nuevo
		rol = Rol()
		rol.group_name = 'lider_'+str(proyecto.id_proyecto)
		rol.display_name = 'Lider del proyecto '+ proyecto.nombre
		DBSession.add(rol)
		#Se obtiene el id de rol
		new_rol = DBSession.query(Rol).filter(Rol.group_name == rol.group_name).all()
		rol = new_rol[0]
		#Se obtienen los permisos del template
		permisos_rol = DBSession.query(RolPermiso).\
						filter(RolPermiso.group_id == rol_lider.group_id)
		#Se copian los permisos del template a rol nuevo
		for permiso in permisos_rol:
			new_permiso = RolPermiso()
			
			new_permiso.group_id = rol.group_id
			new_permiso.permission_id = permiso.permission_id
			DBSession.add(new_permiso)
		#Se asigna el rol al usuario
		self.asignar_participante (proyecto.lider.user_id, 
									rol.group_name, 
									proyecto.id_proyecto)
		DBSession.flush()
		transaction.commit()

	
	"""
	Se encarga de asignar un rol a un usuario
	"""
	def asignar_rol_usuario(self,user_id , rol_name, id_proyecto):
		
		#Se obtiene el rol con el nombre correspondiente
		rol = DBSession.query(Rol).filter(Rol.group_name == rol_name).all()
		#Se verifica si el usuario posee el rol
		rol_usuario = DBSession.query(RolUsuario).\
					filter(RolUsuario.user_id == user_id).\
					filter(RolUsuario.group_id == rol[0].group_id).all()
		
		#si no posee el rol, se le asigna
		if(len(rol_usuario) == 0):
			rol_usuario = RolUsuario()
			rol_usuario.user_id = user_id
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
						filter(RolPermiso.group_id == rol.group_id)
						
		#Se asocian los permisos de los roles a los proyectos
		for permiso in permisos_rol : 
			rol_permiso_proyecto = RolPermisoProyecto()
			
			rol_permiso_proyecto.group_id = rol.group_id
			rol_permiso_proyecto.proyecto_id = proyecto_id
			rol_permiso_proyecto.permission_id = permiso.permission_id
			
			DBSession.add(rol_permiso_proyecto)
	
	"""
	Encargado de carga el widget para editar las instancias, 
	solo tienen acceso aquellos usuarios que posean el premiso de editar
	"""
	@expose('sap.templates.edit')
	@require(predicates.has_permission('editar_proyecto'))
	def edit(self, id,**kw):
		proyecto =  DBSession.query(Proyecto).get(id)
		tmpl_context.widget = proyecto_edit_form
		kw['id_proyecto'] = proyecto.id_proyecto
		kw['nombre'] = proyecto.nombre
		kw['lider'] = proyecto.lider
		kw['estado'] = DBSession.query(EstadoProyecto).all()
		kw['lider_id'] = proyecto.lider_id
		kw['estado_id'] = proyecto.estado_id
		kw['nro_fases'] = proyecto.nro_fases
		kw['descripcion'] = proyecto.descripcion
		header_file="administracion"
		return dict(value=kw, header_file=header_file, modelname='Proyecto')

	"""
	Evento invocado luego de un evento post en el form de editar
	ecargado de persistir las modificaciones de las instancias.
	"""
	@validate(proyecto_edit_form, error_handler=edit)
	@require(predicates.has_permission('editar_proyecto'))
	@expose()
	def put(self, _method, **kw):
		#Se obtiene de la base de datos el proyecto modifcado
		proyecto = DBSession.query(Proyecto).get(int(kw['id_proyecto']))
		#Se actualizan unicamente los campos actualizables
		proyecto.nombre=kw['nombre']
		proyecto.nro_fases = kw['nro_fases'] 
		proyecto.descripcion = kw['descripcion']
		proyecto.estado=DBSession.query(EstadoProyecto).get(int(kw['estado']))
		DBSession.merge(proyecto)
		flash("El proyecto ha sido '" +proyecto.nombre+ "' modificado correctamente.")
		redirect("/administracion/proyecto/list")
	
	"""
	Encargado de cargar el widget de listado, pueden acceder unicamente 
	los usuarios que posena el permiso de ver, este widget se encuentra 
	acompanhado de enlaces de editar y eliminar
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('ver_proyecto'))
	def list(self, **kw):
		tmpl_context.widget = proyecto_table
		'''
		se obtiene la lista de los proyectos en los cuales pose el
		permiso de ver_proyecto
		'''
		proyectos = checker.get_poyect_list('ver_proyecto')
		value = proyecto_filler.get_value(proyectos)
		header_file="administracion"
		return dict(modelname='Proyectos',header_file=header_file,value=value)
	
	"""
	metodo para listar todos los proyectos al administrador
	"""
	@expose('sap.templates.list')
	@require( predicates.has_permission('manage'))
	def listall(self, **kw):
		tmpl_context.widget = proyecto_table
		#se obtiene la lista de todos los proyectos 
		value = proyecto_filler.get_value()
		header_file="administracion"
		return dict(modelname='Proyectos',header_file=header_file,
									value=value, new_url='/administracion/proyecto/new')
	
	
	"""
	Evento invocado desde el listado, se encarga de eliminar una instancia
	de la base de datos.
	"""
	@expose()
	def post_delete(self, id_proyecto, **kw):
		DBSession.delete(DBSession.query(RolPermisoProyecto).\
				  filter(RolPermisoProyecto.proyecto_id == id_proyecto))
		DBSession.delete(DBSession.query(Proyecto).get(id_proyecto))
		flash("El proyecto ha sido "+ id_proyecto +" eliminado correctamente.")
		redirect("/administracion/proyecto/list")
