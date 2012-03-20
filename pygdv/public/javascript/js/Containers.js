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
PrincipalContainer.prototype.createContainer = function(browser, menuLeftContainer, viewContainer, formwidget, browserwidget){
    // the principal container and the corresponding dijit container
    var principal = dojo.create('div', {id : 'principal_cont'}, menuLeftContainer);
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
    }

    // create additionnal children containers
    this.navigationContainer(principal, principal_dijit, menu_nav);
    this.trackContainer(browser);
    this.selectionContainer(principal, principal_dijit);
    this.operationContainer(principal, principal_dijit, init_operations, viewContainer, formwidget, browserwidget);

    // Retrieve from a cookie the last element of menu selected
    if (dojo.cookie("menu_current_tab")) {
        this.menu_current_tab = dojo.cookie("menu_current_tab");
    } else { //create a new cookie
        this.menu_current_tab = "Navigation";
        dojo.cookie("menu_current_tab", this.menu_current_tab);
    }

    return principal;
};


/*
* Updates the 'menu_current_tab' cookie on click on a menu element
*/
PrincipalContainer.prototype.setOnclickMenuElement = function(){
    var ctx = this;
    var buttons = dojo.query(".dijitAccordionTitle", this.principal);
    var bl = buttons.length;
    for (var i=0; i<bl; i++) {
        b = buttons[i];
        b.tab = dojo.query(".dijitContentPane", b.parentNode)[0];
        b.open = 1;
        dojo.connect(b, "click", function(e){
            ctx.menu_current_tab = this.firstElementChild.lastElementChild.innerHTML;
            if (dojo.cookie("menu_current_tab") == ctx.menu_current_tab){ // if active tab is clicked again
            //// Trial to hide a tab if it is clicked twice, show again if clicked again
            //    if (this.open == undefined){
            //        this.tab.past_height = this.tab.offsetHeight+"px";
            //        this.open = 1;
            //    } else if (this.open == 1) { // if open, close it
            //        this.tab.style.cssText = "display: none !important";
            //        this.open = 0;
            //    } else { // if already close or 'undefined', open it
            //        ctx.principal_dijit.selectChild(this.tab.id)
            //            //this.tab.style.display = "block";
            //            //this.tab.style.height = this.tab.past_height;
            //                //ctx.show_operations();
            //        this.open = 1;
            //    }
                if (this.open == 1){
                    ctx.show_operations();
                    this.open = 0;
                } else {
                    this.open = 1;
                }
            } else { // if a different tab is clicked
                dojo.cookie("menu_current_tab", ctx.menu_current_tab);
                this.open = 1;
            }
            dojo.stopEvent(e);
        });
    }
}

/*
* Switch to the last visited menu element
*/
PrincipalContainer.prototype.switchMenuElement = function(){
    switch (this.menu_current_tab){
        case "Navigation": this.show_navigation(); break;
        case "Selections": this.show_selections(); break;
        case "Operations": this.show_operations(); break;
        case "Tracks"    : this.show_tracks(); break;
        default: console.log("ProgrammingError: cannot retrieve menu_current_tab from cookie.");
    }
}


/**
* Add the Track tab
*/
PrincipalContainer.prototype.trackContainer = function(browser){
    // add the tracks container
    var track_container = new dijit.layout.ContentPane({
        title: "Tracks",
        id: 'tab_tracks'
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

    var nav_table = dojo.create("table", {
                         id:"nav_table",
                         style: {width:"100%"}
                      }, cont);
    var new_tr;
    var len = menu_nav.length;
    for (var i=0; i<len; i++){
        link_name = menu_nav[i];
        link_end = link_name.toLowerCase();
        if (i%2==0){ new_tr = dojo.create("tr", null, nav_table); }
        var new_button = dojo.create("td", {className:"nav_table_td"}, new_tr);
        var link = dojo.create('a',{
                         href : _GDV_URL + '/' + link_end,
                         className:"nav_cell",
                         id : 'menu_' + link_name,
                      }, new_button);
        var item = dojo.create("table",{className: "gdv_menu_item"}, link);
        var item_label_tr = dojo.create("tr",null,item);
        var item_img_tr = dojo.create("tr",null,item);
        var item_label = dojo.create("td",{className:'gdv_menu_td'},item_label_tr);
        var item_img = dojo.create("td",{className:'gdv_menu_td'},item_img_tr);
        dojo.create("span", {innerHTML: link_name,
                         className: 'nav_span',
                      }, item_label);
        dojo.create('img', {src : window.picsPathRoot + "menu_" + link_end + ".png",
                         className : 'nav_image',
                      }, item_img);
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
PrincipalContainer.prototype.operationContainer = function(DomNode, DijitNode, paths, viewContainer, fwdgt, bwdgt){
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
                   style : {width : '10em'}
               });
    var c = paths.childs;
    var l = c.length;
    for(var i=0;i<l;i++){
        op.menu_add_child(menu, c[i]);
    }
    menu.placeAt('tab_ops');


    // initialize the iframe that will be showed
    // if an user click on an Operation button
    op.create_frame(viewContainer, fwdgt, bwdgt);
};



