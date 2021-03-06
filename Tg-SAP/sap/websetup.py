# -*- coding: utf-8 -*-
"""Setup the SAP application"""

import logging
import random
import transaction
from tg import config

from sap.config.environment import load_environment
from sap import model

#para generar el codigo de las entidades
from sap.controllers import util

__all__ = ['setup_app']

log = logging.getLogger(__name__)


__permisos__ = ['admin_usuario', 'admin_proyecto','admin_rol',
				'ver_proyecto','crear_proyecto','editar_proyecto', 'eliminar_proyecto',
				'crear_usuario', 'eliminar_usuario', 'editar_usuario', 'ver_usuario',
				'crear_rol', 'eliminar_rol', 'editar_rol','ver_rol',
				'ver_fase', 'crear_fase','editar_fase','eliminar_fase',
				'administrar_participantes',
				'generar_lineabase', 'abrir_lineabase',
				'crear_tipo_item', 'eliminar_tipo_item', 'editar_tipo_item',
				'ver_tipo_item',
				'crear_item', 'eliminar_item', 'editar_item','aprobar_item',
				'ver_item']

__permisos_sistema__ = ['admin_usuario', 'admin_proyecto','admin_rol',
						'crear_usuario', 'eliminar_usuario', 'editar_usuario', 'ver_usuario',
						'crear_rol', 'eliminar_rol', 'editar_rol','ver_rol',
						'crear_proyecto','editar_proyecto','eliminar_proyecto']

__permisos_proyecto__ = ['ver_proyecto','administrar_participantes']


__permisos_fase__ = ['ver_fase', 'crear_fase','editar_fase','eliminar_fase',
					 'administrar_participantes','generar_lineabase', 'abrir_lineabase',
					 'crear_tipo_item', 'eliminar_tipo_item', 'editar_tipo_item','ver_tipo_item',
					 'crear_item', 'eliminar_item', 'editar_item','aprobar_item','ver_item']

#lista de tipos de relacion
__relaciones__= ['padre_hijo','antecesor_sucesor']

def cargar_usuarios ():

    usr = model.Usuario()
    usr.user_name = u'mbaez'
    usr.nombre = u'Maxi'
    usr.email_address = u'mbaez@gmail.com'
    usr.password = u'mbaez'

    model.DBSession.add(usr)

    usr2 = model.Usuario()
    usr2.user_name = u'dtorres'
    usr2.nombre = u'Diego'
    usr2.email_address = u'dtorres@gmail.com'
    usr2.password = u'dtorres'

    model.DBSession.add(usr2)

    usr3 = model.Usuario()
    usr3.user_name = u'rbanuelos'
    usr3.nombre = u'Roberto'
    usr3.email_address = u'rbanuelos@gmail.com'
    usr3.password = u'rbanuelos'

    model.DBSession.add(usr3)
    return usr, usr2, usr3

def cargar_roles(manager,usr=None, usr2=None, usr3=None):

    group = model.Rol()
    group.codigo = u'admin'
    group.nombre = u'Administracion'
    group.descripcion = u'Rol de Administracion'
    group.is_template = False

    group.usuarios.append(manager)

    model.DBSession.add(group)

    group2 = model.Rol()
    group2.codigo = u'lider'
    group2.nombre = u'Lider'
    group2.descripcion = u'Lider del Proyecto'
    group2.is_template = True
    '''
    group21 = model.Rol()
    group21.codigo = u'lider_1'
    group21.nombre = u'Lider'
    group21.descripcion = u'Lider del Proyecto'
    group21.is_template = False

    group22 = model.Rol()
    group22.codigo = u'lider_2'
    group22.nombre = u'Lider'
    group22.descripcion = u'Lider del Proyecto'
    group22.is_template = False


    group23 = model.Rol()
    group23.codigo = u'lider_3'
    group23.nombre = u'Lider'
    group23.descripcion = u'Lider del Proyecto'
    group23.is_template = False

    #group2.usuarios.append(manager)
    group21.usuarios.append(usr)
    group22.usuarios.append(usr)
    group23.usuarios.append(usr2)

    model.DBSession.add(group2)
    model.DBSession.add(group21)
    model.DBSession.add(group22)
    model.DBSession.add(group23)
    '''
    model.DBSession.add(group2)
    group3 = model.Rol()
    group3.codigo = u'visitante'
    group3.nombre = u'Visitante'
    group3.descripcion = u'Visitante de Proyectos'
    group3.is_template = True
    '''
    group31 = model.Rol()
    group31.codigo = u'visitante_3'
    group31.nombre = u'Visitante'
    group31.descripcion = u'Visitante de Proyectos'
    group31.is_template = False

    group31.usuarios.append(usr3)

    model.DBSession.add(group3)
    model.DBSession.add(group31)
    '''
    model.DBSession.add(group3)

    return group, group2, group3 #, group21, group31, group22, group23

