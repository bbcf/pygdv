/**
* Handle the operation management.
* Operation Pane && Server management.
*/
function Operations(){
    this.ifr_loaded = false;
};



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
	this.connect_menu(m, node);
	parent.addChild(m);
    }
};




/**
* Create the iframe of the serv
*/
Operations.prototype.create_frame = function(container){
    this.ifr = dojo.io.iframe.create(this.ifr_id, '_gdv_info.operations.iframe_loaded()', _GDV_PLUG_URL + '/get_form');
    container.appendChild(this.ifr);
};

/**
* Connect the menu item to show the form
*/
Operations.prototype.connect_menu = function(menu, node){
    var ctx = this;
    dojo.connect(menu, 'onclick', function(e){
	ctx.serv_get_form(node.id);
	ctx.show_iframe();
	dojo.stopEvent(e);
    });
};

/**
* OP SERV
* Get the form from the server with the uid.
*/
Operations.prototype.serv_get_form = function(form_id){
    this.ifr.src = _GDV_PLUG_URL + '/get_form?form_id=' + form_id;
};


/**
* OP SERV
*
*/
Operations.prototype.show_iframe = function(){
    if (this.ifr_loaded){
	var ifr = dojo.style(this.ifr, {visibility:'visible', height:'100%', width:'100%', zIndex:'500', backgroundColor: 'white'});
	dojo.query('#' + this.id + ' >').forEach(function(node, i, arr){
     	    node.style.display='block';
	});
    }
};

Operations.prototype.hide_iframe = function(){
    
};


Operations.prototype.iframe_loaded = function(){
    this.ifr_loaded = true;
}