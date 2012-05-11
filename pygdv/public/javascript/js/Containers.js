/**
* Create all containers in the browser view.
*/

function PrincipalContainer(){}


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
PrincipalContainer.prototype.show_jobs = function(){
    this.principal_dijit.selectChild('tab_jobs');
};
PrincipalContainer.prototype.reset = function(){
    this.principal_dijit.selectChild('tab_fake');
};



/**
* Create the CONTAINER for tracks, selections, operation, ...
* Will create the Accordion container.
*/
PrincipalContainer.prototype.createContainer = function(browser, menuLeftContainer, viewContainer, formwidget, browserwidget){
    // the principal container and the corresponding dijit container
    var principal = dojo.create('div', {id : 'principal_cont'}, menuLeftContainer);
    var principal_dijit = new dijit.layout.AccordionContainer({
        style: "height: 100%; width: 100%;",

        },
        principal);
    this.principal = principal;
    this.principal_dijit = principal_dijit;

    // init some parameters
    var menu_nav = ['Home', 'Tracks', 'Projects', 'Circles', 'Jobs'];
    if (!_gdv_info.admin){
        init_operations = ['You must be logged in to use operations'];
        jobs = ['You must be logged in to view jobs'];
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
    this.jobContainer(principal, principal_dijit);
    if (init_operations == 'connect'){
        console.error('cannot connect to plugin system');
    } else {
        this.operationContainer(principal, principal_dijit, init_operations, viewContainer, formwidget, browserwidget);
    }
    this.fakeContainer(principal, principal_dijit);

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
        var but = buttons[i];
        but.tab = dojo.query(".dijitContentPane", but.parentNode)[0];
        but.open = 1;
        dojo.connect(but, "click", function(e){
            document.activeElement.blur(); // else if interacts with keyb events
            ctx.menu_current_tab = this.firstElementChild.lastElementChild.innerHTML;
            // if active tab is clicked again, close it
            if (dojo.cookie("menu_current_tab") == ctx.menu_current_tab){
                if (this.open == 1){
                    ctx.reset();
                    dojo.cookie("menu_current_tab", "Fake");
                    this.open = 0;
                } else {
                    this.open = 1;
                }
            // if a different tab is clicked, change for it
            } else {
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
    case "Fake"      : this.reset(); break;
    case "Jobs"      : this.show_jobs(); break;
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
    dojo.cookie("Menu-tracks");
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


    // initialize the print button
    // var bilou = dojo.create('input', {type:'button', value:'print'},cont);
    // dojo.connect(bilou, 'click', function(e){
    //     var trs = dojo.query('.track.dojoDndItem');
    //     console.log(trs);
    //     window.print();
    //     dojo.stopEvent(e);
    // });

};


/**
* Add a fake tab for the "reset" effect if a menu item is clicked twice
*/
PrincipalContainer.prototype.fakeContainer = function(DomNode, DijitNode){
    var fake = dojo.create('div', {}, DomNode);
    var fake_container = new dijit.layout.ContentPane({
        title: "Fake",
        id:'tab_fake',
    }, fake);
    DijitNode.addChild(fake_container);
    this.fake = fake_container;
};




/**
* Add the Jobs tab
*/
PrincipalContainer.prototype.jobContainer = function(DomNode, DijitNode){
    var job_manager = new JobPane();
    job_manager.init_panel(DomNode, DijitNode);
    this.jobs = job_manager;
};
