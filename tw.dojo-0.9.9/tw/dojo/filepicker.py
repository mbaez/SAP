from tw.dojo.core import DojoBase

class DojoFilePicker(DojoBase):
    require = ['dojox.widget.FilePicker', 'dojox.data.FileStore']
    dojoType = 'dojox.widget.FilePicker'
    params = ['id', 
              'attrs', 
              'columns', 
              'jsId', 
              'cssclass', 
              ]
    delayScroll = "true"
    cssclass=""
    rowsPerPage = 20
    columns = []
    columnReordering = "true"
    columnResizing="false"
    include_dynamic_js_calls = True
    action='.json'
    model = None
    actions = True
    engine_name = "genshi"
    template = """<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">
                      <div dojoType="dojox.data.FileStore" url="${url}" jsId="${jsId}_filestore" pathAsQueryParam="true"></div>
                      <div dojoType="dojox.widget.FilePicker" jsId="${jsId}" id="${jsId}" style="width: 50%;" store="${jsId}_filestore" query="{}"></div>
                  </span>
               """
    
class DojoTreeFilePicker(DojoBase):
    require = ['dojox.widget.ItemFileReadStore', 'dijit.Tree', 'dojo.parser']
    dojoType = 'dijit.Tree'
    params = ['id', 
              'attrs', 
              'jsId', 
              'cssclass', 
              ]
    delayScroll = "true"
    cssclass=""
    rowsPerPage = 20
    columns = []
    columnReordering = "true"
    columnResizing="false"
    include_dynamic_js_calls = True
    action='.json'
    model = None
    actions = True
    engine_name = "genshi"
    template = """
<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">
    <div dojoType="dojo.data.ItemFileReadStore"
         url="${url}" jsid="${jsId}_store" />
    <div dojoType="dijit.Tree" store="${jsId}_store" labelAttr="root"
         label="Root">
            <script type="dojo/method" event="getLabelClass" args="item">
            if (item != null && ${jsId}.getValue(item, "type") == 'category') {
                    return ${jsId}.getValue(item, "name");
            }
        </script>
    </div>
"""
    
    