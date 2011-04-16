# -*- coding: utf-8 -*-
"""Setup the SAP application"""

import logging

import transaction
from tg import config

from sap.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


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

    manager = model.User()
    manager.user_name = u'admin'
    manager.display_name = u'Administrador'
    manager.email_address = u'admin@somedomain.com'
    manager.password = u'admin'

    model.DBSession.add(manager)

    group = model.Group()
    group.group_name = u'managers'
    group.display_name = u'Managers Group'

    group.users.append(manager)

    model.DBSession.add(group)

    permission = model.Permission()
    permission.permission_name = u'manage'
    permission.description = u'This permission give an administrative right to the bearer'
    permission.groups.append(group)

    model.DBSession.add(permission)

    editor = model.User()
    editor.user_name = u'editor'
    editor.display_name = u'Example editor'
    editor.email_address = u'editor@somedomain.com'
    editor.password = u'editpass'

    model.DBSession.add(editor)
    model.DBSession.flush()

    transaction.commit()
    print "Successfully setup"
