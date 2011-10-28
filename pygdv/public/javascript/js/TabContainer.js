/*
 * TabContainer : contains methods for building &
 * updating the tabpanel at the bottom of
 * the browser view
 *
 */



dojo.declare("ch.epfl.bbcf.gdv.TabContainer",null,{
    constructor: function(args){
        dojo.mixin(this, args);
        this.initTabs();
        this.initHider();
        this.elements_types = ['radio_choice','boolean','drop_container','number']
    },
    /**
     * Show th tab referenced by this id
     */
    show_tab : function(id){
	this.container.selectChild(id);
    },

    selections : function (){
	this.show_tab('tab_selections');
    },
    tracks : function(){
	this.show_tab('tab_tracks');
    },
    jobs : function(){
	this.show_tab('tab_jobs');
    },
    /**
     * Initialize the tabs :
     * - tracks tabs (already loaded)
     * - selection tabs
     * - jobs tabs
     */
    initTabs : function(){
        //reference tabs container
        this.container=this.browser.tabContainer;
        var tc = this.container;
        //reference tracks tab
        this.tab_tracks=this.browser.tab_tracks;
        //selection tab
        var cp2 = this.buildSelectionsTab(this.readonly);
        tc.addChild(cp2);
        if(!this.readonly){
            //jobs tab
            var cp3 = new dijit.layout.ContentPane({title: "Jobs",id:'tab_jobs'});
            tc.addChild(cp3);
            this.tab_jobs=cp3;
            this.connectJobUpdateEvents();
        }
    },
    /**
     * Add a button to show/hide the tabs
     */
    initHider : function(){
        //TODO
    },
    
    /* ################################################################ */
    /* ########################### JOBS ############################### */
    /* ################################################################ */
    /**
     * add a job to the jobs tab
     *@param{job} the job
     *@param{status} status of the job
     *@param{output} type of the job : e.g : a link to an image, to relaod the page,...
     */
    addJob : function(job){
        var name = job.job_id;
        var status = job.status;
        var output = job.output;
        var type = job.type;
	
        var div = dojo.byId('job_'+name);
        if(!div){
            div = document.createElement("DIV");
            div.id='job_'+name;
        }
	
	
        if(status=='success'){
            div.innerHTML='job : '+name+"  ("+type+")   ";
            div.className="job_success";
            if(output=='reload'){
		var d = document.createElement('span');
		var link = document.createElement('a');
		link.innerHTML='reload the page';
		link.className='hl';
		link.href=_GDV_URL+'/browser?id='+dojo.byId('gdv_project_id').innerHTML;
		d.appendChild(link);
		div.appendChild(d);
            } else if(output=='image'){
		var d = document.createElement('span');
                var link = document.createElement('a');
                link.innerHTML='image';
                link.className='hl';
                link.href=_GDV_URL+'/image?id='+job.job_id;
                d.appendChild(link);
                div.appendChild(d);
            }
        } else if(status == 'running'){
            div.innerHTML='job : '+name+"  ("+type+")   ";
            div.className="job_running";
        } else if(status == 'error'){
            div.innerHTML='job : '+name+"  ("+job.data+")   ";
            div.className="job_error";
        }
	
	
        this.tab_jobs.domNode.appendChild(div);
    },
    /**
     * This will update the status of the jobs when the jobs tab is selected
     */
    connectJobUpdateEvents : function(){
	
        var tabs = dijit.byId("tabcontainer");
        dojo.connect(tabs,"_transition", function(newPage, oldPage){
            var reload = false;
            if(newPage.id=='tab_jobs'){
                _jh.display_jobs();
            } else {
                _jh.stop_display();
            }
        });
    },
    /* ################################################################ */
    /* ######################### SELECTION ############################ */
    /* ################################################################ */
    /**
     * Build the selection tab panel
     * @param{readonly} true if no possibility to launch jobs
     */
    buildSelectionsTab : function(readonly){
        var tabcontainer = this;
        var cp = new dijit.layout.BorderContainer({
            liveSplitters: false,
            design: "sidebar",
            gutters: false,
            title:'Selections',
            id:'tab_selections'
        });
        //selection display
        var sels = new dijit.layout.ContentPane({region: "center",id:'tab_selections_sels'});
        if(!readonly){
            //selection form
            var act = new dijit.layout.ContentPane({region: "right",id:'tab_selections_act'});
            //button : make a new track
            var button = new dijit.form.Button({
                label: "Save selection 'as a track'",
                onClick: function() {
                    var sels = tabcontainer.tab_selections.selections;
                    if(sels){
			var selname="";
			dojo.forEach(sels, function(sel, i){
                            selname+=sel.chr+'('+sel.start+','+sel.end+')_';
			});
			selname+='.db';
			var selections_json = dojo.toJson(sels);
			_jh.new_selection(sels);
                    } else {
			alert('Make a selection first.\nUse selection icon on top left.');
                    }
                }
            });
            act.domNode.appendChild(button.domNode);
            cp.addChild(act);
        }
        cp.addChild(sels);
	
        tabcontainer.tab_selections=sels;
        return cp;
    },
    /**
     * Update the selection tab when a selection event occurs
     * Selections are accessible via _tc.tab_selections.selections
     * @param{selections} - the sorted selections
     * @param{zoneSel} - the zone selection object
     * @param{handler} - the handler of all marquees
     */
    updateSelectionTab : function(zoneSel,handler,selections){
        var tabcontainer=this;
        var tab=this.tab_selections;
        tab.selections=selections;
        //remove previous
        var store=dojo.byId('selections_store');
        if(store){
            tab.domNode.removeChild(store);
        }
        //create new
        var seldiv=document.createElement('div');
        seldiv.id=('selections_store');
        var tmp_dom = {};
        //fetch all marquees and build tmp DOM
        dojo.forEach(selections, function(sel, i){
            //build tree
            var chr = sel.chr;
            var parent=tmp_dom[chr];
            if(!parent){
                parent=document.createElement('div');
                parent.className='selection_parent';
                parent.innerHTML='Chromosome : '+chr;
            }
            var child = document.createElement('div');
            child.innerHTML='( '+sel.start+' , '+sel.end+' ) ';
            child.className='selection_child';
            //add a delete selection link
            var del = document.createElement('a');
            del.innerHTML=" delete ";
            tabcontainer.connectSel(del,zoneSel,selections,sel);
            child.appendChild(del);
            parent.appendChild(child);
	    
            tmp_dom[chr]=parent
        });
	
        //build html
        for(i in tmp_dom){
            seldiv.appendChild(tmp_dom[i]);
        }
        tab.domNode.appendChild(seldiv);
	
    },
    /**
     * Get the selections as a JSON
     * @param{selections} - the selections
     * @return a JSON Object
     */
    getJsonSelections : function(selections){
        var tmp_dom={};
        dojo.forEach(selections, function(sel, i){
            //build tree
            var chr = sel.chr;
            var array=tmp_dom[chr];
            if(!array){
                array=[];
            }
            array.push(sel.start);
            array.push(sel.end);
            tmp_dom[chr]=array;
        });
        return tmp_dom;
    },
    /**
     * Connect the delete link to the deletion of the marquee
     * Externalized to avoid disclosure events
     */
    connectSel : function(del,zoneSel,selections,sel){
        dojo.connect(del, "onclick",function(e){
            handler.delete(sel);
            handler.position();
            zoneSel.updatedSelection();
            dojo.stopEvent(e);
        });
    },
    /* ################################################################ */
    /* ########################### FORM ############################### */
    /* ################################################################ */
    /**
     * Display a form with several properties
     *@param{item} containing the properties
     */
    addFormTab : function(item){
	
        /* destroy previous form */
        this.destroyForm();
	
        /* build the form */
        var form = new dijit.form.Form({id:"gfm_form"});
        form.zIndex=70;
        //title
        var title = document.createElement("div");
        title.id="gm_form_title";
        title.innerHTML = item.name;
        form.domNode.appendChild(title);
        //close button
        var closer = document.createElement("div");
        closer.id="gfm_closer";
        dojo.connect(closer,"click",function(e){
            dojo.stopEvent(e);
            form.destroyRecursive(false);
        });
        form.domNode.appendChild(closer);
        //form body
        var bd = document.createElement("div");
        bd.id="gm_form_body";
        var ctx=this;
        //a list that will contains drop containes
        //as their are not 'standards' form inputs
        form.drop_containers = [];
        //build each elements
        var childs = _menub.getChilds(item);
        var len=childs.length;
        for(var i=0; i<len; i++){
            var child = childs[i];
            var el = ctx.getFormElement(child,form);
            bd.appendChild(el);
        }
        //reference additionnal parameters */
        form.additionnals_parameters=item.parameters;
        form.domNode.appendChild(bd);
	
        /* make it a new tab */
        var lay = new dijit.layout.LayoutContainer({title: "Form",id:'tab_form'});
        lay.addChild(form);
        this.container.addChild(lay);
        this.tab_form=lay;
	
        /* submit process */
        var dd = document.createElement('div');
        bd.appendChild(dd);
        var sub = new dijit.form.Button({id:"form_sub",label:"submit",type:"submit"
					},dd);
        this.connect_form(form);
    },
    /**
     * Connect submit button and parse values to give to GDV.
     * @param form : the form to connect
     */
    connect_form : function(form){
        var ctx=this;
        dojo.connect(form, "onSubmit", function(e) {
            e.preventDefault();
            if (form.validate()) {
		/* get the form parameters */
		var jsonform = form.attr("value");
		
		//add drop container, parameters
		if(form.drop_containers.length>0){
		    var len=form.drop_containers.length;
		    for(var i=0; i<len; i++){
			ctx.addTrackParameter(form.drop_containers[i],jsonform);
		    }
		}
		
		
		/* get other parameters from the json tree */
		var adds=form.additionnals_parameters;
		for(k in adds){
		    jsonform[k]=adds[k];
		}
		var project_id=dojo.byId('gdv_project_id').innerHTML;
		_jh.new_gfeatminer_job(project_id,jsonform);
            }
        });
	
	
    },
    /**
     * Add the track information to the JSON.
     * @param{object} the object coming from a dnd.Source
     * @param{json} the JSON Object representing the values in the form
     */
    addTrackParameter : function(object,json){
        var map = object.map;
        var len=map.length;
        var array = [];
        var map = object.map;
        for(i in map){
            var j={};
            var track = map[i]['data'];
            var url = track.url
            var db = url.substring(3,url.length-14);//get the db name from the url
            j['path']=db;
            j['name']=track.label;
            array.push(j);
        }
        json[object.drop_type]=array;
    },
    /**
     * Construct the right HTML element depending
     * of the item type.
     * The types are one of this.elements_types
     * @param{item} the item
     * @param{form} the form to references all elements created
     * @return{el} the DOM element
     */
    getFormElement : function(item,form){
        var type = item["type"];
        var name = item['name'];
        var item_id = item['id']
        var el;
	
        switch(type){
        case "radio_choice":
            el = document.createElement("div");
            el.className='gm_cb';
            console.log(item);
            var values = item['radio_values'];
            var _name = item['name'];
            var len = values.length;
            var first =true;
            for(var i=0;i<len;i++){
		var cont = document.createElement('span');
		var val = values[i];
		cont.innerHTML=val;
		var foo = new dijit.form.RadioButton({
		    name: item_id,
		    label: val,
		    value: val,
		    checked: first
		},cont);
		if(first){
		    first = false;
		}
		//foo.srcNodeRef = el;
		cont.appendChild(foo.domNode);
		el.appendChild(cont);
            }
            break;
	    
        case 'boolean':
            el = document.createElement("div");
            el.innerHTML = item["name"];
            el.className="gm_cb";
            var foo = new dijit.form.CheckBox({
		name: item_id,
		value : name,
		checked: true
            });
            el.appendChild(foo.domNode);
            break;
	    
        case 'drop_container':
            el = document.createElement("div");//base element
            el.className="gm_container";
            var t = document.createElement("div");//title
            t.innerHTML = item["name"];
            el.appendChild(t);
            var div1 = document.createElement("div");//div container for the drop container
            div1.className='gm_drop_container';
            var ctx=this;
            //drop container
            var widget1 = new dojo.dnd.Source(
		div1,{creator:ctx.copyFilterTrack,accept: ["track"],withHandles: false});
            //container for trash
            var div2 = document.createElement("div");//div container for the trash
            div2.className='gm_drop_trash';
            //trash
            var widget2 = new dojo.dnd.Source(
		div2,{creator:ctx.deleteTrack,accept: ["track-filter"],withHandles: false});
	    
            widget1.drop_type=item_id;
	    
            el.appendChild(div1);el.appendChild(div2);
            form.drop_containers.push(widget1);
            break;
	    
        case 'number':
            el = document.createElement("div");
            el.innerHTML = item["name"];
            el.className="gm_cb";
            var foo = new dijit.form.NumberTextBox({
		name: item_id,
		value : 20,
		width:'3em'
            });
            el.appendChild(foo.domNode);
            break;
            break;
	    
	    
	    
	    
	    
            //     //TRACKS
            // case "ntracks":
            //                 el = document.createElement("div");//base element
            //     el.className="gm_container";
            //     var t = document.createElement("div");//title
            //     t.innerHTML = item["name"];
            //     el.appendChild(t);
            //     var div1 = document.createElement("div");//div container for the drop container
            //     div1.id=key;
            //     div1.className='gm_drop_container';
            //     var ctx=this;
            //     var widget1 = new dojo.dnd.Source(div1,{creator:ctx.copyTrack,accept: ["track"],withHandles: false});//drop container
            //     var div2 = document.createElement("div");//div container for the trash
            //     div2.id=key;
            //     div2.className='gm_drop_trash';
            //     var widget2 = new dojo.dnd.Source(div2,{creator:ctx.deleteTrack,accept: ["track-selection"],withHandles: false});//drop container
            //     el.appendChild(div1);el.appendChild(div2);
	    
            //     form.dnd_selection=widget1;
            //     form.dnd_selection.id=type;
	    
            //     break;
	    
        default: el = document.createElement("span");
            console.warn("type "+type+" not recognized");
	    
        }
        return el;
    },
    
    /**
     * destroy the created form
     */
    destroyForm : function(){
	
        var tab_form = dijit.byId("tab_form");
        if(tab_form){
            this.container.removeChild(tab_form);
            tab_form.destroy();
            tab_form.destroyRecursive(true);
        }
    },
    /**
     * Copy the track to the desired Location
     *@param{track} the track
     */
    copyFilterTrack : function(track,hint){
        var node = document.createElement("div");
        node.className = "track-filter";
        node.innerHTML = track.label;
        node.id = dojo.dnd.getUniqueId();
        return {node: node,data: track, type: ["track-filter"]};
	
    },
    /**
     * Idem than @function{copyFilterTrack}
     */
    copyTrack : function(track,hint){
        var node = document.createElement("div");
        node.className = "track-selection";
        node.innerHTML = track.label;
        node.id = dojo.dnd.getUniqueId();
        return {node: node,data: track, type: ["track-selection"]};
    },
    /**
     * Delete the track
     */
    deleteTrack : function(track,hint){
        var node = document.createElement("div");
        node.className = "track-trashed";
        node.id = 'trashed_'+dojo.dnd.getUniqueId();
        return {node: node,data: track, type: ["track-trashed"]};
    }
});

