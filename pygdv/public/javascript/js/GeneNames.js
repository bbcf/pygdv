/**
 * Contains definition and methods about the search field in the Browser.
 *
 */

dojo.declare("ch.epfl.bbcf.gdv.Livesearch",null,{
    constructor: function(args){
        dojo.mixin(this, args);
        this.timing;//the timer
        this.field;// the field in location box
        this.refSeq; // the refSeq in the browser
    },
    /**
     * Delay after onKeyUp to wait for user stop typing
     * and send the request
     */
    delay : 1,
    
    /**
     * Start the timing
     */
    startTiming : function(){
        _this = this;
        this.timing = setTimeout("_this.sendSearchPOST()",_this.delay);
    },
    /**
     * Restart the timing
     */
    restartTiming : function(){
        clearTimeout(this.timing);
        this.startTiming();
    },
    /**
     * If the user is typing
     */
    isTyping : false,
    
    /**
     * Send the POST request 'search name'
     */
    sendSearchPOST : function(){
        this.isTyping = false;
        this.post_it(this.field);
    },
    
    post_it : function(field){
	var ctx = this;
        var pData="project_id=" + _gdv_info.project_id + "&term=" + field;
        var xhrArgs = {
            url: _POST_URL_NAMES,
            postData: pData,
            handleAs: "json",
            load: function(data) {
		ctx.handleSearchNames(data);
            },
            error: function(data){
		ctx.error('GeneNames');
		ctx.error(data);
            }
        }
        dojo.xhrPost(xhrArgs);
    },
    

    /**
     * Build the POST query & send it
     * @param{tracks} the databases to search in
     * @param{name} the name to search
     * @param{chr} the current chromosome
     */
    makePOST : function(tracks,name,chr){
        var _this = this;
        var pData="id=search_name&tracks=" + tracks + "&name=" + name + "&chr=" + chr;
        var xhrArgs = {
            url: _POST_URL_NAMES,
            postData: pData,
            handleAs: "json",
            load: function(data) {
		_this.handleSearchNames(data);
            },
            error: function(data){
		_this.error(data);
            }
        }
        dojo.xhrPost(xhrArgs);
    },
    
    /**
     * Error handler
     */
    error : function(data){
        console.error("LOADING ERROR : "+data);
    },
    /**
     * handle the result of the POST 'search name'
     * @param{data} the result of the connection
     */
    handleSearchNames : function(data){
 
	var suggest_field = dojo.byId("suggest_field");
        suggest_field.style.display="inline";
        suggest_field.innerHTML="";
        var closeSuggest=document.createElement("a");
        closeSuggest.innerHTML="close";
        closeSuggest.className="close_livesearch";
        dojo.connect(closeSuggest,"onclick",function(event){
            suggest_field.style.display="none";
            dojo.stopEvent(event);
        });
        suggest_field.appendChild(closeSuggest);
        var hasResult = false;
        for(chr in data){//iterate throught chromosomes
	    
	    var suggests = data[chr];
	    var hasSuggestions = false;
	    var htmlchr=document.createElement("div");
	    htmlchr.className="chr_livesearch";
	    htmlchr.innerHTML=chr;
	    var res=document.createElement("div");
	    htmlchr.appendChild(res);
	    var limit = 4;
	    var len = suggests.length;
	    if (len < limit) limit = len; 
	    var i = 0;
	    
	    for (i; i<limit; i++){//iterate throught results
                hasSuggestions = true;
                
		var field = suggests[i];
		var name = field[0];
		var start = field[1];
		var end = field[2];

                var lin = document.createElement("a");
                lin.innerHTML = name;
                
		//calculate an interval
		var interval = end - start;
		start = start - interval;
		end = end + interval;
		
                var goTo = chr +":" + start + ".." + end;
                lin.goTo = goTo;
                lin.className="field_livesearch"
                res.appendChild(lin);
                
		dojo.connect(lin, "onclick",lin, function(event) {
		    gb = dojo.byId("GenomeBrowser").genomeBrowser;
		    gb.navigateTo(this.goTo, false);
		    suggest_field.style.display="none";
		    dojo.byId("location").value = this.goTo;
		    dojo.stopEvent(event);
		    dojo.disconnect(this);
                });
		lin.appendChild(document.createElement('BR'));
	    }
	    if(hasSuggestions == true){
                suggest_field.appendChild(htmlchr);
	    }
        }
	
	
    },
    
    /**
     * Function binded to the location box 'onKeyUp'
     */
    search : function(field, refSeq){
        var suggest_field = dojo.byId("suggest_field");
        var browser = dojo.byId("GenomeBrowser").genomeBrowser;
        suggest_field.style.display="inline";
        suggest_field.innerHTML = "";
        var loader = document.createElement("img");
        loader.src = browser.imageRoot + "ajax-loader.gif";
        suggest_field.appendChild(loader);
        this.field = field;
        this.refSeq = refSeq;
        if(this.isTyping == true){
	    this.restartTiming();
        } else {
	    this.startTiming();
	    this.isTyping = true;
        }
    }
    
});











/**
 * The purpose of this method is to search the
 * gene name inputed by the user in the FeatureTracks - exact match -
 * computed by GDV
 * @param{name} the gene name
 * @param{chr} the current chromosome
 */
