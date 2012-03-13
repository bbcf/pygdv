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
	var ctx = this;
	var m = new dijit.MenuItem({label : node.key,
				    onClick : function(e){
					ctx.serv_get_form(node.id);
					ctx.show_form();
					dojo.stopEvent(e);
				    }});
	parent.addChild(m);
    }
};




/**
* OP FORM
* Create the iframe of the serv (will contains the form)
*/
Operations.prototype.create_frame = function(container, fwdgt, bwdgt){
    this.ifr = dojo.io.iframe.create(this.ifr_id, '_gdv_info.operations.iframe_loaded()', _GDV_PLUG_URL + '/get_form');
    container.appendChild(this.ifr);
    this.container = container;
    this.fwdgt = fwdgt;
    this.bwdgt = bwdgt;
    this.form_showed = true;
    this.hide_form();
};

/**
* OP FORM
* Show the operation form
*/
Operations.prototype.show_form = function(){
    if (!(this.form_showed)){
	
	this.bwdgt.addChild(this.fwdgt);
	this.form_showed = true;
	var ifr = dojo.style(this.ifr, {visibility:'visible', height:'100%', width:'100%', zIndex:'500', backgroundColor: 'white'});
	var closer = dojo.create('img', {src:'../images/delete.png', style : {zIndex:1000, position:'absolute'}}, this.container);
	var ctx = this;
	dojo.connect(closer, 'click', function(e){
	    ctx.hide_form();
	});


    };
};
/**
* OP FORM
* Hide the operation form
*/
Operations.prototype.hide_form = function(){
    if (this.form_showed){
	this.bwdgt.removeChild(this.fwdgt);
	this.form_showed = false;
    };
};

/**
* OP SERV
* Get the form from the server with the uid.
*/
Operations.prototype.serv_get_form = function(form_id){
    this.ifr.src = _GDV_PLUG_URL + '/get_form?form_id=' + form_id;
    console.log(_GDV_PLUG_URL + '/get_form?form_id=' + form_id);
};

Operations.prototype.iframe_loaded = function(){
    this.ifr_loaded = true;
}