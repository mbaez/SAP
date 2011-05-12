function doSearch(grid){
    var query={};
    d=dojo.query('div[id^="queryrow_"]').forEach(function(node){
        fnum=node.id.split('_')[2];
        grid=node.id.split('_')[1];
        num=grid+'_'+fnum;
        query['field_'+num]=dijit.byId('field_'+num).value;
        query['operator_'+num]=dijit.byId('operator_'+num).value;
        query['value_'+num]=dijit.byId('value_'+num).value;
    });
    grid=dijit.byId(grid);
    grid.model.query=query;
    grid.model.requestRows();
};
function changeWidget(wid){
    fnum=wid.id.split('_')[2];
    grid=wid.id.split('_')[1];
    num=grid+'_'+fnum;
    a=dojo.byId('valuebox_'+num);
    v=dijit.byId('value_'+num);
    v.destroy();
	a.innerHTML="<input type='text' dojoType='"+elemBuilder(grid,wid.value)+"' id='value_"+num+"' />";
	dojo.parser.parse(a);
};
function removeElement(wid) {
    fnum=wid.id.split('_')[2];
    grid=wid.id.split('_')[1];
    num=grid+'_'+fnum;
    d = dojo.byId('querybox_'+grid);
    w=dijit.byId('operator_'+num);
    w.destroy();
    w=dijit.byId('field_'+num);
    w.destroy();
    w=dijit.byId('value_'+num);
    w.destroy();
    w=dijit.byId('remove_'+num);
    w.destroy();
    olddiv = dojo.byId('queryrow_'+num);
    d.removeChild(olddiv);
};
grid_types = {'grid' : {'id' : 'dijit.form.TextBox','codice_fiscale' : 'dijit.form.DateTextBox','ragione_sociale' : 'dijit.form.DateTextBox'}};
function elemBuilder(grid,field){
    var types=grid_types[grid];
    var type=types[field];
    return type
};
rows = {};
function addElement(grid){
    if (rows[grid]==null) {rows[grid]=1};
    rows[grid]++;
    row=rows[grid];
    var querybox = dojo.byId('querybox_'+grid);
    var newdiv = document.createElement('div');
    divIdName="queryrow_"+grid+"_"+row
    newdiv.setAttribute('id',divIdName);
    newdiv.innerHTML = "\
    <select id='field_"+grid+"_"+row+"' name='field_"+grid+"_"+row+"'\
    dojoType='dijit.form.FilteringSelect' autocomplete='false' onChange='changeWidget(this)'>\
    <option selected='selected' value='id'>Id\
    </option><option value='ragione_sociale'>Ragione Sociale</option>\
    <option value='codice_fiscale'>Codice Fiscale</option></select></span>\
    <span id='opbox_"+grid+"_"+row+"'>\
    <select id='operator_"+grid+"_"+row+"' name='operator_"+grid+"_"+row+"' \
    dojoType='dijit.form.FilteringSelect' autocomplete='false' onChange='changeWidget(this)'>\
    <option selected='selected' value='equal'>=</option>\
    <option value='not_equal'>!=</option></select></span>\
    <span id='valuebox_"+grid+"_"+row+"'>\
    <input type='text' dojoType='dijit.form.TextBox' id='value_"+grid+"_"+row+"'\
    name='value_"+grid+"_"+rows+"' /> </span>\
    <button dojoType='dijit.form.Button' id='remove_"+grid+"_"+row+"'\
    onClick='removeElement(this)' >Remove</button>";
    querybox.appendChild(newdiv);
    dojo.parser.parse(newdiv);
  };