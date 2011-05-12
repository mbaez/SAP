"""
Dojo 1.1 widget for ToscaWidgets

To download and install::

  easy_install tw.dojo

"""
import os
import tw
from tw.core.resources import registry, working_set, Requirement
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls
import simplejson
from defaults import __DEFAULT_LINK_IS_EXTERNAL__, __DOJO_URL_BASE__, __DOJO_VERSION__, __DEFAULT_PREFIX__

class DojoLinkMixin(Link):
    params = {'basename': '(string) basename for the given file.  if you want dojotest-min.js, the base is dojotest/dojotest',
              'prefix': '(string) "", min, beta-min, or beta.  Default is "min"',
              'version': '(string) select the dojo version you would like to use. Default version is: '+__DOJO_VERSION__,
              'external': '(boolean) default:False True if you would like to grab the file from Google CDN instead of locally',
              'dojo_url_base':'The base url for fetching the Dojo library externally',
    }

    version = __DOJO_VERSION__
    external = __DEFAULT_LINK_IS_EXTERNAL__
    dojo_url_base = __DOJO_URL_BASE__
    modname = "tw.dojo"
    extension = ''
    prefix = __DEFAULT_PREFIX__
    

    def __init__(self, *args, **kw):
        super(Link, self).__init__(*args, **kw)
        if not self.is_external:
            modname = self.modname or self.__module__
            self.webdir, self.dirname, self.link = registry.register(
                self, modname, self.filename
                )

    @property
    def external_link(self):
        link = '/'.join((self.dojo_url_base, self.basename+'.'+self.extension))
        #xxx:check for existance of this resource and choose -min -min-beta -debug or no prefix as alternatives.
        return link

    def _get_link(self):
        if self.is_external:
            return self.external_link
        return tw.framework.url(self._link or '')

    def _set_link(self, link):
        self._link = link

    link = property(_get_link, _set_link)

    def abspath(self, filename):
        return os.sep.join((os.path.dirname(__file__), filename))

    def try_filename(self, filename):
        abspath = self.abspath(filename)
        if os.path.exists(abspath):
            return filename
        return False

    @property
    def filename(self):
        basename = self.basename
        
        #make basename windows/qnix compat
        basename = self.basename.replace('/', os.sep)
        basename = self.basename.replace('\\', os.sep)

        basename = os.sep.join(('static', self.version, self.prefix, basename))
        #try the default
        if self.extension:
            basename =  basename+'.'+self.extension
        return basename
        #if self.try_filename(filename):
        #    return filename

#        return None

    @property
    def is_external(self):
        return self.external


class DojoJSLink(JSLink, DojoLinkMixin):
    extension = 'js'


class DojoCSSLink(DojoLinkMixin, CSSLink):
    extension = 'css'

class DojoLink(DojoJSLink):
    engine_name='genshi'
    template = """<script type="text/javascript" src="$link" djConfig="isDebug: ${isDebug and 'true' or 'false'},
    parseOnLoad: ${parseOnLoad and 'true' or 'false'}"/>"""
    params = ["isDebug","parseOnLoad"]
    isDebug=False
    parseOnLoad=True
    
dojo_js = DojoLink(basename='dojo/dojo')
dojo_debug_js = DojoLink(prefix='debug', basename='dojo/dojo')

dojo_css = DojoCSSLink(basename = 'dojo/resources/dojo')

grid_css = DojoCSSLink(basename = 'dojox/grid/resources/Grid.css')

static_dir = Link(modname='tw.dojo', filename='static/')

dijit_dir = DojoLinkMixin(
    basename = 'static/dijit/',
    )

dojox_dir = DojoLinkMixin(
    basename = 'static/dojox/',
    )
"""
twdojo_dir = Link(
    modname = __name__, 
    filename = 'static/twdojo/',
    )
"""

tundra_css = DojoCSSLink(
    basename = 'dijit/themes/tundra/tundra',
    )

soria_css = DojoCSSLink(
    basename = 'dijit/themes/soria/soria',
    )

nihilo_css = DojoCSSLink(
    basename = 'dijit/themes/nihilo/nihilo',
    )

tundragrid_css = DojoCSSLink(
    basename = 'dojox/grid/resources/tundraGrid',
    )

