# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from sqlalchemy import func

from tg.controllers import RestController
from sap.model import *
from sap.model import DBSession, metadata
from sap.controllers.fase import FaseController
#import de widgets
from sap.widgets.createform import *
from sap.widgets.listform import *
from sap.widgets.editform import *
#impot del checker de permisos
from sap.controllers.checker import *
from sap.controllers.participante import ParticipanteProyectoController
#import del util
from sap.controllers.util import *


class ProyectosController(RestController):

	fase = FaseController()

	participantes = ParticipanteProyectoController()

	params = {'title':'','header_file':'','modelname':'', 'new_url':'',
			  'idfase':'','permiso':'', 'label': '', 'permiso':'',
			'idproyecto':'', 'permiso_editar': '', 'permiso_anadir': '' }

	@expose('sap.templates.miproyecto')
	@require(predicates.has_permission('ver_proyecto'))
	def ver(self, idproyecto):
		"""
		se obtiene la lista de las fases sobre las cuales el usurio
		tiene permisos de 'ver' y que pertenecen al proyecto que
		selecciono.

		@type  idproyecto : Integer
		@param idproyecto : Identificador del proyecto.

		@rtype  : Diccionario
		@return : El diccionario que sera utilizado en el template.
		"""
		#se controla si posee el permiso de ver para el proyecto
		has_permiso = proyecto_util.check_proyecto_permiso(idproyecto,
														   'ver_proyecto',True)
		if ( has_permiso == None) :
			flash("No posee permisos para ver el proyecto #"+str(idproyecto),'error')
			redirect('/miproyecto/error')

		tmpl_context.widget = fase_table

		fases = DBSession.query(Fase).\
									filter(Fase.proyecto==idproyecto).\
									all()
		value = fase_filler.get_value(fases)

		proyecto = proyecto_util.get_current(idproyecto)
		
		usuarios = usuario_util.get_usuarios_by_permiso(idproyecto)
		text_header='Listado de Fases del Proyecto'

		#se verifica que el proyecto ya tenga la cantidad de fases
		#establecida
		limite_fase = DBSession.query(Fase).\
									filter(Fase.proyecto==idproyecto).\
									all().count(Fase.id_fase)
		
		permiso = 'crear_fase'
		print "LIMITE "+ str(proyecto.nro_fases)
		if (proyecto.nro_fases == limite_fase):
			permiso = 'NO MOSTRAR BOTON NUEVO'

		#para saber si mostrar o no el boton editar
		permiso_editar = proyecto_util.check_proyecto_permiso(idproyecto,
												'editar_proyecto')
		#para saber si mostrar o no el boton anhdir participante
		permiso_anadir = proyecto_util.check_proyecto_permiso(idproyecto,
											'administrar_participantes')

		self.params['modelname'] = 'Fases'
		self.params['permiso'] = permiso
		self.params['label'] = '+Crear'
		self.params['new_url'] = "/miproyecto/fase/"+str(idproyecto)+"/new"
		self.params['text_header'] = 'Listado de Fases del Proyecto'
		self.params['idproyecto'] = idproyecto
		self.params['proyecto'] = proyecto
		self.params['usuarios'] = usuarios
		self.params['permiso_editar'] = permiso_editar
		self.params['permiso_anadir'] = permiso_anadir
		return dict(value=value, params=self.params)
