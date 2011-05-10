# -*- coding: utf-8 -*-
"""Setup the SAP application"""

import logging

import transaction
from tg import config

from sap.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)
__permisos__= ['ver_proyecto','crear_proyecto','editar_proyecto',
				'administrar_participantes','eliminar_proyecto','ver_fase',
				'crear_fase','editar_fase','eliminar_fase',
				'crear_rol', 'eliminar_rol', 'editar_rol' 
				'ver_rol','crear_usuario', 'eliminar_usuario',
				'editar_usuario', 'ver_usuario']

def setup_app(command, conf, vars):
    """Place any commands to setup sap here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from sap import model
    engine = config['pylons.app_globals'].sa_engine
    print "Droping tables"
    model.metadata.drop_all(engine)
    print "Finish..\nCreating tables"
    model.metadata.create_all(bind=engine)

    manager = model.Usuario()
    manager.user_name = u'admin'
    manager.display_name = u'Administrador'
    manager.email_address = u'admin@somedomain.com'
    manager.password = u'admin'

    model.DBSession.add(manager)

    group = model.Rol()
    group.group_name = u'managers'
    group.display_name = u'Managers Group'

    group.users.append(manager)

    model.DBSession.add(group)

    activo = model.EstadoProyecto()
    activo.nombre = u'Activo'
    activo.descripcion = u'Estado que indica que un proyecto esta activo'

    model.DBSession.add(activo)

    permission = model.Permiso()
    permission.permission_name = u'manage'
    permission.description = u'This permission give an administrative right to the bearer'
    permission.groups.append(group)

    model.DBSession.add(permission)
    for name in __permisos__ :
		permiso = model.Permiso()
		permiso.permission_name = name
		permiso.description = u'Este permiso permite '+name
		permiso.groups.append(group)
    
    model.DBSession.flush()

    transaction.commit()
    print "Successfully setup"
