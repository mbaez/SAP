"""
Dojo 1.1 widget for ToscaWidgets

To download and install::

  easy_install tw.dojo

"""
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.dojo.core import *
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls
import simplejson

class DojoUpdateValues(JSSource):
    _resource = []
    update_url = ''
    object_type = ''
    template_engine = "genshi"
    source_vars = ["object_type"]
    src = """function updateValue(update_url,object_type,object_id,field,value){
        var identifier=object_type+'_id';
        var array=new Array();
        array[field]=value;
        array[identifier]=object_id;
  		var wgt=dijit.byId(object_type+'_'+object_id+'_'+field);
  		try{valid=wgt.isValid();}
  		catch (errore){valid=true;}
        if (valid){var kw={url:update_url,content:array,load:function(data){},error:function(data){},timeout:2000};dojo.xhrGet(kw);};
        };"""

    def __init__(self, location=None, **kw):
        if location:
            if location not in locations:
                raise ValueError, "JSSource location should be in %s" % locations
            self.location = location
        super(DojoUpdateValues, self).__init__(**kw)
        self.object_type = kw.pop('object_type','')
        self.update_url = kw.pop('update_url','')
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()

    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(DojoUpdateValues, self).update_params(d)


class DojoButton(DojoBase):
    require = ['dijit.form.Button']
    dojoType = 'dijit.form.Button'
    onClick = None
    title = ''
    attrs = {}
    params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    template = """<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    dojoType='${dojoType}' py:attrs="dict(attrs,onClick=onClick)">${title}</div>"""

class DojoTextBox(DojoBase):
    require = ['dijit.form.TextBox']
    dojoType = 'dijit.form.TextBox'
    title = ''
    lowercase = None
    maxlength = None
    propercase = None
    size = None
    trim = None
    uppercase = None
    name = None
    required = None
    attrs = {}
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass','dojoType','id']
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    dojoType='${dojoType}' type="text" class="${cssclass}"
    py:attrs="dict(attrs,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,trim=trim,
    uppercase=uppercase,name=name,style=style,required=required,value=value)"/>"""

class DojoDateTextBox(DojoTextBox):
    require = ['dijit.form.DateTextBox']
    dojoType = 'dijit.form.DateTextBox'
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass',
    'dojoType','id','datePattern','timePattern']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,datePattern=datePattern,
    timePattern=timePattern)"/>"""

class DojoCurrencyTextBox(DojoTextBox):
    require = ['dijit.form.CurrencyTextBox']
    dojoType = 'dijit.form.CurrencyTextBox'
    currency = None
    fractional = None
    symbol = None
    params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,currency=currency,
    fractional=fractional,symbol=symbol)"/>"""

class DojoValidationTextBox(DojoTextBox):
    require = ['dijit.form.ValidationTextBox']
    dojoType = 'dijit.form.ValidationTextBox'
    constraints = None
    invalidMessage = None
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass',
    'dojoType','id','constraints','invalidMessage','promptMessage','rangeMessage','regExp']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,constraints=constraints,
    invalidMessage=invalidMessage,promptMessage=promptMessage,rangeMessage=rangeMessage,regExp=regExp)"/>"""

class DojoCheckbox(DojoBase):
    require = ['dijit.form.Checkbox']
    dojoType = 'dijit.form.Checkbox'
    checked = None
    params = ['attrs','size','name','style','value','cssclass','dojoType','id','checked']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,size=size,name=name,style=style,value=value,checked=checked)"/>"""

class DojoRadioButton(DojoBase):
    require = ['dijit.form.RadioButton']
    dojoType = 'dijit.form.RadioButton'
    checked = None
    params = ['attrs','size','name','style','value','cssclass','dojoType','id','checked']
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,size=size,name=name,style=style,value=value,checked=checked)"/>"""

class DojoInlineEditFarm(DojoBase):
    dojoType = 'dijit.InlineEditBox'
    engine_name = 'genshi'
    upload_url = ''
    object_type = ''
    params = ["update_url", "object_type","object_id", "object_type", "field", "value", "editor", "editorParams",
            "onChange", "autoSave", "style", "attrs"]
    js_params = ["update_url", "object_type"]
    #dojo_update_values = DojoUpdateValues
    value = ''
    required = 'false'
    style = ''
    onChange = 'updateValue'
    autoSave = ''
    field = ''
    editor = ''
    regExp = ''
    promptMessage = ''
    invalidMessage = ''
    object_type = ''
    attrs = {}
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${object_type}_${object_id}_${field}"
    editorParams="${editorParams}" py:attrs="dict(attrs,editor=editor,style=style,autoSave=autoSave,dojoType=dojoType)"
    onChange="${onChange}('${update_url}','${object_type}','${object_id}','${field}',this.value)">${value}
    </span>"""
    def __init__(self,**kw):
        super(DojoInlineEditFarm, self).__init__(**kw)
        d = {}
        for param in self.js_params:
            value = getattr(self, param)
            if value is not None:
                d[param] = getattr(self, param)
        self.dojo_update_js = DojoUpdateValues(update_url=kw.get('update_url'),object_type=kw.get('object_type'))
        self.javascript.append(self.dojo_update_js)
        #self.onChange = 'updateValue'

    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(DojoInlineEditFarm, self).update_params(d)

class DojoFilteringSelect(DojoBase):
    """DojoFilteringSelect is a drop-down field with autocomplete built from a DojoDataStore
    ${SampleFilteringSelect(id='sample',store='store',searchAttr='label',onChange='alert(this.value);')}
    """
    require = ['dijit.form.FilteringSelect']
    dojoType = 'dijit.form.FilteringSelect'
    searchAttr = None
    required = 'false'
    value = None
    style = None
    onChange = None
    params = {'onChange':'the onChange method','required':'Specify if required','value':'initial value',
        'style':'CSS style'}
    template = """<input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${id}" dojoType="${dojoType}"
    py:attrs="dict(attrs,style=style,searchAttr=searchAttr,name=name,value=value,store=store,onChange=onChange,required=required)" />"""

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
