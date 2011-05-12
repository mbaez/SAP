"""
dijit widgets
"""
from tw.dojo.core import DojoBase, DojoCSSLink
from tw.forms import InputField

dijit_css = DojoCSSLink(
    basename = 'dijit/themes/dijit'
)


class DojoProgressBar(DojoBase):
    require = ['dijit.ProgressBar']
    dojoType = 'dijit.ProgressBar'
    params = ['id', 'jsId']
    store = None
    rootLabel = None
    childrenAttrs = None
    onClick = None
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <div dojoType="dijit.ProgressBar"
         jsId="$jsId" id="$id"></div>
    </span>"""

class DojoCalendarDatePicker(DojoBase):
    require = ['dijit._Calendar']
    dojoType= 'dijit._Calendar'
    params = ['jsId', 'onChange']
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <div dojoType="$dojoType"
         jsId="$jsId" id="$id" onChange="$onChange"></div>
    </span>"""
    
class DijitRichTextEditor(DojoBase, InputField):
    require = ['dijit.Editor']
    dojoType = 'dijit.Editor'
    params = ['id', 'jsId']
    template = "<div/>"
    template = """<div xmlns="http://www.w3.org/1999/xhtml"
       dojoType="$dojoType"
       jsId="${jsId}"
       xmlns:py="http://genshi.edgewall.org/"
       type="${type}" name="${name}" class="${css_class}" id="${id}"
       py:attrs="attrs" 
       value="${value}" />
       """
