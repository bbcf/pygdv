function LinkPanel(){
    this._lp_showed = false;
    this.id = 'link_panel'
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
    // 	dojo.xhrGet(xhrArgs);
	


    if(!this._lp_showed){
    	this._lp_showed = true;
    	this.wait(node);
    	var ctx = this;
    	var name = feat[fields["name"]]; 
    	var start = feat[fields["start"]];
    	var end = feat[fields["end"]];
    	callback = function(data){ctx.buildLinkPanel(node, name, data)};
    	new GenRep().links(assembly_id, name, callback);
    };
};

LinkPanel.prototype.buildReflectPanel = function(node, data){
    var f = document.createElement('IFRAME');
    f.innerHTML = data;
    node.appendChild(f);
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



LinkPanel.prototype.wait = function(node){
    var panel = document.createElement("div");
    panel.className = "link_panel";
    panel.id = this.id;
        
    var browser = dojo.byId("GenomeBrowser").genomeBrowser;
    var loader = document.createElement("img");
    loader.src = browser.imageRoot + "ajax-loader.gif";
    panel.appendChild(loader);

    var ctx = this;
    var handler = dojo.connect(panel, 'onmouseleave', function(e){
        node.removeChild(panel);
	ctx._lp_showed = false;
	dojo.stopEvent(e);
    });

    node.appendChild(panel);
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
