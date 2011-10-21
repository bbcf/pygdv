
/*
 * This file contains everything about the left Menu
 */

var gminer = {'gfm_el_42': {'gfm_el_26': {'name': 'Base Coverage', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'base_coverage'}, 'gfm_el_24': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_25': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_22': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'gfm_el_23': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'doform': 'true'}, 'gfm_el_41': {'gfm_el_39': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_38': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'name': 'Score distribution', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'score'}, 'gfm_el_37': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'doform': 'true', 'gfm_el_40': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}}, 'name': 'Statistics', 'gfm_el_31': {'gfm_el_30': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_28': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'gfm_el_29': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'number_of_features'}, 'gfm_el_27': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'doform': 'true', 'name': 'Number of features'}, 'gfm_el_36': {'name': 'Length distribution', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'length'}, 'gfm_el_33': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'gfm_el_32': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'gfm_el_35': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_34': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'doform': 'true'}}, 'gfm_el_110': {'name': 'Manipulations', 'gfm_el_109': {'name': 'Neighborhood', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'neighborhood'}, 'gfm_el_106': {'help_text': '.', 'type': 'number', 'name': 'Before end', 'id': 'before_end'}, 'gfm_el_107': {'help_text': '.', 'type': 'number', 'name': 'After start', 'id': 'after_start'}, 'gfm_el_104': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_105': {'help_text': '.', 'type': 'number', 'name': 'Before start', 'id': 'before_start'}, 'gfm_el_103': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_108': {'help_text': '.', 'type': 'number', 'name': 'After end', 'id': 'after_end'}, 'doform': 'true'}, 'gfm_el_102': {'name': 'Threshold', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'threshold'}, 'gfm_el_100': {'help_text': 'Choose a cut off value.', 'type': 'number', 'name': 'Threshold value', 'id': 'threshold'}, 'gfm_el_101': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_99': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'doform': 'true'}, 'gfm_el_98': {'gfm_el_97': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_96': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Merge', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'merge'}, 'doform': 'true'}, 'gfm_el_95': {'gfm_el_94': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Filter', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'filter'}, 'doform': 'true'}, 'gfm_el_91': {'gfm_el_86': {'gfm_el_85': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'OR', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_or'}, 'doform': 'true'}, 'gfm_el_84': {'gfm_el_83': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'AND', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_and'}, 'doform': 'true'}, 'name': 'Booleans', 'gfm_el_88': {'gfm_el_87': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'NOT', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_not'}, 'doform': 'true'}, 'gfm_el_90': {'gfm_el_89': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'XOR', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_xor'}, 'doform': 'true'}}, 'gfm_el_93': {'gfm_el_92': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Mean score (by feature)', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'mean_score_by_feature'}, 'doform': 'true'}}, 'form_ids_template': 'gfm_el', 'gfm_el_54': {'gfm_el_50': {'gfm_el_49': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Cross-correlation', 'parameters': {'operation_type': 'plot', 'plot': 'correlation'}, 'doform': 'true'}, 'gfm_el_53': {'gfm_el_51': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_52': {'type': 'boolean', 'name': 'Log scale', 'id': 'log_scale'}, 'name': 'Two signal scatter', 'parameters': {'operation_type': 'plot', 'plot': 'scatter'}, 'doform': 'true'}, 'name': 'Plots'}, 'title': 'Operations'}

var menu_nav = ['Home', 'Projects', 'Preferences']