function lookupGeneNames_exactMatch(name,chr){
    var tracks="";
    dojo.forEach(trackInfo, function(entry, i){
        if(entry.type=="FeatureTrack"){
            var url = entry.url;
            var matches=String(url).match(/^(\.\.\/)(.*\..*)(\/\{refseq\}\.json)$/i);
            if(matches && matches[2]){
		tracks+=matches[2]+",";
            }
        }
    });
    
    var geneFetcher = new GeneNameFetcher();
    geneFetcher.lookupInGDV_exactMatch(tracks,name,chr);
    
};

/**
 * The purpose of this method is to search for
 * genes names inputed by the user in the FeatureTracks
 * computed by GDV and suggest then to the user
 * @param{name} the gene name
 * @param{chr} the current chromosome
 */
function lookupGeneNames_searchNames(name,chr){
    var tracks="";
    dojo.forEach(trackInfo, function(entry, i){
        if(entry.type=="FeatureTrack"){
            var url = entry.url;
            var matches=String(url).match(/^(\.\.\/)(.*\..*)(\/\{refseq\}\.json)$/i);
            if(matches && matches[2]){
                tracks+=matches[2]+",";
            }
        }
    });
    
    var geneFetcher = new GeneNameFetcher();
    geneFetcher.lookupInGDV_searchMatch(tracks,name,chr);
};



function GeneNameFetcher(){
};

/**
 * Look in the GDV tracks if the name exist - search for possible match (limit 10) -
 * @param{tracks} the tracks
 * @param{name} the gene name
 * @param{chr} the current chromosome
 */
GeneNameFetcher.prototype.lookupInGDV_searchMatch = function(tracks,name,chr){
    var geneFetcher = this;
    var pData="id=search_name&tracks="+tracks+"&name="+name+"&chr="+chr;
    var xhrArgs = {
        url: _POST_URL_NAMES,
        postData: pData,
        handleAs: "json",
        load: function(data) {
            geneFetcher.handleSearchNames(data);
        },
        error: function(data){
            geneFetcher.error(data);
        }
    }
    dojo.xhrPost(xhrArgs);
};

/**
 * Look in the GDV tracks if the name exist - exact match -
 * @param{tracks} the tracks
 * @param{name} the gene name
 * @param{chr} the current chromosome
 */

GeneNameFetcher.prototype.lookupInGDV_exactMatch = function(tracks,name,chr){
    var geneFetcher = this;
    var pData="id=exact_match&tracks="+tracks+"&name="+name+"&chr="+chr;
    var xhrArgs = {
        url: _POST_URL_NAMES,
        postData: pData,
        handleAs: "json",
        load: function(data) {
            geneFetcher.handleExactMatch(data);
        },
        error: function(data){
            geneFetcher.error(data);
        }
    }
    dojo.xhrPost(xhrArgs);
};

/**
 * Handle the result of the POST connection
 * @param{data} the result of the connection ad JSON : a list of start & end
 * coordinates commas separated : {perfect:[100,10000,100000,200000]);
 * @warning DEV - for the moment, just take the first start & the last end position
 * jump to result. possible problem : when the start & end position are far from each other
 * the jump to the view will result in seing the histograms and not the feature searched
 * the data result is formatted JSON like : "{perfect:[start,end,start,end,...],suggest:[{name:[start,end,...]},{name:[start,end,...]},...}";
 */
GeneNameFetcher.prototype.handleExactMatch = function(data){
    //if perfect match, jump to location
    if(data.perfect){
	pos=data.perfect;
	var start = parseInt(pos[0]);
        //var end = parseInt(pos[1]);
	var end = parseInt(pos[pos.length-1]);
	var interval = end-start;
	start=start-interval;
        end=end+interval;
	gb=dojo.byId("GenomeBrowser").genomeBrowser;
	gb.navigateTo(start+".."+end,false);
    }
};



/**
 * Handle the result of the POST connection
 * @param{data} the result of the connection ad JSON :
 * "{suggest:[match1,match2,...],pos:{match1:[start,end,...],match2:[start,end,...],...}}";
 */
GeneNameFetcher.prototype.handleSearchNames = function(data){
    geneFetcher = this;
    var suggest_field = dojo.byId("suggest_field");
    suggest_field.style.display="inline";
    suggest_field.innerHTML="";
    var hasResult = false;
    
    for(db in data){
	var tmp = data[db];
	if(tmp.suggest && tmp.pos){
            var names = tmp.suggest;
            dojo.forEach(names,function(entry,i){
		hasResult=true;
                var link = document.createElement("a");
                link.innerHTML=entry;
                suggest_field.appendChild(link);
                //connect the links
                dojo.connect(link, "onclick", function(event) {
                    var array = tmp.pos[entry];
                    var jsonData = dojo.fromJson("{perfect:["+array+"]}");
                    //var toto = dojo.fromJson("{perfect:["+array+"]}");
                    geneFetcher.handleExactMatch(jsonData);
                    suggest_field.style.display="none";
                    dojo.byId("location").value = entry;
                    dojo.stopEvent(event);
                    dojo.disconnect(this);
                });
            });
	}
    }
    if(hasResult == false){
	suggest_field.innerHTML = "no suggestions";
    }
};


/**
 * If there is an error with handeling the
 * result of the POST connection
 */
GeneNameFetcher.prototype.error =function(data){
    console.error("loading JSON :"+data);
};
