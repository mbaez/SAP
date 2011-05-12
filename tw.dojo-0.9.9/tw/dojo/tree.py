from tw.dojo.core import DojoBase, DojoCSSLink
from tw.core import JSLink

tree_css = DojoCSSLink(
    basename = 'dijit/themes/tundra/Tree'
    )

dijit_css = DojoCSSLink(
    basename = 'dijit/themes/dijit'
)

#lazy_store_js = JSLink(modname='tw.dojo'
#                         'static/twdojo/LazyLoadStore.js')

class DojoTreeFilePicker(DojoBase):
    require = [
      "dojox.data.FileStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
    ]
    dojoType = 'dijit.Tree'
    params = ['id', 
              'attrs', 
              'jsId', 
              'cssclass', 
              'url'
              ]
    delayScroll = "true"
    css = [tree_css, dijit_css]
#    javascript = [lazy_store_js]
    cssclass=""
    rowsPerPage = 20
    columns = []
    columnReordering = "true"
    columnResizing="false"
    include_dynamic_js_calls = True
    action='.json'
    model = None
    actions = True
    template = "genshi:tw.dojo.templates.dojotreepicker"
    
class DojoTreeFileCheckboxPicker(DojoTreeFilePicker):
    require = [
      "dojox.data.FileStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
      "twdojo.CheckedTree",
    ]
    template = "genshi:tw.dojo.templates.dojotreefilecheckboxpicker"
    
class DojoTreeCheckboxPicker(DojoTreeFilePicker):
    require = [
      "dojox.data.FileStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
      "twdojo.CheckedTree",
    ]
    template = "genshi:tw.dojo.templates.dojotreecheckboxpicker"