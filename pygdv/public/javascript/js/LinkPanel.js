var _linkPanel;
/**
 * Quick made function which has the purpose
 * to show a link Panel on the browser view
 * @param{node} the HTML node
 * @param{nrAssemblyId} the nr_assembly_id of Genrep
 * @param{name} name of the gene
 * @param{start} start of the feature
 * @param{end of the feature}
 */
function showLinkPanel(node,nrAssemblyId,name,start,end){
    if(!_linkPanel){
    var url=_GDV_URL+"/link";
    var pData="gene_name="+name+"&nr_assembly_id="+nrAssemblyId;
    var xhrArgs = {
            url: url,
        postData: pData,
            handleAs: "json",
            load: function(data){
        console.log(data);
        console.log(node);
        buildLinkPanel(node,data);
        },
            error: function(error) {
        console.error(data);
            }
        };
    console.log(xhrArgs);
    var deferred = dojo.xhrPost(xhrArgs);
    }
};

/**
 * Build the HTNL panel
 * @param{node} the HTML node
 * @param{data} the link data as JSON
 */
function buildLinkPanel(node,data){
    var panel = document.createElement("div");
    panel.className = "link_panel";
    panel.id = "linkPanel";
    panel.style.border="1px solid black";
    panel.style.padding="1px";
    var title = document.createElement("h5");
    title.innerHTML = "Links";
    panel.appendChild(title);
    for(key in data){
    var el = document.createElement("a");
    el.innerHTML=key;
    el.href=data[key];
    panel.appendChild(el);
    }
    node.appendChild(panel);
    _linkPanel=true;
    //add events
    var handler = dojo.connect(panel,'onmouseleave',function(e){
        e.stopPropagation();
        dojo.stopEvent(e);
        if(e.srcElement){
        if(e.srcElement.tagName=="DIV"){
            node.removeChild(panel);
            _linkPanel=false;
            dojo.disconnect(handler);
            }
        }
        else {
            if(e.currentTarget.className=="link_panel"){
            _linkPanel=false;
            node.removeChild(panel);
            dojo.disconnect(handler);
            }
        }
        });
};


function LinksMaker(){};

/**
 * Build an reference to Ensembl database
 * @param{species} the species
 * @param{name} the name of the gene
 * @return a link to ensembl
 */
LinksMaker.prototype.getEnsembl = function (species,name) {
    return this.buildLink("http://www.ensembl.org/"+species+"/Location/View?g="+name,"Ensembl");
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
