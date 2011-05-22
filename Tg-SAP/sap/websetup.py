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
				'editar_usuario', 'ver_usuario',
				'crear_item', 'eliminar_item', 'editar_item', 
				'crear_tipo_item', 'eliminar_tipo_item', 'editar_tipo_item']

#lista de tipos de relacion
__relaciones__= ['padre_hijo','antecesor_sucesor']

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
    manager.nombre = u'Administrador'
    manager.email_address = u'admin@somedomain.com'
    manager.password = u'admin'

    model.DBSession.add(manager)

    group = model.Rol()
    group.codigo = u'admin'
    group.nombre = u'Administracion'
    group.descripcion = u'Rol de Administracion'
    group.is_template = True

    group.usuarios.append(manager)

    model.DBSession.add(group)

    group2 = model.Rol()
    group2.codigo = u'lider'
    group2.nombre = u'Lider'
    group2.descripcion = u'Lider del Proyecto'
    group2.is_template = True

    group2.usuarios.append(manager)

    model.DBSession.add(group2)


    activo = model.EstadoProyecto()
    activo.nombre = u'Activo'
    activo.descripcion = u'Estado que indica que un proyecto esta activo'

    model.DBSession.add(activo)

    permission = model.Permiso()
    permission.nombre = u'manage'
    permission.descripcion = u'This permission give an administrative right to the bearer'
    permission.roles.append(group)

    model.DBSession.add(permission)
    for name in __permisos__ :
		permiso = model.Permiso()
		permiso.nombre = name
		permiso.descripcion = u'Este permiso permite '+name
		permiso.roles.append(group)

    """
    --------------------Datos Prueba Grafos---------------------
    """
    proyecto = model.Proyecto()
    proyecto.lider_id = manager.usuario_id
    proyecto.nombre = u'proyecto1'
    proyecto.nro_fases = 3

    model.DBSession.add(proyecto)

    model.DBSession.flush()

    fase1 = model.Fase()
    fase1.nombre = u'fase1'
    fase1.proyecto = 1

    model.DBSession.add(fase1)

    fase2 = model.Fase()
    fase2.nombre = u'fase2'
    fase2.proyecto = 1

    model.DBSession.add(fase2)
    model.DBSession.flush()
    tipodeitem1 = model.TipoItem()
    tipodeitem1.fase = fase1.id_fase
    tipodeitem1.nombre = u'tipo1'

    model.DBSession.add(tipodeitem1)

    tipodeitem2 = model.TipoItem()
    tipodeitem2.fase = fase2.id_fase
    tipodeitem2.nombre = u'tipo2'

    model.DBSession.add(tipodeitem2)

    estadoitem = model.EstadoItem()
    estadoitem.nombre = u'estado1'

    model.DBSession.add(estadoitem)

    for name in __relaciones__ :
		relacion = model.RelacionParentesco()
		relacion.nombre = name
		relacion.descripcion = u'Este tipo representa la relacion '+name
		model.DBSession.add(relacion)

    model.DBSession.flush()

    for i in range(10):
		item = model.Item()
		item.estado = 1
		item.tipo_item = 1
		item.fase = 1
		item.version = 1
		item.prioridad = 1
		item.complejidad = i+1
		model.DBSession.add(item)

    item = model.Item()
    item.estado = 1
    item.tipo_item = 1
    item.fase = 2
    item.version = 1
    item.prioridad = 1
    item.complejidad = 11
    model.DBSession.add(item)

    model.DBSession.flush()

    relacion1 = model.RelacionItem()
    relacion1.id = 1
    relacion1.item_realcionado = 2
    relacion1.relacion_parentesco = 1

    model.DBSession.add(relacion1)

    relacion2 = model.RelacionItem()
    relacion2.id = 1
    relacion2.item_realcionado = 11
    relacion2.relacion_parentesco = 2

    model.DBSession.add(relacion2)


    relacion3 = model.RelacionItem()
    relacion3.id = 2
    relacion3.item_realcionado = 5
    relacion3.relacion_parentesco = 1

    model.DBSession.add(relacion3)

    """
    --------------------Fin Datos de Prueba----------------------
    """
    model.DBSession.flush()
    for i in range(17):
        rpp = model.RolPermisoProyecto()
        rpp.rol_id = 1
        rpp.proyecto_id = 1
        rpp.permiso_id = i+1

        model.DBSession.add(rpp)

        rpf = model.RolPermisoFase()
        rpf.fase_id = 1
        rpf.permiso_id = i+1
        rpf.rol_id = 1

        model.DBSession.add(rpf)

    transaction.commit()
    print "Successfully setup"
