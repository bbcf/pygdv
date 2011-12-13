/**
 * This script will load and launch the different
 * javavascript function needed & declared by GDV
 */

//MODIFY HERE
var _GDV_PROXY="http://localhost:8080";
var _GDV_URL=_GDV_PROXY;

//GLOBAL VARIABLES
var _GDV_URL_DB = _GDV_URL + '/database';
var _GDV_URL_SCORES = _GDV_URL_DB + '/scores'
var _GDV_PROJECT_VIEW = _GDV_URL + '/projects/view';

var _POST_URL_NAMES = _GDV_URL_DB + "/search";
var _GDV_WORKER_URL = _GDV_URL + '/workers';
var _GDV_JOB_URL = _GDV_URL + '/jobs';

var _GDV_FORM_URL = _GDV_URL + '/forms';

var _GDV_JOB_STATUS_WAIT = 8000;
var _gdvls;//the live search
var _tc;//the tab container
var _jh;//the job handler
var _menub;//the menubar

var _gdv_info = {};

/**
* Initialization function for the browser
* @param{browser} the reference of the browser
* @param{project_id} the project id
* @param{readonly} true if the user cannot launch jobs
*/
function initGDV(browser, project_id, gdv_info, readonly){
    dojo.require("dijit.form.CheckBox");
    dojo.require("dijit.form.Textarea");
    dojo.require("dijit.form.Form");
    
    /* init global parameters */
    _gdv_info = gdv_info;
    _gdv_info.project_id = project_id;
    
    /* if it's a public view, parameters must be instancied diferrently */
    
    if (!_gdv_info.admin){
	gminer = {};
	menu_nav = ['Home', 'Copy in Profile']
    };
    
    dojo.addOnLoad(function(){
	/* the menu on the left */
	try {
	    var bool = 
	    _menub = new ch.epfl.bbcf.gdv.GDVMenuBar(
		{'toolbar' : gminer, 'menu_navigation' : menu_nav , 'browser' : browser});
	} catch(err) {console.error(err);}
	
	/* the search field on top right */
	try {
	    _gdvls = new ch.epfl.bbcf.gdv.Livesearch();
	} catch(err) {console.error(err);}
		
	/* the tab container on bottom */
	try {
	    _tc = new ch.epfl.bbcf.gdv.TabContainer({'browser':browser,'readonly':readonly});
	} catch(err) {console.error(err);}
	
	/* a handler for the jobs */
	try {
	    _jh = new ch.epfl.bbcf.gdv.JobHandler({});
	} catch(err) {console.error(err);}
	
	
	if(!_menub) console.error('menu bar failed');
	if(!_gdvls) console.error('tab container failed');
	if(!_gdvls) console.error('search field initialization failed');
	if(!_jh) console.error('job handler failed');

    });

    


};

/* DEFINE GfEATmINER BUTTONS */
var gminer = {'gfm_el_42': {'gfm_el_26': {'name': 'Base Coverage', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'base_coverage'}, 'gfm_el_24': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_25': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_22': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'gfm_el_23': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'doform': 'true'}, 'gfm_el_41': {'gfm_el_39': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_38': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'name': 'Score distribution', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'score'}, 'gfm_el_37': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'doform': 'true', 'gfm_el_40': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}}, 'name': 'Statistics', 'gfm_el_31': {'gfm_el_30': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_28': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'gfm_el_29': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'number_of_features'}, 'gfm_el_27': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'doform': 'true', 'name': 'Number of features'}, 'gfm_el_36': {'name': 'Length distribution', 'parameters': {'operation_type': 'desc_stat', 'characteristic': 'length'}, 'gfm_el_33': {'type': 'boolean', 'name': 'Per chromosomes', 'id': 'per_chromosomes'}, 'gfm_el_32': {'type': 'boolean', 'name': 'Compare with parents', 'id': 'compare_parents'}, 'gfm_el_35': {'type': 'drop_container', 'name': 'Filter', 'id': 'filter'}, 'gfm_el_34': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'doform': 'true'}}, 'gfm_el_110': {'name': 'Manipulations', 'gfm_el_109': {'name': 'Neighborhood', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'neighborhood'}, 'gfm_el_106': {'help_text': '.', 'type': 'number', 'name': 'Before end', 'id': 'before_end'}, 'gfm_el_107': {'help_text': '.', 'type': 'number', 'name': 'After start', 'id': 'after_start'}, 'gfm_el_104': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_105': {'help_text': '.', 'type': 'number', 'name': 'Before start', 'id': 'before_start'}, 'gfm_el_103': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_108': {'help_text': '.', 'type': 'number', 'name': 'After end', 'id': 'after_end'}, 'doform': 'true'}, 'gfm_el_102': {'name': 'Threshold', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'threshold'}, 'gfm_el_100': {'help_text': 'Choose a cut off value.', 'type': 'number', 'name': 'Threshold value', 'id': 'threshold'}, 'gfm_el_101': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_99': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'doform': 'true'}, 'gfm_el_98': {'gfm_el_97': {'radio_values': ['qualitative', 'quantitative'], 'type': 'radio_choice', 'name': 'Output type', 'id': 'output_type'}, 'gfm_el_96': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Merge', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'merge'}, 'doform': 'true'}, 'gfm_el_95': {'gfm_el_94': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Filter', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'filter'}, 'doform': 'true'}, 'gfm_el_91': {'gfm_el_86': {'gfm_el_85': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'OR', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_or'}, 'doform': 'true'}, 'gfm_el_84': {'gfm_el_83': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'AND', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_and'}, 'doform': 'true'}, 'name': 'Booleans', 'gfm_el_88': {'gfm_el_87': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'NOT', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_not'}, 'doform': 'true'}, 'gfm_el_90': {'gfm_el_89': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'XOR', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'bool_xor'}, 'doform': 'true'}}, 'gfm_el_93': {'gfm_el_92': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Mean score (by feature)', 'parameters': {'operation_type': 'genomic_manip', 'manipulation': 'mean_score_by_feature'}, 'doform': 'true'}}, 'form_ids_template': 'gfm_el', 'gfm_el_54': {'gfm_el_50': {'gfm_el_49': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'name': 'Cross-correlation', 'parameters': {'operation_type': 'plot', 'plot': 'correlation'}, 'doform': 'true'}, 'gfm_el_53': {'gfm_el_51': {'type': 'drop_container', 'name': 'List of tracks', 'id': 'ntracks'}, 'gfm_el_52': {'type': 'boolean', 'name': 'Log scale', 'id': 'log_scale'}, 'name': 'Two signal scatter', 'parameters': {'operation_type': 'plot', 'plot': 'scatter'}, 'doform': 'true'}, 'name': 'Plots'}, 'title': 'Operations'}

/* THE nav BUTTONS */
    var menu_nav = ['Home', 'Tracks', 'Projects', 'Circles']




var gdv_notifier = []
var koopa;
function notify(mess){
    gdv_notifier.push(mess);
    str = '';
    dojo.forEach(gdv_notifier, function(entry, i){
	str += entry + '\n';
    });

    dojo.byId('gdv_notifier').innerHTML = str;
    
}