def cargar_estados():
    inicial = model.EstadoProyecto()
    inicial.id_estado_proyecto = 1
    inicial.nombre = u'Inicial'
    inicial.descripcion = u'Estado que indica que un proyecto esta en estado inicial'
    model.DBSession.add(inicial)

    desarrollo = model.EstadoProyecto()
    desarrollo.nombre = u'Desarrollo'
    desarrollo.id_estado_proyecto = 2
    desarrollo.descripcion = u'Estado que indica que un proyecto esta en desarrollo'
    model.DBSession.add(desarrollo)

    cancelado = model.EstadoProyecto()
    cancelado.nombre = u'Cancelado'
    cancelado.id_estado_proyecto = 3
    cancelado.descripcion = u'Estado que indica que un proyecto esta cancelado'
    model.DBSession.add(cancelado)

    pausado = model.EstadoProyecto()
    pausado.nombre = u'Pausado'
    pausado.id_estado_proyecto = 4
    pausado.descripcion = u'Estado que indica que un proyecto esta pausado'
    model.DBSession.add(pausado)

    finalizado = model.EstadoProyecto()
    finalizado.nombre = u'Finalizado'
    finalizado.id_estado_proyecto = 5
    finalizado.descripcion = u'Estado que indica que un proyecto esta finalizado'
    model.DBSession.add(finalizado)

    model.DBSession.flush()
    return inicial, desarrollo, cancelado, pausado, finalizado

def cargar_permisos(group, group2, group3, group21=None, group31=None, group22=None,group23=None):
	permiso = model.Permiso()
	permiso.nombre = u'manage'
	permiso.descripcion = u'Permiso administracion'
	permiso.roles.append(group)

	for name in __permisos__ :
		permiso = model.Permiso()
		permiso.nombre = name
		permiso.descripcion = u'Este permiso permite '+name
		permiso.roles.append(group)
		if(name.find("admin_") < 0):
			permiso.roles.append(group2)
		if(name.find("ver")>=0):
			permiso.roles.append(group3)


def cargar_proyectos(usr, usr2):
    proyecto = model.Proyecto()
    proyecto.lider = usr
    proyecto.nombre = u'SW Proyect'
    proyecto.descripcion = u'SW Proyect es un proyecto. Fin'
    proyecto.nro_fases = 4

    model.DBSession.add(proyecto)
    model.DBSession.flush()
    proyecto2 = model.Proyecto()
    proyecto2.lider = usr
    proyecto2.nombre = u'Parallel Programing Proyect'
    proyecto2.descripcion = u'Parallel Programing Proyect es un proyecto. Fin'
    proyecto2.nro_fases = 3

    model.DBSession.add(proyecto2)
    model.DBSession.flush()

    proyecto3 = model.Proyecto()
    proyecto3.lider = usr2
    proyecto3.nombre = u'Software Development'
    proyecto3.descripcion = u'Software Development es otro proyecto'
    proyecto3.nro_fases = 3

    model.DBSession.add(proyecto3)

    model.DBSession.flush()
    return proyecto,proyecto2,proyecto3

def cargar_fases():
    fase1 = model.Fase()
    fase1.nombre = u'Analisis de Requerimientos'
    fase1.descripcion = u'Esta fase pertenece al proyecto SW Proyect'
    fase1.proyecto = 1

    model.DBSession.add(fase1)

    fase2 = model.Fase()
    fase2.nombre = u'Disenho'
    fase2.descripcion = u'Esta fase pertenece al proyecto SW Proyect'
    fase2.proyecto = 1

    model.DBSession.add(fase2)

    fase3 = model.Fase()
    fase3.nombre = u'Analisis de Requerimientos'
    fase3.descripcion = u'Esta fase pertenece al proyecto Parallel Programing'
    fase3.proyecto = 2

    model.DBSession.add(fase3)

    fase4 = model.Fase()
    fase4.nombre = u'Analisis de Requerimientos'
    fase4.descripcion = u'Esta fase pertenece al proyecto Software Development'
    fase4.proyecto = 3

    model.DBSession.add(fase4)
    return fase1, fase2,fase3,fase4

