/**
* Handle the operation management.
* Operation Pane && Server management.
*/
function Operations(){};



/**
* OP PANE
* Add childrens to operation menu
*/
Operations.prototype.menu_add_child = function(parent, node){
    var c = node.childs;
    var l = c.length;
    if(l>0){
	// node has childs (build a menu & add childs to it)
	var m = new dijit.Menu({});

	for(var i=0;i<l;i++){
	    this.menu_add_child(m, c[i]);
	}
	var p = new dijit.PopupMenuItem({label : node.key,
					 popup : m 
					});
	parent.addChild(p);
    } else {
	// it's the end (must connect to the form apparition)
	var m = new dijit.MenuItem({label : node.key,
				   });
	parent.addChild(m);
    }
};