function initMenuBar(browser){
    dojo.declare("ch.epfl.bbcf.gdv.GDVMenuBar",null,{
	constructor: function(args){
            dojo.mixin(this, args);
            if(this.toolbar && this.menu_navigation){
		this.build_navigation(this.menu_navigation);
		this.build_gminer();
	    } else {
		console.warn('cannot build toolbar, no json specified');
            }
	},

	/**
	 * Build the ``Navigation`` menu
	 *@param{item_list} : the menu items
	 */
	build_navigation : function(item_list){
	    
	    var container = dojo.byId('gdv_menu');
	    var navig = document.createElement('div');
	    navig.innerHTML = 'Navigation';
	    navig.className = 'menu_entry';
	    container.appendChild(navig);
	    var len = item_list.length;
	    for (var i=0; i<len; i++){
		link_name = item_list[i];
		link_end = link_name.toLowerCase();
		var cont = document.createElement('div');
		var link = document.createElement('a');
		cont.appendChild(link);
		// Make an image
		var img = document.createElement('img');
		img.src = window.picsPathRoot + "menu_" + link_end + ".png";
		img.className='gdv_menu_image';
		link.appendChild(img);
		// Create a span
		var span = document.createElement('span');
		span.innerHTML=link_name;
		span.className='gdv_menu_item';
		link.appendChild(span);
		// Configure the link
		link.href=_GDV_URL+'/'+link_end;
		link.className='hl';
		container.appendChild(cont);
	    }
	},
        /**
         * Build the HTML Menu
         */
        build_gminer : function(){
            var toolbar = this.toolbar;
            this.form_ids_template = toolbar['form_ids_template'];
            /* title */
            var htmlroot = dojo.byId("gdv_menu");
            var div = document.createElement("div");
            div.className = "menu_entry";
            div.innerHTML=toolbar['title'];
            htmlroot.appendChild(div);
            /* pricipal menu */
            var pmenu = this.getMenu(toolbar,'100%')
            // var pmenu = new dijit.Menu();
            // //this.menu = pMenuBar;
            // /* loop over buttons */
            // var childs = this.getChilds(toolbar)
            // var len=childs.length;
            // console.log("START");
            // console.log(toolbar);
            // console.log(childs);
            // //var pmenu = this.getMenu(childs);
            // for(var i=0; i<len; i++){
            //     var child = childs[i];
            //     /* begin recursivity to get all menu & sub menus */
            //     var menu = this.getMenu(child);
            //     /* finalize */
            //     var popup_item = new dijit.PopupMenuItem({
            //         label:child.name,
            //         popup: menu
            //     });
            //     pmenu.addChild(menu);
            //     if(i+1<len){
            //         pmenu.addChild(new dijit.MenuSeparator());
            //     }
            // }
            pmenu.placeAt("gdv_menu")
        },
    /**
     * Get the children of the item and not other parameters
     * in order to loop over them. They all begin by
     * 'form_ids_template' variable
     */
    getChilds : function(item){
        var prefix = this.form_ids_template
        data=[];
        for(i in item){
        if (this.start_with(i, prefix)) {
            data.push(item[i]);
        }
        }
        return data
    },
    /**
     * Look if a string start with the string specified.
     * This is the most efficient way to do this.
     * @param data : the string to check on
     * @param str : the prefix to look on.
     */
    start_with : function(data, str){
        return data.lastIndexOf(str, 0) === 0
    },

    /**
     * Build the menu for an item that has children
     *@param{item} the item
     *@Pparam{w} the width of the menu
     */
    getMenu : function(item,w){
        /* define the menu */
        var menu = new dijit.Menu({
        colspan:1,
        style:{width:w}
        });

        /* loop over childs */
        var childs = this.getChilds(item);
        var len=childs.length;
        for(var i=0; i<len; i++){
        var child = childs[i];
        /** connect the menu if it's a leaf or
         * recursivly get childs
         */
        if(child.doform){
            var ctx=this;
            menu.addChild(ctx.getMenuItem(ctx,child));
        } else {
            var child_menu = this.getMenu(child,'10em');
            var popup_item = new dijit.PopupMenuItem({
            label:child.name,
            popup: child_menu
            });
            menu.addChild(popup_item);
        }
             if(i+1<len){
             menu.addChild(new dijit.MenuSeparator());
         }
        }
        return menu;
    },
    /**
     * Build a Menuitem corresponding to the given item
     * @param{ctx} the context
     * @param{item} the menu item
     */
    getMenuItem : function(ctx,item){
        var o = new dijit.MenuItem({
        label:item.name,
        onClick: function(event) {
            ctx.displayForm(item);
            dojo.stopEvent(event);
        }});
        return o;
    },

    /**
     * Display the form corresponding to the item clicked
     */
    displayForm : function(item){
        _tc.addFormTab(item);
        _tc.container.selectChild("tab_form");
    }
    });
    _menub = new ch.epfl.bbcf.gdv.GDVMenuBar({'toolbar' : gminer, 'menu_navigation' : menu_nav , 'browser' : browser});
}


