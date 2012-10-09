/**
 * This script will load and launch the different
 * javavascript function needed & declared by GDV
 */

//MODIFY HERE
var _GDV_PROXY = 'http://' + window.location.host;
var _GDV_PREFIX = "";
var _GDV_URL=_GDV_PROXY + _GDV_PREFIX;

//GLOBAL VARIABLES
var _GDV_URL_DB = _GDV_URL + '/database';
var _GDV_URL_SCORES = _GDV_URL_DB + '/scores'
var _GDV_PROJECT_VIEW = _GDV_URL + '/projects/view';
var _GDV_GR_URL = _GDV_URL + '/genrep';
var _POST_URL_NAMES = _GDV_URL_DB + "/search";
var _GDV_WORKER_URL = _GDV_URL + '/workers';
var _GDV_JOB_URL = _GDV_URL + '/jobs';
var _GDV_SEL_URL = _GDV_URL + '/selections';

var _GDV_FORM_URL = _GDV_URL + '/forms';
var _GDV_LINK_URL = _GDV_URL + '/reflect/links';

var _GENREP_URL = 'http://bbcftools.vital-it.ch/genrep';


var _GDV_JOB_STATUS_WAIT = 8000;
var _gdvls;//the live search
var _tc;//the tab container
var _jh;//the job handler
var _menub;//the menubar
var _lp;//the link panel
var _zs;//zone selection
var _gdv_pc;//principal container
var _gdv_info = {};
var _GDV_PLUG_URL = '';
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
    dojo.require("dojo.dnd.Moveable");
    dojo.require("dojox.layout.TableContainer");

    /* init global parameters */
    _gdv_info = gdv_info;
    _gdv_info.project_id = project_id;
    _gdv_info.gb = browser;
    _GDV_PLUG_URL = _gdv_info['plug_url'];

    /* if it's a public view, parameters must be instancied diferrently */

 
    
    dojo.addOnLoad(function(){
	/* the search field on top right */
	try {
	    _gdvls = new ch.epfl.bbcf.gdv.Livesearch();
	} catch(err) {console.error(err);}
	
	_lp = new LinkPanel();
	
        /* hack for the copy menu */
	if(!gdv_info.admin){
            var copy_link = dojo.byId('menu_Copy');
            var uri = document.URL;
            var query = uri.substring(uri.indexOf('?') + 1, uri.length);
            var queryO = dojo.queryToObject(query);
            if ('k' in queryO){
		copy_link.href= _GDV_URL + '/projects/copy?k=' + queryO['k'] + '&project_id=' + _gdv_info.project_id;
            } else {console.fatal('you will not be able to copy the project')};
	};
	
    });
    


};

var gdv_notifier = []

function notify(mess){
    gdv_notifier.push(mess);
    str = '';
    dojo.forEach(gdv_notifier, function(entry, i){
    str += entry + '\n';
    });
    dojo.byId('gdv_notifier').innerHTML = str;
};
