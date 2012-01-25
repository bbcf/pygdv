function LinkPanel(){
    this._lp_showed = false;
    this.id = 'link_panel';
    this.ifr_id = 'ifr_reflect';
    this.loader_id = 'link_panel_loader';
    this.data = null;
    this.ifr_node = null;
    this.gr_loaded = false;
    this.ifr_loaded = false;
};

/**
* Show the info panel.
*/
LinkPanel.prototype.showPanelInfo = function(node, event, assembly_id, feat, fields){
    this.node = node;
    this.genRepPanel(node, event, assembly_id, feat, fields);
};

LinkPanel.prototype.parent_node = function(event){
    var p = document.createElement("div");
    p.style.position = 'fixed'; 
    console.log(event);
    p.style.top =  event.pageY + 'px';
    p.style.left = event.pageX + 'px';
    document.body.appendChild(p);
    return p;
};

/**
* Show GenRep info.
*/
LinkPanel.prototype.genRepPanel = function(node, event, assembly_id, feat, fields){
    var pnode = this.parent_node(event);
    /* remove panel if one */
    if(this._lp_showed){
	dojo.query('#' + this.id).orphan();
    };
    this._lp_showed = true;
    this.wait(pnode, node);
    
    var ctx = this;
    
    this.gene_name = feat[fields["name"]]; 
    var start = feat[fields["start"]];
    var end = feat[fields["end"]];

    callback = function(data){ctx.genrep_loaded(data, pnode, feat[fields['subfeatures']])};
    new GenRep().links(assembly_id, this.gene_name, callback);
};




/**
* Called when GenRep Has send back result
*/
LinkPanel.prototype.genrep_loaded = function(data, pnode, subfeatures){
    this.gr_loaded = true;
    this.data = data;
    /* destroy loader */
    var loader = dojo.query('#' + this.loader_id).orphan();
    dojo.query('#' + this.id + ' >').forEach(function(node, i, arr){
	node.style.display='block';
    });
    /* build genrep panel */
    var ct = document.createElement("DIV");
    var gn = document.createElement('h4');
    gn.innerHTML = this.gene_name;
    ct.appendChild(gn);


    /* subfeatures */
    if (subfeatures){};

    /* links */
    var title = document.createElement('h5');
    title.innerHTML = 'Links';
    ct.appendChild(title);
    
    var cclose = document.createElement('img');
    cclose.src = '../images/delete.png';
    cclose.className = 'lp_close';
    dojo.connect(cclose, 'onclick', function(e){
	dojo.query('#' + ctx.id).orphan();
	ctx.unload();
	dojo.stopEvent(e);
    });

    ct.appendChild(cclose);

    for(key in data){
	var d = document.createElement('DIV');
	var el = document.createElement('a');
	el.innerHTML = key;
	el.href = data[key];
	d.appendChild(el);
	ct.appendChild(d);
    }
    ct.className = 'link_panel_gr';
    
    /* add a link to reflex */
    var reflex_div = document.createElement('DIV');
    var reflex_link = document.createElement('DIV');
    reflex_link.id = "reflex_link";
    reflex_link.innerHTML = "reflex.ws";
    reflex_link.href = '';
    reflex_div.appendChild(reflex_link);
    ct.appendChild(reflex_div);
    dojo.byId(this.id).appendChild(ct);
    var ctx = this;
    
    /* connect reflex */
    dojo.connect(reflex_div, 'onclick', function(e){
	ctx.reflexPanel(pnode);
	dojo.stopEvent(e);
    });
};




/**
* Info panel from reflex.ws
*/
LinkPanel.prototype.reflexPanel = function(pnode){
    /* create iframe (should juste create one and use it everytime) */
    var fr = dojo.io.iframe.create(this.ifr_id, '_lp.iframe_loaded()', 'http://reflect.ws/REST/GetPopup?name=' + this.gene_name);
    fr.src='http://reflect.ws/REST/GetPopup?name=' + this.gene_name;
    
    /* destroy genRep panel */
    var loader = dojo.query('#' + this.id).orphan();
    
    
    /* show wait panel*/
    var node = this.node;
    this.wait(pnode, node);
    var n = dojo.byId(this.id);
    n.style.height='300px';
    n.style.width='400px';

    /* create container for the iframe */
    var fr_cont = document.createElement('div');
    fr_cont.width='100%';
    fr_cont.id = 'link_panel_cont';
    var cclose = document.createElement('img');
    cclose.src = '../images/delete.png';
    cclose.className = 'lp_close';
    fr_cont.appendChild(cclose);
    var panel = dojo.byId(this.id);
    var ctx = this;
    dojo.connect(cclose, 'onclick', function(e){
	dojo.query('#' + ctx.id).orphan();
	ctx.unload();
	dojo.stopEvent(e);
    });
    fr_cont.appendChild(cclose);
    
    fr_cont.appendChild(fr);
    fr_cont.style.display = 'none';
    panel.appendChild(fr_cont);
};











/**
* Called when the iframe finished loading
*/
LinkPanel.prototype.iframe_loaded = function(){
    this.ifr_loaded = true;
    this.ifr_node = null;
    var loader = dojo.query('#' + this.loader_id).orphan();
    
    var ifr = dojo.style(dojo.byId(this.ifr_id), {visibility:'visible', height:'100%', width:'100%', zIndex:'500', backgroundColor: 'white'});
    dojo.query('#' + this.id + ' >').forEach(function(node, i, arr){
     	node.style.display='block';
     });
};


/**
* Called when closing the link panel
*/
LinkPanel.prototype.unload = function(data){
    this.ifr_loaded = false;
    this.gr_loaded = false;
    this.data = null;
};





LinkPanel.prototype.wait = function(parent_node, node){
    var panel = document.createElement("div");
    panel.className = "link_panel";
    panel.id = this.id;
    panel.style.cssText = node.style.cssText;
    
    var browser = dojo.byId("GenomeBrowser").genomeBrowser;
    var loader = document.createElement("img");
    loader.src = browser.imageRoot + "ajax-loader.gif";
    loader.id = this.loader_id;
    panel.appendChild(loader);

    parent_node.appendChild(panel);
};

