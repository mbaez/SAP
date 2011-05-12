from tw.dojo.core import DojoBase


class MenuBar(DojoBase):
    require=[
    "dijit.MenuBar",
    ]
    template="genshi:tw.dojo.templates.menubar"

class PopupMenuBarItem(DojoBase):
    params=['title']
    require=[
    "dijit.PopupMenuBarItem",
    "dijit.Menu"
    ]
    template="genshi:tw.dojo.templates.popupmenubaritem"

class MenuItem(DojoBase):
    """
        >>> h = MenuItem(title='Foo')
        jkgjs
    """
    on_click=''
    params=['title', 'href', 'on_click']
    require=[
    "dijit.MenuItem",
    ]
    template="genshi:tw.dojo.templates.menuitem"

class Action(object):
    def __init__(self, on_click=''):
        self.on_click=on_click
class Link(object):
    def __init__(self, href):
        self.href=href
    def __unicode__(self):
        return self.href



def make_menu_bar(menu):
    """
    >>> make_menu_bar([
        ('File', [
            ('link', Link('http://www.turbogears.org')),
        ('action', Action('alert("This was an action");')),
        ]),
        ('Further...',[('rum', Link('http://python-rum.org'))])])
    ...
    """
    assert isinstance(menu, list)
    def make_sub_menu(title, sub_menu):
        if isinstance(sub_menu, Link):
            return MenuItem(title=title, href=unicode(sub_menu))
        if isinstance(sub_menu, Action):
            return MenuItem(title=title, on_click=sub_menu.on_click)
        if isinstance(sub_menu, list):
            return PopupMenuBarItem(title=title, children=[make_sub_menu(k,v) for (k,v) in sub_menu])
        never_come_here=False
        assert never_come_here
    return MenuBar(children=[make_sub_menu(k,v) for (k,v) in menu])
        