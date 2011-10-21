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

var _POST_URL = _GDV_URL+"/gdv_queries";
var _POST_URL_NAMES = _GDV_URL+"/gdv_names";
var _POST_URL_GDV = _GDV_URL+"/post";

var _gdvls;//the live search
var _gfm;
var _tc;//the tab container
var _jh;//the job handler
var _menub;//the menubar

/**
* Initialization function for the browser
* @param{browser} the reference of the browser
* @param{readonly} true if the user cannot launch jobs
*/
function initGDV(browser,readonly){
    dojo.require("dijit.form.CheckBox");
    dojo.require("dijit.form.Textarea");
    dojo.require("dijit.form.Form");

    initGDVLiveSearch();
    dojo.addOnLoad(function(){
        initTab_container(browser,readonly);
        if(!readonly){
        initJobHandler();
        initMenuBar(browser);
        }
    });
}

/**
* Initialization function for the
* configure track panel
*/
function initGDV_configure(){
    dojo.require("dijit.ColorPalette");
    console.log("configure");
    dojo.addOnLoad(function() {
        dojo.parser.parse();
        var color_picker = dijit.byId('color_picker');
        console.log(color_picker);
        dojo.connect(color_picker,"onChange",function(event){
            console.log(dojo.byId('color_input'));
            console.log(color_picker);
        });
    });


}

/**
* Undocumented
*/
function initGDV_prez(){
    dojo.addOnLoad(function() {
        //dojo.parser.parse();
        var cont = dojo.byId('gdv_prez');
        var foo = new dojox.image.SlideShow({autoload:true,fixedHeight:true,id:'gdv_prez',hasNav:true},cont);


         /* the images */
         var data = {items: [
         {"index":'1',"img":"../public/img/epfl-logo.jpeg","title":"logo epfl"},
         {"index":'2',"img":"../public/img/noimage.jpeg","title":"no image"},
         {"index":'3',"img":"../public/img/logo_gdv.jpg","title":"logo GDV"}
                 ]};

         var imageItemStore = new dojo.data.ItemFileReadStore({data:data});
        var request= {query: {},count:20};
        var itemNameMap = {imageLargeAttr: "img"};
         dijit.byId('gdv_prez').setDataStore(imageItemStore,request,itemNameMap);

    });
}
