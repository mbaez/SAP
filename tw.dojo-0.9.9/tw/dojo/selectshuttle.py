from tw.dojo.core import DojoBase
from tw.dojo.dijit import dijit_css

from tw.core import CSSLink, JSLink
from tw.forms import MultipleSelectField

select_shuttle_js = JSLink(modname='tw.dojo'
                         'static/twdojo/select_shuttle.js')

from tw.dojo import DojoBase

class DojoSelectShuttleField(DojoBase, MultipleSelectField):
    require = [
        'dijit.dijit',
        'dijit.form.MultiSelect',
        'dijit.form.Button',
        'twdojo.SelectShuttle',
    ]
    dojoType = 'twdojo.SelectShuttle'
    params = ['jsId',]
    css = [dijit_css]
#    javascript = [select_shuttle_js]
    include_dynamic_js_calls = True
    available_engines=['genshi']
    template = "tw.dojo.templates.selectshuttle"
    
    def update_params(self,d):
        super(DojoSelectShuttleField, self).update_params(d)
        self.update_attrs(d, "size")
        d['attrs']['multiple'] = True
        value = self.safe_validate(d['value'])
        d['selected_options'] = [option for option in d['options'] if len(option)>2 and 'selected' in option[2]]
        d['options']          = [option for option in d['options'] if len(option)<-2 or (len(option)>2 and 'selected' not in option[2])]
        
        
class DojoSortedSelectShuttleField(DojoSelectShuttleField):
    dojoType = 'twdojo.SortedSelectShuttle'