def cargar_tipo_atributo():
    tipo1 = model.TipoAtributo()
    tipo1.nombre = u'Texto'
    tipo1.descripcion = u'Contiene datos del tipo texto'

    tipo2 = model.TipoAtributo()
    tipo2.nombre = u'Numerico'
    tipo2.descripcion = u'Contiene datos del tipo numerico'

    tipo3 = model.TipoAtributo()
    tipo3.nombre = u'Fecha'
    tipo3.descripcion = u'Contiene datos del tipo Fecha'

    model.DBSession.add(tipo1)
    model.DBSession.add(tipo2)
    model.DBSession.add(tipo3)

    model.DBSession.flush()
    return tipo1, tipo2, tipo3

def cargar_tipo_item(fase1, fase2, fase3, fase4):
    tipodeitem1 = model.TipoItem()
    tipodeitem1.fase = fase1.id_fase
    tipodeitem1.nombre = u'Caso de Uso'
    #tipodeitem1.codigo = checker.util.gen_codigo('tipo_item')
    tipodeitem1.codigo = u'CU'

    model.DBSession.add(tipodeitem1)

    tipodeitem2 = model.TipoItem()
    tipodeitem2.fase = fase2.id_fase
    tipodeitem2.nombre = u'Diagrama Secuencia'
    #tipodeitem2.codigo = checker.util.gen_codigo('tipo_item')
    tipodeitem2.codigo = u'DS'

    model.DBSession.add(tipodeitem2)

    tipodeitem3 = model.TipoItem()
    tipodeitem3.fase = fase3.id_fase
    tipodeitem3.nombre = u'Documento'
    #tipodeitem3.codigo = checker.util.gen_codigo('tipo_item')
    tipodeitem3.codigo = u'DOC'

    model.DBSession.add(tipodeitem3)

    tipodeitem4 = model.TipoItem()
    tipodeitem4.fase = fase4.id_fase
    tipodeitem4.nombre = u'Diagrama BD'
    #tipodeitem4.codigo = checker.util.gen_codigo('tipo_item')
    tipodeitem4.codigo = u'DBD'

    model.DBSession.add(tipodeitem4)
    return tipodeitem1,tipodeitem2,tipodeitem3,tipodeitem4

def cargar_estados_item():
    estadoItem1 = model.EstadoItem()
    estadoItem1.nombre = 'Aprobado'
    estadoItem1.id_estado_item = 1
    model.DBSession.add(estadoItem1)
    model.DBSession.flush()

    estadoItem2 = model.EstadoItem()
    estadoItem2.nombre = 'En Desarrollo'
    estadoItem2.id_estado_item = 2
    model.DBSession.add(estadoItem2)

    estadoItem3 = model.EstadoItem()
    estadoItem3.nombre = 'Revision'
    estadoItem3.id_estado_item = 3
    model.DBSession.add(estadoItem3)

    estadoItem4 = model.EstadoItem()
    estadoItem4.nombre = 'muerto'
    estadoItem4.id_estado_item = 4
    model.DBSession.add(estadoItem4)

    return estadoItem1,estadoItem2,estadoItem3, estadoItem4
'''
def cargar_relaciones():
    i = 1
    for name in __relaciones__ :
        relacion = model.RelacionParentesco()
        relacion.relacion_parentesco = i
        relacion.nombre = name
        relacion.descripcion = u'Este tipo representa la relacion '+name
        model.DBSession.add(relacion)
        i += 1

    model.DBSession.flush()

    relacion1 = model.RelacionItem()
    relacion1.id_item_actual = 1
    relacion1.id_item_relacionado = 2
    relacion1.relacion_parentesco = 1

    model.DBSession.add(relacion1)

    relacion2 = model.RelacionItem()
    relacion2.id_item_actual = 1
    relacion2.id_item_relacionado = 11
    relacion2.relacion_parentesco = 2

    model.DBSession.add(relacion2)


    relacion3 = model.RelacionItem()
    relacion3.id_item_actual= 2
    relacion3.id_item_relacionado = 5
    relacion3.relacion_parentesco = 1

    model.DBSession.add(relacion3)

    relacion4 = model.RelacionItem()
    relacion4.id_item_actual= 5
    relacion4.id_item_relacionado = 11
    relacion4.relacion_parentesco = 2

    model.DBSession.add(relacion4)

    model.DBSession.flush()
'''

