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
* Called when the iframe finished loading
*/
LinkPanel.prototype.iframe_loaded = function(){
    this.ifr_loaded = true;
    this.ifr_node = null;
    this.loaded();
};

/**
* Called when GenRep Has send back result
*/
LinkPanel.prototype.genrep_loaded = function(data){
    this.gr_loaded = true;
    this.data = data;
    this.loaded();
};

/**
* Called when closing the link panel
*/
LinkPanel.prototype.unload = function(data){
    this.ifr_loaded = false;
    this.gr_loaded = false;
    this.data = null;
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
    var pnode = node.parentNode;
    /* remove panel if one */
    if(this._lp_showed){
	dojo.query('#' + this.id).orphan();
    };
    this._lp_showed = true;
    this.wait(pnode, node);
    
    var ctx = this;
    var name = feat[fields["name"]]; 
    var start = feat[fields["start"]];
    var end = feat[fields["end"]];
    
    /* create iframe (should juste create one and use it everytime) */
    var fr = dojo.io.iframe.create(this.ifr_id, '_lp.iframe_loaded()', 'http://reflect.ws/REST/GetPopup?name=' + name);
    fr.src='http://reflect.ws/REST/GetPopup?name=' + name;
   
    /* send request to GenRep */
    callback = function(data){ctx.genrep_loaded(data)};
    new GenRep().links(assembly_id, name, callback);

    /* create container for the iframe */
    var fr_cont = document.createElement('div');
    fr_cont.width='100%';
    fr_cont.id = 'link_panel_cont';
    var cclose = document.createElement('img');
    cclose.src = '../images/delete.png';
    cclose.className = 'lp_close';
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
* Called by the two method of loading data (iframe & GenRep),
* executing when both are complete
*/
LinkPanel.prototype.loaded = function(){
    if (this.ifr_loaded && this.gr_loaded){
	/* destroy loader */
	var loader = dojo.query('#' + this.loader_id).orphan();
	dojo.query('#' + this.id + ' >').forEach(function(node, i, arr){
	    node.style.display='block';
	});
	
	
	var ifr = dojo.style(dojo.byId(this.ifr_id), {visibility:'visible', height:'100%', width:'100%', zIndex:'200', backgroundColor: 'white'});
	this.buildLinkPanel(dojo.byId('link_panel_cont'), name, this.data);
    };
};


/**
 * Build the HTML panel
 * @param{node} the HTML node
 * @param{data} the link data as JSON
 */
LinkPanel.prototype.buildLinkPanel = function(node, gene_name, data){
    var ct = document.createElement("DIV");
    var gn = document.createElement('h4');
    gn.innerHTML = gene_name;
    ct.appendChild(gn);
    var title = document.createElement('h5');
    title.innerHTML = 'Links';
    ct.appendChild(title);
    for(key in data){
	var d = document.createElement('DIV');
	var el = document.createElement('a');
	el.innerHTML = key;
	el.href = data[key];
	d.appendChild(el);
	ct.appendChild(d);
    }
    ct.className = 'link_panel_gr'
    node.appendChild(ct);
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