soriagrid_css = DojoCSSLink(
    basename = 'dojox/grid/resources/soriaGrid',
    )

nihilogrid_css = DojoCSSLink(
    basename = 'static/dojox/grid/resources/nihiloGrid',
    )

themes_css = {'tundra':[tundra_css,tundragrid_css],'soria':[soria_css,soriagrid_css],'nihilo':[nihilo_css,nihilogrid_css]}

class DojoRequireCalls(JSDynamicFunctionCalls): 
    location = "headbottom" 
    javascript = [dojo_js]
#    _resource = [dijit_dir,dojox_dir]#,twdojo_dir]
    _resource = [static_dir]
    css = [dojo_css,tundra_css]
    # This is an attribute which can hold requirements in a request-local 
    # set. anything added here will only be visible in the current request
    _require = RequestLocalDescriptor("dojo_require_calls", default=set())
    _new_request = RequestLocalDescriptor("dojo_request", default=True)
    def __init__(self,*args,**kwargs):
        if self._new_request: 
            self._require=set()
            self._new_request=False
        super(DojoRequireCalls,self).__init__(*args,**kwargs)
    def call_getter(self,location): 
        # return dojo.require calls. This is called by the superclass 
        return map(js_function('dojo.require'), self._require) 
    def require(self, requirement):
        if self._new_request: 
            self._require=set()
            self._new_request=False
        # Called by dojo widgets which want to inject a requirement 
        self._require.add(requirement)
        # Inject ourselves into the page fisrt time we're called (we can inject 
        # ourselves many times but only will get rendered once 
        self.inject()

dojo_require = DojoRequireCalls("dojo_require")

class DojoTheme(Widget):
    params = ['theme']
    css = []
    engine_name = 'genshi'
    theme='tundra'
    template = """<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">${theme}</span>"""
    def __init__(self, themes=['tundra'], **kw):
        super(DojoTheme, self).__init__(**kw)
        self.object_type = kw.pop('object_type','')
        self.update_url = kw.pop('update_url','')
        for th in themes:
            if themes_css.has_key(th): self.css.extend(themes_css[th])
                
    
class Dojo(Widget):
    _resource = [dijit_dir,dojox_dir]
    css = [dojo_css,tundra_css]
    javascript = [dojo_js]

class DojoDebug(Widget):
    _resource = [dijit_dir,dojox_dir]
    css = [dojo_css,tundra_css]
    javascript = [dojo_debug_js]

class JSONHash(dict):
    properties=[]
    attributes_list=[]
    skip_attributes = False
    def __init__(self,**kwargs):
        for prop in self.properties: 
            value=kwargs.get(prop,None)
            if value!=None:
                self[prop]=value
        if not self.skip_attributes:
            self['attributes']={}
            for attribute in self.attributes_list:
                value=kwargs.get(attribute,None)
                if value!=None:
                    self['attributes'][attribute]=value

    def json(self):
        return simplejson.dumps(self)


dojo = Dojo()



class DojoBase(Widget):
    """DojoBase is the base dojo(dijit) widget.
    To write a new widget just subclass this, specify the required dojo resources (e.g. "dijit.form.Button")
    in the require list and specify the right dojoType.
    Needed dojo.require calls are automatically injected on head according to the require list content
    """
    require = ['dojo.parser']
    dojoType = ''
    engine_name = 'genshi'
    template = ''
    style = None
    cssclass = None
    params = {'dojoType':'The dojo type of specified widget'}

    def update_params(self, d): 
        super(DojoBase, self).update_params(d)
        for r in self.require+['dojo.parser']:
            dojo_require.require(r)

class DojoTree(DojoBase):
    require = ['dijit.Tree']
    dojoType = 'dijit.Tree'
    params = ['store','rootLabel','childrenAttrs','onClick','labelAttr','id']
    store = None
    rootLabel = None
    childrenAttrs = None
    onClick = None
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <div dojoType="dijit.tree.ForestStoreModel" py:attrs="dict(id=id+'_treemodel',jsId=id+'_treemodel',
    store=store,rootLabel=rootLabel,childrenAttrs=childrenAttrs)" />
    <div dojoType="${dojoType}" py:attrs="dict(attrs,model=id+'_treemodel',id=id,jsId=id,onClick=onClick,
    labelAttr=labelAttr)"/>
    </span>"""
