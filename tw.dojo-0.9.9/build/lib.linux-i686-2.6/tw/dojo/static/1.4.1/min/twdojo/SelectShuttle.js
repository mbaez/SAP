dojo.provide("twdojo.SelectShuttle");
dojo.provide("twdojo.SortedSelectShuttle");
dojo.require("dijit._Widget");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.MultiSelect");
dojo.require("dojo.string");

dojo.declare("twdojo.SortedMultiSelect", dijit.form.MultiSelect, {
    addSelected: function(/* dijit.form.MultiSelect */select){
        // summary:
        //		Move the selected nodes af an passed Select widget
        //		instance to this Select widget.
        //
        // example:
        // |	// move all the selected values from "bar" to "foo"
        // | 	dijit.byId("foo").addSelected(dijit.byId("bar"));

        var selectedItems = select.getSelected();

        var srcName = selectedItems[0].innerHTML;
        var dstOptions = dojo.query("option",this.containerNode);
        var j = 0;
        
        for (var i=0; i<dstOptions.length; i++){
            var dstOption = dstOptions[i];
            
            if (j>selectedItems.length){ break; }
            
            while (srcName<dstOption.innerHTML){
                this.containerNode.options.add(selectedItems[j], i);
                j++;
                if (j>=selectedItems.length){ break; }
                srcName = selectedItems[j].innerHTML;
            }
        }
        //attach remaining items to the end of the list
        if (j<selectedItems.length){
            for (; j<selectedItems.length; j++){
                this.containerNode.appendChild(selectedItems[j]);
            }
        }
    },
    sort: function(){
        var options = dojo.query("option", this.containerNode);
        var newOptions = [];
        for (var i=0; i<options.length; i++){
            newOptions[i] = {};
            newOptions[i].text = options[i].text;
            newOptions[i].value = options[i].value;
            }
        newOptions.sort(function(a, b){return a.text>b.text;});
        
        for (i=0; i<options.length; i++){
            var sortedOption = newOptions[i];
            var option = options[i];
            option.value = sortedOption.value;
            option.text = sortedOption.text;
        }
    }
});

dojo.declare("twdojo.SelectShuttle",
    [dijit._Widget],
    {
        srcSelectType: dijit.form.MultiSelect,
        dstSelectType: dijit.form.MultiSelect,
        constructor: function(){
            this.el= arguments[1];
            var selects = dojo.query("select", this.el);

            this.src = new this.srcSelectType({ name: selects[0].id, parent:this }, selects[0]);
            this.src.containerNode.attachedDigit = this;
        
            this.dst = new this.dstSelectType({ name: selects[1].id, parent:this }, selects[1]);
            this.dst.containerNode.attachedDigit = this;
        
            var buttons = dojo.query("button", this.el);
            this.allRightButton = new dijit.form.Button({name:   buttons[0].id, 
                parent: this, 
                onClick:   function(){this.parent.moveAllRight();}}, 
            buttons[0]);
            this.rightButton    = new dijit.form.Button({name:buttons[1].id,
                parent: this, 
                onClick:   function(){this.parent.moveRight();}}, 
                buttons[1]);
            this.leftButton     = new dijit.form.Button({name:buttons[2].id,
                parent: this, 
                onClick:   function(){this.parent.moveLeft();}},
                buttons[2]);
            this.allLeftButton  = new dijit.form.Button({name:   buttons[3].id,
                parent: this, 
                onClick:   function(){this.parent.moveAllLeft();}},
            buttons[3]);
            this.form = this.dst.containerNode.form;
        
            //register the shuttles for this form
            if (this.form.shuttles === undefined){
                this.form.shuttles = [];
                }
            this.form.shuttles[this.form.shuttles.length]=this;
        
            //set up double click
            dojo.connect(this.src.containerNode, "ondblclick", function(e){
                this.attachedDigit.moveRight();
            });
            dojo.connect(this.dst.containerNode, "ondblclick", function(e){
                this.attachedDigit.moveLeft();
            });

            // ensure that when the "submit" button is clicked, all of the items in the "dst" 
            // select are selected
            dojo.connect(this.form, "onclick", function(e){
                if (e.target.type == 'submit'){
                    for (var i=0; i<this.shuttles.length; i++){
                        var options = this.shuttles[i].dst.containerNode.options;
                        for(var j=0; j<options.length; j++){
                            var option = options[j];
                            option.selected = "selected";
                        }
                    }
                }
            });
        },
        moveLeft: function(e){
            this.move(this.dst, this.src);
        },
        moveRight: function(e){
            this.move(this.src, this.dst);
        },
        moveAllLeft: function(e){
            this.move(this.dst, this.src, true);
        },
        moveAllRight: function(e){
            this.move(this.src, this.dst, true);
        },
        move: function(src, dst, all){
            if (all){
                // move all items
                var options = src.containerNode.options;
                for(var j=0; j<options.length; j++){
                    var option = options[j];
                    option.selected = "selected";
                }
            }
            dst.addSelected(src);
        }

    }
);

dojo.declare("twdojo.SortedSelectShuttle",
    [twdojo.SelectShuttle],
    {
     srcSelectType: twdojo.SortedMultiSelect,
     dstSelectType: twdojo.SortedMultiSelect,
     postCreate:function(){
        //make sure the containerNode options are sorted before we begin
        this.src.sort();
        this.dst.sort();
    }
});