def cargar_items():
    #solo se cargan items en la primera fase.
    for i in range(10):
        item = model.Item()
        item.nombre = u'item '+str(i+1)
        item.estado = 2
        item.tipo_item = 1
        item.fase = 1
        item.version = 1
        item.prioridad = 1
        item.complejidad =  int(random.random()*10)+1
        #se le pasa el id de la fase y el id del tipo de item al cual
        #corresponde
        item.codigo = util.item_util.gen_cod(1, 1)
        model.DBSession.add(item)
    model.DBSession.flush()

def cargar_permisos_proyecto(group21, group22, group23, group31):

    id = [group21.rol_id, group22.rol_id, group23.rol_id, group31.rol_id]

    for i in range(len(__permisos__)):
        for j in range(len(id)):
            rpp = model.RolPermisoProyecto()
            rpp.rol_id = id[j]
            if j==3 :
                rpp.proyecto_id = j
            else :
                rpp.proyecto_id = j+1
            rpp.permiso_id = i+1

            model.DBSession.add(rpp)

        rpf = model.UsuarioPermisoFase()
        rpf.fase_id = 1
        rpf.permiso_id = i+1
        rpf.usuario_id = 2

        model.DBSession.add(rpf)

        rpf2 = model.UsuarioPermisoFase()
        rpf2.fase_id = 2
        rpf2.permiso_id = i+1
        rpf2.usuario_id = 2

        model.DBSession.add(rpf2)

def cargar_estado_lineabase():
    model.DBSession.flush()

    estadoLineaBase = model.EstadoLineaBase()
    estadoLineaBase.id_estado_linea_base = 1
    estadoLineaBase.nombre = 'Comprometida'
    model.DBSession.add(estadoLineaBase)

    estadoLineaBase = model.EstadoLineaBase()
    estadoLineaBase.id_estado_linea_base = 2
    estadoLineaBase.nombre = 'Cerrada'
    model.DBSession.add(estadoLineaBase)

    estadoLineaBase = model.EstadoLineaBase()
    estadoLineaBase.id_estado_linea_base = 3
    estadoLineaBase.nombre = 'Abierta'
    model.DBSession.add(estadoLineaBase)

def cargar_tipos_relaciones ():
    id_rel = 1
    for name in __relaciones__ :
        relacion = model.RelacionParentesco()
        relacion.relacion_parentesco = id_rel
        relacion.nombre = name
        relacion.descripcion = u'Este tipo representa la relacion '+name
        model.DBSession.add(relacion)
        id_rel += 1
    model.DBSession.flush()

def setup_app(command, conf, vars):
    """Place any commands to setup sap here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
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
    ##usuarios
    #usr, usr2, usr3 = cargar_usuarios()
    #Roles
    model.DBSession.flush()
    group, group2, group3 = cargar_roles(manager)
    model.DBSession.flush()
    #estados
    inicial, desarrollo, cancelado, pausado, finalizado = cargar_estados()
    #Permisos
    model.DBSession.flush()
    cargar_permisos(group, group2, group3)
    #Proyectos
    model.DBSession.flush()
    #proyecto,proyecto2,proyecto3 = cargar_proyectos(usr,usr2)
    #fases
    #model.DBSession.flush()
    #fase1, fase2,fase3,fase4 = cargar_fases()
    #tipo de atributo
    #model.DBSession.flush()
    #tipo1, tipo2, tipo3 = cargar_tipo_atributo()
    #tipo de item
    #model.DBSession.flush()
    #tipodeitem1,tipodeitem2,tipodeitem3,tipodeitem4 = cargar_tipo_item(
    #                                                   fase1, fase2,fase3,
    #                                                   fase4)
    #estados de item
    model.DBSession.flush()
    estadoItem1,estadoItem2,estadoItem3, estadoItem4 = cargar_estados_item()
    #items
    #cargar_items()
    model.DBSession.flush()
    #tipo de relaciones
    cargar_tipos_relaciones()
    model.DBSession.flush()
    #Permisos del rol de proyecto
    #cargar_permisos_proyecto(group21,group22,group23,group31)
    #estado linea base
    model.DBSession.flush()
    cargar_estado_lineabase()
    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"
