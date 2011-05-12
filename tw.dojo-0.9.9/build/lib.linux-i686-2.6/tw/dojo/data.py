from tw.dojo.core import DojoBase, JSONHash
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls

buildService=JSSource(src = """
    function buildService(url){
        var service = function(query, queryOptions) {
        if (queryOptions.isRender==undefined) queryOptions.isRender=true;
        return dojo.xhrGet({url:url, content:{query:query, queryOptions:dojo.toJson(queryOptions)},handleAs:'json',handle:function(data){return data;}});
        }
        service.put = function(id, value) {
        return dojo.xhrPut({url:url+'/'+id, handleAs:'json', content:{value:value}});
        }
        service.post = function(id, value) {
        return dojo.xhrPost({url:url+'/'+id, content:{id:id, value:value}});
        }
        service.delete = function(id) {
          var d = new dojo.Deferred();
          d.callback(); //delete is a noop for pagers
          return d;
        }
        return service
		};
    """)


class DojoDataStore(DojoBase):
    url = ''
    params = {'url':'url of remote data'}

class DojoItemFileReadStore(DojoDataStore):
    """DojoItemFileReadStore builds a dojo.data.ItemFileReadStore from a json source
    """
    require = ['dojo.data.ItemFileReadStore']
    dojoType = 'dojo.data.ItemFileReadStore'
    params = ['dojoType','id','url']
    template = """<div dojoType="${dojoType}" jsId="${id}"  id="${id}" url="${url}"/>"""
    
class DojoItemFileWriteStore(DojoDataStore):
    require = ['dojo.data.ItemFileWriteStore']
    dojoType = 'dojo.data.ItemFileWriteStore'
    params = ['dojoType','id','url']
    template = """<div dojoType="${dojoType}" jsId="${id}" id="${id}" url="${url}"/>"""

class DojoQueryReadStore(DojoDataStore):
    require = ['dojox.data.QueryReadStore']
    dojoType = 'dojox.data.QueryReadStore'
    params = ['dojoType','id','url']
    template = """<div dojoType="${dojoType}" jsId="${id}" id="${id}" url="${url}" />"""
    
class DojoJsonRestStore(DojoBase):
    javascript = [buildService]
    require = ['twdojo.data.TWDojoRestStore']
    dojoType = 'twdojo.data.TWDojoRestStore'
    params = ['target','id','url','idAttribute','autoSave']
    idAttribute='id'
    autoSave=True
    template = """
            <script type='text/javascript'>
                var ${id}=new twdojo.data.TWDojoRestStore({target:"${target}",autoSave:"${autoSave and 'true' or 'false'}", service:buildService("${url}"),idAttribute:"${idAttribute}"})
            </script>"""
    
