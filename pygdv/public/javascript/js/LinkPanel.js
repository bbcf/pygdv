function LinkPanel(){
    this._lp_showed = false;
    this.id = 'link_panel';
    this.ifr_id = 'ifr_reflect';
    this.loader_id = 'link_panel_loader';
};


/**
 * Quick made function which has the purpose
 * to show a link Panel on the browser view
 * @param{node} the HTML node
 * @param{nrAssemblyId} the nr_assembly_id of Genrep
 * @param{name} name of the gene
 * @param{start} start of the feature
 * @param{end of the feature}
 */

 
LinkPanel.prototype.showPanelInfo = function(node, assembly_id, feat, fields){
    // var name = feat[fields["name"]];
    // var deferred = dojo.io.iframe.send({
    // 	url : 'http://reflect.ws/REST/GetPopup?name=' + name,
    // 	contentType: 'html',
    // 	handleAs: 'html',
    // 	handle: function(data, ioargs){
    // 	    console.log(data);
    // 	    console.log(ioargs);
    // 	}
    // });

    // var name = feat[fields["name"]];
    // var ctx = this;
    // callback = function(data){ctx.buildReflectPanel(node, data)};
    // var xhrArgs = {
    // 	url : _GDV_LINK_URL + '?name=' + name + '&assembly_id=' + assembly_id,
    // 	handleAs : 'html',
    // 	load : function(data){
    // 	    callback(data);
    // 	},
    // 	error : function(data){
    // 	    console.error(data);
	
    // 	}
    // };
    // 	dojo.xhrGet(xUncaught Error: NOT_FOUND_ERR: DOM Exception 8hrArgs);
	

    
    // if(!this._lp_showed){
    // 	this._lp_showed = true;
    // 	this.wait(node);
    // 	var ctx = this;
    // 	var name = feat[fields["name"]]; 
    // 	var start = feat[fields["start"]];
    // 	var end = feat[fields["end"]];
    // 	callback = function(data){ctx.buildLinkPanel(node, name, data)};
    // 	new GenRep().links(assembly_id, name, callback);
    // };
    var pnode = node.parentNode;
    if(!this._lp_showed){
	this._lp_showed = true;
	this.wait(pnode, node);
	
	var ctx = this;
    	var name = feat[fields["name"]]; 
	var start = feat[fields["start"]];
	var end = feat[fields["end"]];
    	

	var fr = dojo.io.iframe.create(this.ifr_id, '_lp.loaded()', 'http://reflect.ws/REST/GetPopup?name=' + name);
	
	var fr_cont = document.createElement('div');
	fr_cont.width='100%';
	var cclose = document.createElement('img');
	cclose.src = '../images/delete.png';
	cclose.className = 'lp_close';
	var panel = dojo.byId(this.id);
	var ctx = this;
	dojo.connect(cclose, 'onclick', function(e){
	    dojo.query('#' + ctx.id).orphan();
	    ctx._lp_showed = false;
	    dojo.stopEvent(e);
	});
	fr_cont.appendChild(cclose);
	fr_cont.appendChild(fr);
	
	fr_cont.style.display = 'none';
	
	panel.appendChild(fr_cont);
    };
};



LinkPanel.prototype.loaded = function(){
    var loader = dojo.query('#' + this.loader_id).orphan();
    dojo.query('#' + this.id + ' >').forEach(function(node, i, arr){
	node.style.display='block';
    });
    var ifr = dojo.style(dojo.byId(this.ifr_id), {visibility:'visible', height:'100%', width:'100%', zIndex:'200'});
    
};


/**
 * Build the HTML panel
 * @param{node} the HTML node
 * @param{data} the link data as JSON
 */
LinkPanel.prototype.buildLinkPanel = function(node, gene_name, data){
    var panel = dojo.byId(this.id);
    dojo.empty(panel);
    var gn = document.createElement('h4');
    gn.innerHTML = gene_name;
    panel.appendChild(gn);
    var title = document.createElement('h5');
    title.innerHTML = 'Links';
    panel.appendChild(title);
    for(key in data){
	var d = document.createElement('DIV');
	var el = document.createElement('a');
	el.innerHTML = key;
	el.href = data[key];
	d.appendChild(el);
	panel.appendChild(d);
    }
    node.appendChild(panel);
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



function LinksMaker(){};

/**
 * Build an reference to Ensembl database
 * @param{species} the species
 * @param{name} the name of the gene
 * @return a link to ensembl
 */
LinksMaker.prototype.getEnsembl = function (species,name) {
    return this.buildLink("http://www.ensembl.org/" + species + "/Location/View?g=" + name,"Ensembl");
};

LinksMaker.prototype.hover = function (node,over,out) {
    return node.onmouseenter(over).onmouseleave(out||over);
};

/**
 * Build a reference to SGD database
 * @param{name} the gene name
 */
LinksMaker.prototype.getYeast = function (name){
    return this.buildLink("http://www.yeastgenome.org/cgi-bin/locus.fpl?locus="+name,"SGD");
};

/**
 * Convenient method to build a link
 * @param {url} the href of the link
 * @param {name} the name of the gene
 * @param {entity} the text link
 */
LinksMaker.prototype.buildLink = function(url,entity){
    var link = document.createElement("a");
    link.href = url;
    link.innerHTML = entity;
    return link;
};
