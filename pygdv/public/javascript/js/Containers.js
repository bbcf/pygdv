/**
* Create all containers in the browser view.
*/

function PrincipalContainer(){};


/**
* Selectors
*/
PrincipalContainer.prototype.show_selections = function(){
    this.principal_dijit.selectChild('tab_sels');
};
PrincipalContainer.prototype.show_tracks = function(){
    this.principal_dijit.selectChild('tab_tracks');
};
PrincipalContainer.prototype.show_navigation = function(){
    this.principal_dijit.selectChild('tab_navigation');
};
PrincipalContainer.prototype.show_operations = function(){
    this.principal_dijit.selectChild('tab_ops');
};



/**
* Create the CONTAINER for tracks, selections, operation, ...
* Will create the Accordion container.
*/
PrincipalContainer.prototype.createContainer = function(browser, container){
    // the principal container and the corresponding dijit container
    var principal = dojo.create('div', {id : 'principal_cont'}, container);
    var principal_dijit = new dijit.layout.AccordionContainer({
            style: "height: 100%; width: 100%;"
        },
        principal);
    this.principal = principal;
    this.principal_dijit = principal_dijit;

    // init some parameters
    var menu_nav = ['Home', 'Tracks', 'Projects', 'Circles'];
    if (!_gdv_info.admin){
    init_operations = ['You must be logged in to use operations'];
    if (_gdv_info.mode == 'download'){
        menu_nav = ['Home', 'Copy']
    } else {
        menu_nav = ['Home']
    }
    };

    // create additionnal childs containers

    this.navigationContainer(principal, principal_dijit, menu_nav);
    this.trackContainer(browser);
    this.selectionContainer(principal, principal_dijit);
    this.operationContainer(principal, principal_dijit, init_operations);

    return principal;
};



/**
* Add the Track tab
*/
PrincipalContainer.prototype.trackContainer = function(browser){
    // add the tracks container
    var track_container = new dijit.layout.ContentPane({
            title: "Tracks",
        id:'tab_tracks'
    });
    this.principal_dijit.addChild(track_container);
    browser.tab_tracks = track_container;
    this.tracks = track_container;
};

/**
* Add the Navigation tab
*/
PrincipalContainer.prototype.navigationContainer = function(DomNode, DijitNode, menu_nav){

    var cont = dojo.create('div', {}, DomNode);
    var nav_container = new dijit.layout.ContentPane({
        title: "Navigation",
        id:'tab_navigation'
    }, cont);


    var len = menu_nav.length;
    for (var i=0; i<len; i++){
    link_name = menu_nav[i];
    link_end = link_name.toLowerCase();

    var link = dojo.create('a', {href : _GDV_URL + '/' + link_end,
                     className : 'hl',
                     id : 'menu_' + link_name
                    }, cont);
    dojo.create('img', {src : window.picsPathRoot + "menu_" + link_end + ".png",
                className : 'gdv_menu_image'
               }, link);
    dojo.create('span', {innerHTML : link_name,
                 className : 'gdv_menu_item'
                }, link);
    }
    DijitNode.addChild(nav_container);
    this.navigation = nav_container;
};


/**
* Add the Selection tab
*/
PrincipalContainer.prototype.selectionContainer = function(DomNode, DijitNode){
    var cont = dojo.create('div', {}, DomNode);

    var sel_container = new dijit.layout.ContentPane({
        title: "Selections",
        id:'tab_sels'
    }, cont);
    DijitNode.addChild(sel_container);
    this.selections = sel_container;

    // initialize the selection handler
    var sel_handler = _gdv_info.gb.view.zoneSel
    var sp = new SelectionPane(cont, sel_handler);
    sel_handler.sel_pane = sp;
};


/**
* Add the Operations tab
*/
PrincipalContainer.prototype.operationContainer = function(DomNode, DijitNode, paths){
    var cont = dojo.create('div', {}, DomNode);

    var ops_container = new dijit.layout.ContentPane({
        title: "Operations",
        id:'tab_ops'
    }, cont);
    DijitNode.addChild(ops_container);
    this.operations = ops_container;

    // initialize the operations
    var op = new Operations();
    op.pane = cont;
    _gdv_info.operations = op;

    var menu = new dijit.Menu({colspan : 1,
                   style : {width : '10em'
                       }});
    var c = paths.childs;
    var l = c.length;
    for(var i=0;i<l;i++){
    op.menu_add_child(menu, c[i]);
    }
    menu.placeAt('tab_ops');
};



