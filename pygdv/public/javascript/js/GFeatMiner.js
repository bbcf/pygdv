var gmjson2 ={};

/**
 * AN EXAMPLE OF JSON PROVIDED BY GFEATMINER
 */
var gmjson = {GMROOT : {
    name : "gFFeatMiner",
    desc_stat :{
        name : "Descriptive statistics",
        type : "operation_type",

               number_of_features :{
        name:"Number of Features",
        type:"characteristic",
        doform:true,
        compare_parents:{name:"Compare with parents",type:"boolean"},
        per_chromosome:{name:"Per chromosome",type:"boolean"},
        selected_regions:{name:"Selected regions",type:"selection"},
        tracks:{name:"List of tracks",type:"ntracks"}
        },

        base_coverage :{
        name:"Base coverage",
        doform:true,
        type:"characteristic",
        compare_parents:{name:"Compare with parents",type:"boolean"},
        per_chromosome:{name:"Per chromosome",type:"boolean"},
        selected_regions:{name:"Selected regions",type:"selection"},
        tracks:{name:"List of tracks",type:"ntracks"}

        }
    },
    genomic_manip : {
        name: "Genomic manipulations",
        type : "operation_type"
    }
    }
};


/**
 * Initialize GFeatMiner
 */
function initGFM(){
    dojo.declare("ch.epfl.bbcf.gfm.GFeatMiner",null,{
            constructor: function(args){
                dojo.mixin(this, args);
        /**
         * @var{operations} all operations that GFeatMiner implements
         * represented by a JSON that can be assimilated
         * to a directed graph
         * define it here
         * @var{parameters} contains parameters that have to be passed
         * to the post data when the GFM form is submitted.
         * eg : it is {type:id}
         * @var{previousParam} the list of parameters that will be put.
         * It's a reminder because when you click in backlink
         * you return one step befor, and you just pop
         * the list
         */
        this.operations = gmjson;
        this.parameters={};
        this.previousParam=[];
        this.initHTMLMenu();
        },
        /**
         * add a parameter to the form
         * @param{key} the type
         * @param{value} the id
         */
        addParameter : function(key,value){
        this.parameters[key]=value;
        this.previousParam.push(key);
        },
        /**
         * remove the parameter from the form
         * @param{key} the type
         */
        removeParameter : function(key){
        delete this.parameters[key];
        },
        /**
         * Reinit the parameters. Generally occurs when the
         * user submit the form
         */
        resetParams : function(){
        this.parameters={};
        this.previousParam=[];
        },
        /**
         * initialize the buttons
         * and the form
         * Method called at the instanciation
         * of the 'class'
         */
        initHTMLMenu : function(){
        var htmlroot = dojo.byId("gdv_menu");
        //title
        var gm_title = document.createElement("div");
        gm_title.className = "menu_entry";
        //body
        var gm_body = document.createElement("div");
        gm_body.className="menu_items";
        htmlroot.appendChild(gm_title);
        htmlroot.appendChild(gm_body);
        this.gm_title = gm_title;
        this.gm_body = gm_body;
        this.htmlroot = htmlroot;
        var root = "GMROOT";
        this.gm_path =[];
        this.gm_path.push(root);
        //backlink
        var bcl = document.createElement("div");
        bcl.id="gm_backlink";
        bcl.style.display="none";
        this.backlink = bcl;
        this.backLinkConnection;
        htmlroot.appendChild(bcl);
        //init the rendering
        this.render(this.operations[root],root);
        },

        /**
         * destroy the created form
         */
        destroyForm : function(){
        var form = dijit.byId("gfm_form");
        if(form){
            form.destroy();
            form.destroyRecursive(true);
        }
        },

        /**
         * render the current element (new menu or form)
         * when you click on a button
         * @param{item} the item to render
         * @param{id} the id of the operation
         */
        render : function(item,id,tag){
        var gm = this;
        //add a parameter if one
        if(item.type && !tag){
            gm.addParameter(item.type,id);
        }
        if(item.doform){
            gm.displayForm(item,id);
        } else {
            //render the new menu
            gm.resetMenu();
            if(item.name){
            gm.gm_title.innerHTML = item.name;
            for (k in item){
                if(k!="name" && k!="type"){
                gm.addItem(item,k);
                }
            }
            }

        }
        //backlink
        if(gm.backLinkConnection){
            dojo.disconnect(gm.backLinkConnection);
        }
        gm.backLinkConnection = dojo.connect(gm.backlink, "click", function(event) {
            gm.goBack();
            dojo.stopEvent(event);
            });
        },
        /**
         * called when the user click on backlink
         */
        goBack : function(){
        this.gm_path.pop();
        if(this.gm_path.length==1){
            this.backlink.style.display="none";
        }
        var data = this.operations;
        for(k in this.gm_path){
                data = data[this.gm_path[k]];
        }
        this.render(data,this.gm_path[k],true);
        //remove previous parameter if one
        this.removeParameter(this.previousParam.pop());
        //destroy the form if one
        this.destroyForm();
        },
        /**
         * go back until the menu s the 'start' one
         */
        goStart : function(){
        while(this.gm_path.length>1){
            this.goBack();
        }
        },

        /**
         * Reset the menu
         */
        resetMenu : function(){
        this.htmlroot.removeChild(this.gm_body);
        var gm_body = document.createElement("div");
        gm_body.className="menu_items";
        this.htmlroot.appendChild(gm_body);
        this.gm_body = gm_body;
        },

        /**
         * Add the methods to the current menu
         * @param{item} the previous item
         * @param{key} the key to fecth the method
         */
        addItem : function(item,key){
        //console.log("add item "+item+"  "+key);
        //add the item
        var method = item[key];
        var gm = this;
        var but = document.createElement("button");
        but.className="gdv_menu_item";
        but.appendChild(document.createTextNode(method["name"]));
        gm.gm_body.appendChild(but);
        //connect it
        dojo.connect(but, "click", function(event) {
            gm.render(method,key);
            if(!method.doForm){
                gm.gm_path.push(key);
                gm.backlink.style.cssText=
                "position:relative;left:4em;border-color: transparent SlateGray transparent transparent;border-style: solid;border-width:1em;display: block;width: 0;"
                //gm.backlink.style.display="block";
                }

            dojo.stopEvent(event);
            });
        },

        /**
         * Display the form of gFeatMiner
         * @param{item} the input to diplay
         * @param{id} the operation type
         */
        displayForm : function(item,id){
        this.destroyForm();
        var TC = new dijit.layout.TabContainer({region: "bottom"});
        var gm=this;
        var form = new dijit.form.Form({id:"gfm_form"});
        form.zIndex=70;
        var title = document.createElement("div");
        title.id="gm_form_title";
        title.innerHTML = item.name;
        //form.domNode.appendChild(title);
        form.attr('content',title);
        var closer = document.createElement("div");
        closer.id="gfm_closer";
        dojo.connect(closer,"click",function(e){
            dojo.stopEvent(e);
            form.destroyRecursive(false);
            });
        form.attr('content',closer);
        //form.domNode.appendChild(closer);
        var bd = document.createElement("div");
        bd.id="gm_form_body";
        for (k in item){
            if(k!="name" && k!="type" && k!="doform"){
            var el = gm.getElement(item[k],k);
            bd.appendChild(el);
            }
        }
        //form.domNode.appendChild(bd);
        form.attr('content',bd);
        //submit button
        var sub = new dijit.form.Button({id:"form_sub",label:"submit",type:"submit"
            });
        //form.domNode.appendChild(sub.domNode);
        form.attr('content',sub);
        dojo.connect(form, "onSubmit", function(e) {
            e.preventDefault();
            if (form.validate()) {
                var jsonform = form.attr("value");
                //reformat tracks
                if(jsonform.tracks){
                jsonform.tracks=gm.getTracksSelected();
                }
                var projectId=dojo.byId('gdv_project_id').innerHTML;
                var param=gm.parameters;
                for(key in gm.parameters){
                jsonform[key]=param[key];
                }
                var pData="from=1&form=" +encodeURIComponent(dojo.toJson(jsonform))+"&project_id="+projectId;




                var xhrArgs = {
                url: _POST_URL_GFEATMINER,
                postData: pData,
                handleAs: "json",
                load: function(data) {
                    gm.handleJobSubmitted(data);
                },
                error: function(data){
                    gm.error(data);
                }
                }
                dojo.xhrPost(xhrArgs);
                gm.onSubmit();

            }
            });

        var tab = new dijit.layout.ContentPane({title: "form"});
        tab.appendChild(form.domNode);
        TC.appendChild(tab);
        dojo.body().appendChild(TC);

        //update form if selections already done
        this.updateZoneSelection();
        this.updateTrackSelection();
        },


        /**
         * Construct the right HTML element depending
         * of the item type
         * @param{item} the item
         * @param{key} the key of the item
         * @return{el} the HTML element
         */
        getElement : function(item,key){
        var type = item["type"];
        var el;
        switch(type){

            //CHECKBOX
        case "boolean":
            el = document.createElement("div");
            el.innerHTML = item["name"];
            el.className="gm_cb";
            var foo = new dijit.form.CheckBox({
                name: key,
                value : key,
                checked: true,
                onChange: function(b) {
                console.log('onChange called with parameter = ' + b + ', and widget value = ' + foo.attr('value'));
                }
            },key);

            el.appendChild(foo.domNode);
            break;
            //TEXTAREA FOR ZONE SELECTION
        case "selection":
            el = document.createElement("div");
            el.className="gm_ta";
            var t = document.createElement("div");
             t.innerHTML = item["name"];
             t.className="gm_ta_title";
             el.appendChild(t);
            //el.id=key;
             var bar = document.createElement("div");
             bar.id=key;

            var foo = new dijit.form.Textarea({
                    name: key,
                    id: "gfm_selection",
                    autocomplete:"on",
                    required:true,
                    title : item["name"],
                    style:"width:30em;max-width:30em;height:3em;text-align:left;",
                },bar);

            bar.appendChild(foo.domNode);
            el.appendChild(bar);
            break;


            //TEXTAREA FOR TRACK SELECTION
        case "ntracks":
            el = document.createElement("div");
            el.className="gm_ta";
            var t = document.createElement("div");
            t.innerHTML = item["name"];
            t.className="gm_ta_title";
            el.appendChild(t);

            var bar = document.createElement("div");
            bar.id=key;
            var foo = new dijit.form.Textarea({
                name: key,
                value : "",
                id:"gfm_tracks",
                required:true,
                title : item["name"],
                style:"width:30em;max-width:30em;height:3em;text-align:left;",
            },key);
            bar.appendChild(foo.domNode);
            el.appendChild(bar);
            break;

        default: el = document.createElement("span");
            console.error("type "+type+" not recognized");

        }
        return el;
        },


        /**
         * Link the zone selection update to the
         * update of the form
         */
        updateZoneSelection : function(){
        var sels = dojo.byId("store_selections");
        var textarea = dijit.byId("gfm_selection");
        if(textarea && sels){
            textarea.setValue(sels.innerHTML);
        }
        },
        /**
         * Link the update of the track selection
         * to the update of the form
         */
        updateTrackSelection : function(){
        var textarea = dijit.byId("gfm_tracks");
        if(textarea){
            textarea.setValue(TrackSelection_get().join("; "));
        }
        },
        /**
         * get the list of the tracks selected
         * under the form of a JSON :
         * {<order>:{name:<name>,path:<path>}}
         */
        getTracksSelected : function(){
        // Get a list of all track labels
        labels = dojo.query(".track-label");
        // New list contains only labels with a true selected proprety
        var json = {};
        var cpt=0;
        for (i in labels) {
            var label=labels[i];
            if (label.selected) {
            cpt++;
            for(k in trackInfo){
                var track = trackInfo[k];
                if(track.label==label.innerHTML){
                var tmp={};
                tmp.name=track.label;
                tmp.path=track.url.slice(3,track.url.length-14);
                json[cpt]=tmp;
                }
            }
            }
        }
        return json;
        },
        /**
         * Method called after the user click submit
         */
        onSubmit : function(){
        this.destroyForm();
        this.resetParams();
        this.goStart();
        },

        /**
         * error handle
         */
        error : function(data){
        console.error(data);
        },
        /**
         * handler for a submitted job
         */
        handleJobSubmitted : function(data){
        console.log(data);
        var job_id= data.jobId;
        console.log(job_id);
        //TODO add an ajax loader to the stack of jobs
        },

        /**
         * will check every n seconds if the job is finished
         */
        startChecking : function(job_id){

        }



    });

    _gfm = new ch.epfl.bbcf.gfm.GFeatMiner();
};
