dojo.require("dijit.Tree")
dojo.provide("twdojo.CheckedTree");
dojo.declare("twdojo._CheckedTreeNode",
	[dijit._TreeNode],
	{
		setLabelNode: function(label){
			var item = this.item;
			this.labelNode.innerHTML = "";
			if (!item.root){
				var checkBox = document.createElement('input');
				checkBox.setAttribute('name', 'checked_items');
				checkBox.setAttribute('id', item.path);
				checkBox.setAttribute('type', 'checkbox');
				checkBox.setAttribute('value', item.path);
				checkBox.setAttribute('class', 'treeCheckBox');

				this.labelNode.appendChild(checkBox);
			}
				
			this.labelNode.innerHTML +='&nbsp;'+label
		}
	}
    );
dojo.declare(   "twdojo.CheckedTree",
	[dijit.Tree],
	{
		_createTreeNode: function(/*Object*/ args){
			return new twdojo._CheckedTreeNode(args);
		},
		_onClick: function(/*Event*/ e){
			// summary: translates click events into commands for the controller to process
			var domElement = e.target;
	
			// find node
			var nodeWidget = dijit.getEnclosingWidget(domElement);	
			if(!nodeWidget || !nodeWidget.isTreeNode){
				return;
			}
	
			if( (this.openOnClick && nodeWidget.isExpandable) ||
				(domElement == nodeWidget.expandoNode || domElement == nodeWidget.expandoNodeText) ){
				// expando node was clicked, or label of a folder node was clicked; open it
				if(nodeWidget.isExpandable){
					this._onExpandoClick({node:nodeWidget});
				}
			}else{
				this._publish("execute", { item: nodeWidget.item, node: nodeWidget} );
				this.onClick(nodeWidget.item, nodeWidget);
				this.focusNode(nodeWidget);
			}
			//this is removed because it gobbles up the event so that a checkbox will not get checked.
			//dojo.stopEvent(e);
		},
		getCheckedItems: function(){
			items = []
			for(var item in this._itemNodeMap){
				if(this._itemNodeMap[item].rowNode.childNodes[2].childNodes[2].childNodes[0].checked){
				items[items.length] = item
				}
			}
			return items
		}
	}
       );
       
dojo.provide("twdojo.CheckedFileTree");
dojo.declare("twdojo._CheckedFileTreeNode",
	[twdojo._CheckedTreeNode],
	{
		setLabelNode: function(label){
			var item = this.item;
			this.labelNode.innerHTML = "";
			if (!item.directory && item.root === undefined){
				var checkBox = document.createElement('input');
				checkBox.setAttribute('name', 'checked_items');
				checkBox.setAttribute('id', item.path);
				checkBox.setAttribute('type', 'checkbox');
				checkBox.setAttribute('value', item.path);
				checkBox.setAttribute('class', 'treeCheckBox');

				this.labelNode.appendChild(checkBox);
			}
				
			this.labelNode.innerHTML +='&nbsp;'+label
		}
	}
    );
dojo.declare("twdojo.CheckedFileTree",
	[twdojo.CheckedTree],
	{
		_createTreeNode: function(/*Object*/ args){
			return new twdojo._CheckedFileTreeNode(args);
		},
		

	}
       );
