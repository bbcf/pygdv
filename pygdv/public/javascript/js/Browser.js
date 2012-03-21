/*
 * Construct a new Browser object.
 * @class This class is the main interface between JBrowse and embedders
 * @constructor
 * @param params a dictionary with the following keys:
 * containerID:     ID of the HTML element that contains the browser
 * refSeqs:         list of reference sequence information items (usually from refSeqs.js)
 * trackData:       list of track data items (usually from trackInfo.js)
 * dataRoot:        (optional) URL prefix for the data directory
 * styleRoot:       (optional) URL prefix for the css and img directories
 * browserRoot:     (optional) URL prefix for the browser code
 * tracks:          (optional) comma-delimited string containing initial list of tracks to view
 * location:        (optional) string describing the initial location
 * defaultTracks:   (optional) comma-delimited string containing initial list of tracks to view if there are no cookies
 *                  and no "tracks" parameter
 * defaultLocation: (optional) string describing the initial location if there are no cookies and no "location" parameter
 */

var Browser = function(params) {
    // Dojo dependencies
    dojo.require("dojo.dnd.Source");
    dojo.require("dojo.dnd.Moveable");
    dojo.require("dojo.dnd.Mover");
    dojo.require("dojo.dnd.move");
    dojo.require("dijit.layout.ContentPane");
    dojo.require("dijit.layout.BorderContainer");
    dojo.require("dijit.layout.AccordionContainer");
    dojo.require("dijit.form.Slider");

    // Copy params variables
    var refSeqs   = params.refSeqs;
    var trackData = params.trackData;

    // Two different roots for data and for img/css files
    if ("dataRoot" in params)  {this.dataRoot  = params.dataRoot;}
    else                       {this.dataRoot  = "";}
    if ("styleRoot" in params) {this.styleRoot = params.styleRoot;}
    else                       {this.styleRoot = "";}
    if ("imageRoot" in params)  {this.imageRoot  = params.imageRoot;}
    else                       {this.imageRoot  = "";}
    // A global variable in JavaScript is done like this
    window.picsPathRoot = this.imageRoot;

    // Undocumented
    this.deferredFunctions = [];

    // Get tracks
    //this.names = new LazyTrie(this.dataRoot + "data/names/lazy-", this.dataRoot + "data/names/root.json");
    this.tracks = [];
    var brwsr = this;
    brwsr.isInitialized = false;

    // Execute this function on load
    dojo.addOnLoad( function() {

        // Specify the dojo css skin
        dojo.addClass(document.body, "tundra");

        // Set up container
        brwsr.container = dojo.byId(params.containerID);
        brwsr.container.genomeBrowser = brwsr;

        // The element "topPane" is setup
        // It will contain the "navbox" element
        var topPane = document.createElement("div");
        topPane.id = "topPane";
        brwsr.container.appendChild(topPane);

        // The navbox will be the only child of topPane
        // and will contain buttons, search field and
        // the minimap (which is called overview)
        navbox = brwsr.createNavBox(params);
        topPane.appendChild(navbox);

        // viewElem is the second div and contains one GenomeView
        var viewElem = document.createElement("div");
        viewElem.id = "viewElem";
        viewElem.className = "dragWindow";
        brwsr.container.appendChild(viewElem);

        // menu at the left
        var menuleft = document.createElement('div');
        menuleft.id ='gdv_menu';
        brwsr.container.appendChild(menuleft);

        // container at bottom
        // var bottomPane = document.createElement('div');
        // bottomPane.id='bottomPane';
        // bottomPane.className='bottomPane';
        // brwsr.container.appendChild(bottomPane);

        // Set up page layout
        var containerWidget = new dijit.layout.BorderContainer({
            //liveSplitters: false,
            design: "sidebar",
            gutters: false
        }, brwsr.container);

        var contentWidget = new dijit.layout.ContentPane({region: "top"}, topPane);
        var browserWidget = new dijit.layout.ContentPane({region: "center"}, viewElem);
        var menuWidget = new dijit.layout.ContentPane({region: "left", splitter:false,
                                                       style : {overflow:'hidden'}}, menuleft);

        //add a layout for the operation form
        var formElem = dojo.create('div', {id:'op_form'}, brwsr.container);
        var formWidget = new dijit.layout.ContentPane({region: "right", splitter:false,
                                                       style : {overflow:'hidden'}}, formElem);
        //var bottomWidget = new dijit.layout.ContentPane({region: "bottom",splitter:true}, bottomPane);

        // This creates the permalink to the current chr and loc
        if (params.bookmark) {
            this.link = document.createElement("a");
            this.link.appendChild(document.createTextNode("Link"));
            this.link.href = window.location.href;
            dojo.connect(this, "onCoarseMove", function() {brwsr.link.href = params.bookmark(brwsr);});
            dojo.connect(this, "onVisibleTracksChanged", function() {brwsr.link.href = params.bookmark(brwsr);});
            this.link.style.cssText = "float: right; clear";
            viewElem.appendChild(this.link);
        }

        // When content overflows it should not overlap
        topPane.style.overflow="hidden";

        // Set up ref seqs
        brwsr.allRefs = {};
        for (var i = 0; i < refSeqs.length; i++)
            brwsr.allRefs[refSeqs[i].name] = refSeqs[i];

        // Check for cookie
        var refCookie = dojo.cookie(params.containerID + "-refseq");
        brwsr.refSeq = refSeqs[0];
        for (i = 0; i < refSeqs.length; i++) {
            brwsr.chromList.options[i] = new Option(refSeqs[i].name, refSeqs[i].name);
            if (refSeqs[i].name.toUpperCase() == String(refCookie).toUpperCase()) {
                brwsr.refSeq = brwsr.allRefs[refSeqs[i].name];
                brwsr.chromList.selectedIndex = i;
            }
         }

        // Connect something
        dojo.connect(brwsr.chromList, "onchange", function(event) {
            var oldLocMap = dojo.fromJson(dojo.cookie(brwsr.container.id + "-location")) || {};
            var newRef = brwsr.allRefs[brwsr.chromList.options[brwsr.chromList.selectedIndex].value];

            if (oldLocMap[newRef.name]){
                var oldLoc = oldLocMap[newRef.name];
                if (oldLoc == 'NaN .. NaN'){
                    brwsr.navigateTo(newRef.name + ":"
                                 + (((newRef.start + newRef.end) * 0.4) | 0)
                                 + " .. "
                                 + (((newRef.start + newRef.end) * 0.6) | 0));
                } else {
                    brwsr.navigateTo(newRef.name + ":" + oldLoc);
                }
            } else {
                    brwsr.navigateTo(newRef.name + ":"
                                 + (((newRef.start + newRef.end) * 0.4) | 0)
                                 + " .. "
                                 + (((newRef.start + newRef.end) * 0.6) | 0));
            }
        });

        // Hook up GenomeView
        var gv = new GenomeView(viewElem, 250, brwsr.refSeq, 1/200);
        brwsr.view = gv;
        brwsr.viewElem = viewElem;
        viewElem.view = gv;

        // Connect something
        dojo.connect(browserWidget, "resize", function() {
                gv.sizeInit();
                brwsr.view.locationTrapHeight = dojo.marginBox(navbox).h;
                gv.showVisibleBlocks();
                gv.showCoarse();
        });
        brwsr.view.locationTrapHeight = dojo.marginBox(navbox).h;

        // Connect Browser.js function and GenomeView.js function
        dojo.connect(gv, "onCoarseMove", brwsr, "onCoarseMove");
        // Set up the menu at the left
        brwsr.buildLeftMenu(menuleft);

        // Set up principal container
        _gdv_pc = new PrincipalContainer();
        _gdv_pc.createContainer(brwsr, menuleft, formElem, formWidget, containerWidget);

        // Set up track list
        brwsr.createTrackList(brwsr.container,brwsr.tab_tracks.domNode, params);

        containerWidget.startup();
        brwsr.isInitialized = true;

        // Switch to the last visited menu element
        _gdv_pc.setOnclickMenuElement();
        _gdv_pc.switchMenuElement();

        // Set initial location
        var oldLocMap = dojo.fromJson(dojo.cookie(brwsr.container.id + "-location")) || {};
        if (params.location) {
            brwsr.navigateTo(params.location);
        } else if (oldLocMap[brwsr.refSeq.name]) {
            brwsr.navigateTo(brwsr.refSeq.name + ":" + oldLocMap[brwsr.refSeq.name]);
        } else if (params.defaultLocation){
            brwsr.navigateTo(params.defaultLocation);
        } else {
            brwsr.navigateTo(brwsr.refSeq.name
                             + ":"
                             + ((((brwsr.refSeq.start + brwsr.refSeq.end) * 0.4) | 0)
                             + " .. "
                             + (((brwsr.refSeq.start + brwsr.refSeq.end) * 0.6) | 0)));
        }

        // Update the position of the zoom slider
        dijit.byId("zoom_slider")._setValueAttr(brwsr.view.curZoom);

        // If someone calls methods on this browser object
        // before it's fully initialized, then we defer
        // those functions until now
        for (var i = 0; i < brwsr.deferredFunctions.length; i++) {brwsr.deferredFunctions[i]();}
        brwsr.deferredFunctions = [];

        // Initializes the GDV canvas
        initCanvas();
    });
};

/**
 * Build the menu on the left
 * @param{container} - the HTML div containing the menu
 */
Browser.prototype.buildLeftMenu = function(container){

    // /* Navigation menu */
    // var navig = document.createElement('div');
    // navig.innerHTML='Navigation';
    // navig.className='menu_entry';
    // container.appendChild(navig);

    // /* Admin var */
    // var admin = dojo.byId('is_admin');

    // /* Links */
    //     if(admin.innerHTML=='false'){
    //     container.appendChild(this.buildMenuItem('login','Copy in profile'));
    // } else {
    //     container.appendChild(this.buildMenuItem('home','Home'));
    //     container.appendChild(this.buildMenuItem('admin','Admin'));
    //     container.appendChild(this.buildMenuItem('projects','Projects'));
    //     container.appendChild(this.buildMenuItem('preferences','Preferences'));
    //     container.appendChild(this.buildMenuItem('help','Help'));
    // }
};

/**
 * Helper to build a menu item
 */
Browser.prototype.buildMenuItem = function(link_end, link_name){
    // Create a container and link
    var cont = document.createElement('div');
    var link = document.createElement('a');
    cont.appendChild(link);
    // Make an image
    var img = document.createElement('img');
    img.src = this.imageRoot + "menu_" + link_end + ".png";
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
    // Return the container
    return cont;
};



/**
 * Generic function to sort a list of the same objects by a given key
 * @field: object key
 * @reverse = true for high to low, false for low to high
 * @primer: transformation to apply before comparison
 * Example: X.sort(sort_by('price', true, parseInt));
 */
var sort_by = function(field, reverse, primer){
   var key = function (x) {return primer ? primer(x[field]) : x[field]};
   return function (a,b) {
       var A = key(a), B = key(b);
       if (isNaN(A) && isNaN(B)) A = A.toLowerCase(); B = B.toLowerCase();
       return ((A < B) ? -1 :
               (A > B) ? +1 : 0) * [-1,1][+!!reverse];
   }
}


/**
 * Create the HTML panel that will contain
 * all tracks not loaded and set up the
 * machinery to accept the DnD with dojo
 * N.B : the leftPanel is now on the
 * bottom with a div which can show or hide the panel
 */
Browser.prototype.createTrackList = function(container,tab_tracks, params) {

    ctx = this;

    // Buttons to sort tracks
    var sort = dojo.create("table", {id: "tracksSort"}, tab_tracks);
    var sorttr = dojo.create("tr", null, sort);
    var sortByName = dojo.create("td", {innerHTML: "By name"}, sorttr);
    var sortByType = dojo.create("td", {innerHTML: "By type"}, sorttr);
    var sortByDate = dojo.create("td", {innerHTML: "By date"}, sorttr);

    // Get list of tracks
    //tracks_info = dojo.cookie("GenomeBrowser-tracks");
    //console.log(tracks_info);
    labels = dojo.query(".tracklist-label");
    console.log(labels);
    nlabels = labels.length;
    console.log(labels[0].innerHTML)
    trackList = [];
    for (var i=0; i<nlabels; i++){ trackList.push(labels[i].innerHTML); }

    // Connect the buttons to sorting functions
    dojo.connect(sortByName, 'click', function(e){
        trackList.sort(sort_by('innerHTML', true, null));
        trackList = ','.join(trackList);
        console.log(trackList)
        //dojo.cookie("GenomeBrowser-tracks", trackList);
        //ctx.createTrackList(container,tab_tracks, params);
    });
    dojo.connect(sortByType, 'click', function(e){
        //trackList.sort('type', true, null);
    });
    dojo.connect(sortByDate, 'click', function(e){ trackList.sort('date', true, parseDate);

    });

    // Container of tracks
    var trackListDiv = dojo.create("div", {id: "tracksAvail",
                className: "container handles"},
                tab_tracks);
    dojo.create("div", {id:"tracksExplain",
                innerHTML: "Drag and Drop tracks to view/hide"},
                trackListDiv);

    // Copy self object
    var brwsr = this;

    // Callback function
    var changeCallback = function() {brwsr.view.showVisibleBlocks(true);};

    // Populates tracksAvail with divs
    var trackListCreate = function(track, hint) {
        // The little block containing the track name
        var node = dojo.create("div",
                { id: dojo.dnd.getUniqueId(),
                  className: "tracklist-label",
                  innerHTML: track.key } );
        var node_inner = dojo.create("table",null,node);
        var node_inner_tr = dojo.create("tr",null,node_inner);
        var node_name = dojo.create("td",{className:"node_inner_td"},node_inner_tr);
        var node_type = dojo.create("td",{className:"node_inner_td"},node_inner_tr);
        var node_data = dojo.create("td",{className:"node_inner_td"},node_inner_tr);
        // In the list, wrap the list item in a container for
        // border drag-insertion-point monkeying
        if ("avatar" != hint) {
            var container = dojo.create("div", {className: "tracklist-container"});
            container.appendChild(node);
            node = container;
        }
        return {node: node, data: track, type: ["track"]};
    };

    // Undocumented
    this.trackListWidget = new dojo.dnd.Source(trackListDiv,
                       {creator: trackListCreate,
                        accept: ["track"],
                        selfAccept:false,
                        withHandles: false});

    // Undocumented
    var trackCreate = function(track, hint) {
        if ("avatar" == hint) {
            return trackListCreate(track, hint);
        } else {
            var replaceData = {refseq: brwsr.refSeq.name};
            var url = track.url.replace(/\{([^}]+)\}/g, function(match, group) {return replaceData[group];});
            var klass = eval(track.type);
            var newTrack = new klass(track, url, brwsr.refSeq,
                                     {
                                         changeCallback: changeCallback,
                                         trackPadding: brwsr.view.trackPadding,
                                         baseUrl: brwsr.dataRoot,
                                         charWidth: brwsr.view.charWidth,
                                         seqHeight: brwsr.view.seqHeight
                                     });
        var node = brwsr.view.addTrack(newTrack);
        }
        return {node: node, data: track, type: ["track"]};
    };

    // Drag and drop stuff
    this.viewDndWidget = new dojo.dnd.Source(this.view.zoomContainer,
                         {copyState:function(keyPressed,self){
                             // if(_tc.tab_form){
                 //      if(_tc.tab_form.selected){
                             //         return true;
                 //      }
                             // }
                             return false;
                         },creator: trackCreate, accept: ["track"], withHandles: true});
    dojo.subscribe("/dnd/drop", function(source,nodes,iscopy) {
        brwsr.onVisibleTracksChanged();
    });

    // Undocumented
    this.trackListWidget.insertNodes(false, params.trackData);
    var oldTrackList = dojo.cookie(this.container.id + "-tracks");
    if (params.tracks) {
        this.showTracks(params.tracks);
    } else if (oldTrackList) {
        this.showTracks(oldTrackList);
    } else if (params.defaultTracks) {
        this.showTracks(params.defaultTracks);
    }
};

/**
 * Undocumented
 */
Browser.prototype.onVisibleTracksChanged = function() {
    this.view.updateTrackList();
    var trackLabels = dojo.map(this.view.tracks, function(track) {
        return track.name;
    });
    var oldTrackList = dojo.cookie(this.container.id + "-tracks");
    dojo.cookie(this.container.id + "-tracks", trackLabels.join(","), {expires:60});
    this.view.showVisibleBlocks();
};

/**
 * Add new tracks to the track list
 * @param trackList list of track information items
 * @param replace true if this list of tracks should replace any existing
 * tracks, false to merge with the existing list of tracks
 */
Browser.prototype.addTracks = function(trackList, replace) {
    if (!this.isInitialized) {
        var brwsr = this;
        this.deferredFunctions.push(
            function() {brwsr.addTracks(trackList, show); }
        );
        return;
    }

    this.tracks.concat(trackList);
    if (show || (show === undefined)) {
        this.showTracks(dojo.map(trackList,
                                 function(t) {return t.label;}).join(","));
    }
};

/**
 * Navigate to a given location
 * @example
 * gb=dojo.byId("GenomeBrowser").genomeBrowser
 * gb.navigateTo("ctgA:100..200")
 * gb.navigateTo("f14")
 * @param loc can be either:
 * chromosome: start .. end;
 * start .. end;
 * center base;
 * feature name;
 */
Browser.prototype.navigateTo = function(loc,tag) {
    if (!this.isInitialized) {
    var brwsr = this;
        this.deferredFunctions.push(function() { brwsr.navigateTo(loc); });
        return;
    }
    loc = dojo.trim(loc);
    //                                (chromosome)    (    start      )   (  sep     )     (    end   )
    var matches = String(loc).match(/^(((\S*)\s*:)?\s*(-?[0-9',.]*[0-9])\s*(\.\.|-|\s+))?\s*(-?[0-9',.]+)$/i);
    // Matches potentially contains location components:
    // matches[3] = chromosome (optional)
    // matches[4] = start base (optional)
    // matches[6] = end base (or center base, if it's the only one)
    if (matches) {
        if (matches[3]) {
            var refName;
            for (ref in this.allRefs) {
            if ((matches[3].toUpperCase() == ref.toUpperCase())
                 || ("CHR" + matches[3].toUpperCase() == ref.toUpperCase())
                 || (matches[3].toUpperCase() == "CHR" + ref.toUpperCase()))
                 {refName = ref;}
            }
            if (refName) {
                dojo.cookie(this.container.id + "-refseq", refName, {expires: 60});
                if (refName == this.refSeq.name) {
                    // Go to given start, end on current refSeq
                    this.view.setLocation(this.refSeq,
                              parseInt(matches[4].replace(/[',.]/g, "")),
                              parseInt(matches[6].replace(/[',.]/g, "")));
                } else {
                    // New refseq, record open tracks and re-open on new refseq
                    var curTracks = [];
                    this.viewDndWidget.forInItems(function(obj, id, map) {curTracks.push(obj.data);});
                    for (var i = 0; i < this.chromList.options.length; i++)
                    if (this.chromList.options[i].text == refName) {this.chromList.selectedIndex = i;}
                    this.refSeq = this.allRefs[refName];
                    // Go to given refseq, start, end
                    this.view.setLocation(this.refSeq,
                              parseInt(matches[4].replace(/[',.]/g, "")),
                              parseInt(matches[6].replace(/[',.]/g, "")));
                    this.viewDndWidget.insertNodes(false, curTracks);
                    this.onVisibleTracksChanged();
                }
                return;
            }
        } else if (matches[4]) {
            // Go to start, end on this refseq
            this.view.setLocation(this.refSeq,
                      parseInt(matches[4].replace(/[',.]/g, "")),
                      parseInt(matches[6].replace(/[',.]/g, "")));
            return;
        } else if (matches[6]) {
            // Center at given base
            this.view.centerAtBase(parseInt(matches[6].replace(/[',.]/g, "")));
            return;
        }
    }
    // If we get here, we didn't match any expected location format
    // add our own gene name indexing
    _gdvls.search(loc,this.refSeq.name);

    // var brwsr = this;
    // this.names.exactMatch(loc, function(nameMatches) {
    //     var goingTo;
    //     //first check for exact case match
    //     for (var i = 0; i < nameMatches.length; i++) {
    //     if (nameMatches[i][1] == loc)
    //         goingTo = nameMatches[i];
    //     }
    //     //if no exact case match, try a case-insentitive match
    //         if (!goingTo) {
    //             for (var i = 0; i < nameMatches.length; i++) {
    //                 if (nameMatches[i][1].toLowerCase() == loc.toLowerCase())
    //                     goingTo = nameMatches[i];
    //             }
    //         }
    //         //else just pick a match
    //     if (!goingTo) goingTo = nameMatches[0];
    //     var startbp = goingTo[3];
    //     var endbp = goingTo[4];
    //     var flank = Math.round((endbp - startbp) * .2);
    //     //go to location, with some flanking region
    //     brwsr.navigateTo(goingTo[2]
    //              + ":" + (startbp - flank)
    //              + ".." + (endbp + flank));
    //     brwsr.showTracks(brwsr.names.extra[nameMatches[0][0]]);
    //});
};

/**
 * Load and display the given tracks
 * @example
 * gb=dojo.byId("GenomeBrowser").genomeBrowser
 * gb.showTracks("DNA,gene,mRNA,noncodingRNA")
 * @param trackNameList {String} comma-delimited string containing track names,
 * each of which should correspond to the "label" element of the track
 * information dictionaries
 */
Browser.prototype.showTracks = function(trackNameList) {
    var brwsr = this;
    if (!this.isInitialized) {
        this.deferredFunctions.push(function() {brwsr.showTracks(trackNameList);});
        return;
    }
    if(!trackNameList){return;}
    var trackNames = trackNameList.split(",");
    var removeFromList = [];
    for (var n = 0; n < trackNames.length; n++) {
        this.trackListWidget.forInItems(function(obj, id, map) {
            if (trackNames[n] == obj.data.label) {
                brwsr.viewDndWidget.insertNodes(false, [obj.data]);
                removeFromList.push(id);
            }
        });
    }
    var movedNode;
    for (var i = 0; i < removeFromList.length; i++) {
    this.trackListWidget.delItem(removeFromList[i]);
    movedNode = dojo.byId(removeFromList[i]);
    if (movedNode) movedNode.parentNode.removeChild(movedNode);
    }
    this.onVisibleTracksChanged();
};

/**
 * @returns {String} string representation of the current location<br>
 * (suitable for passing to navigateTo)
 */
Browser.prototype.visibleRegion = function() {
    return this.view.ref.name + ":" + Math.round(this.view.minVisible()) + ".." + Math.round(this.view.maxVisible());
};

/**
 * @returns {String} containing comma-separated list of currently-viewed tracks<br>
 * (suitable for passing to showTracks)
 */
Browser.prototype.visibleTracks = function() {
    var trackLabels = dojo.map(this.view.tracks,
                               function(track) { return track.name; });
    return trackLabels.join(",");
};

/**
 * Undocumented
 */
Browser.prototype.onCoarseMove = function(startbp, endbp) {
    var length = this.view.ref.end - this.view.ref.start;
    var trapLeft = Math.round((((startbp - this.view.ref.start) / length) * this.view.overviewBox.w) + this.view.overviewBox.l);
    var trapRight = Math.round((((endbp - this.view.ref.start) / length) * this.view.overviewBox.w) + this.view.overviewBox.l);

    // CSS positioning
    this.view.locationThumb.style.height = (this.view.overviewBox.h - 4) + "px";
    this.view.locationThumb.style.left   = trapLeft                      + "px";
    this.view.locationThumb.style.width  = (trapRight - trapLeft)        + "px";
    this.view.locationThumb.style.zIndex = '20';

    // Since this method gets triggered by the initial GenomeView.sizeInit,
    // we don't want to save whatever location we happen to start at
    if (! this.isInitialized) return;
    var locString = Util.addSeperator(Math.round(startbp)) + " .. " + Util.addSeperator(Math.round(endbp));
    this.goButton.disabled = true;
    this.locationBox.blur();
    var oldLocMap = dojo.fromJson(dojo.cookie(this.container.id + "-location"));
    if ((typeof oldLocMap) != "object") oldLocMap = {};
    oldLocMap[this.refSeq.name] = locString;
    dojo.cookie(this.container.id + "-location", dojo.toJson(oldLocMap), {expires: 60});

    // Change the window title
    document.title = this.refSeq.name + ":" + locString;
};

/**
 * Creates the only child of the topPane element.
 * Contains the move/select buttons,
 * the chromosome drop down menu,
 * the chromosome minimap,
 * the zoom silder,
 * the search field and button.
 */
Browser.prototype.createNavBox = function(params) {
    // Copy self object
    var brwsr = this;

    // Three part navbox
    var navbox = document.createElement("div");
    navbox.id = "navbox";
    navbox.style.cssText = "z-index: 10;";
    var navbox_left   = document.createElement("div");
    var navbox_middle = document.createElement("div");
    var navbox_right  = document.createElement("div");
    navbox_left.id = "navbox_left";
    navbox_middle.id = "navbox_middle";
    navbox_right.id = "navbox_right";
    navbox.appendChild(navbox_left);
    navbox.appendChild(navbox_middle);
    navbox.appendChild(navbox_right);

    // ------------Navbox left--------------
    // Select or move buttons
    var disableSel = document.createElement("input");
    disableSel.type = "image";
    disableSel.src = brwsr.imageRoot + "button_move.png";
    disableSel.id = "disableSel";
    disableSel.className = "icon nav";
    disableSel.style.height = "26px";
    disableSel.title = "Move around";
    dojo.connect(disableSel, "click", function(e) {brwsr.view.zoneSel.disableSel(e);});
    navbox_left.appendChild(disableSel);
    var enableSel = document.createElement("input");
    enableSel.type = "image";
    enableSel.src = brwsr.imageRoot + "button_select.png";
    enableSel.id = "enableSel";
    enableSel.className = "icon nav";
    enableSel.style.height = "26px";
    enableSel.title = "Draw selections";
    dojo.connect(enableSel, "click",  function(e) {brwsr.view.zoneSel.enableSel(e);});
    navbox_left.appendChild(enableSel);
    navbox_left.appendChild(document.createTextNode("\u00a0\u00a0\u00a0"));
    // Chromosome drop down menu
    this.chromList = document.createElement("select");
    this.chromList.style.width = "80px";
    this.chromList.style.cssText = "width: 80px; vertical-align: middle";
    this.chromList.id = "chrom";
    this.chromList.title = "Change chromosome";
    navbox_left.appendChild(this.chromList);

    // ------------Navbox middle--------------
    // Minimap
    // (overview means chromosome minimap here)
    var overview = document.createElement("div");
    overview.className = "overview";
    overview.style.cssText = "display: inline-block;";
    overview.id = "overview";
    navbox_middle.appendChild(overview);

    // ------------Navbox right--------------
    // Zoom slider
    var navbox_silder  = document.createElement("div");
    navbox_silder.id = "navbox_silder";
    navbox.appendChild(navbox_silder);
    var zoomSlider = new dijit.form.HorizontalSlider({
           name: "zoom_slider",
           id: "zoom_slider",
           value: 0,
           minimum: 0,
           maximum: 19,
           discreteValues: 20,
           intermediateChanges: false,
           style: "width: 178px;",
           onChange: function(value) {brwsr.view.zoomTo(value);}
       },
       "zoom_slider");
    navbox_silder.title = "Change the zoom level";
    navbox_silder.appendChild(zoomSlider.domNode);
    // Search button
    this.goButton = document.createElement("input");
    this.goButton.type = "image";
    this.goButton.src = brwsr.imageRoot + "button_search.png";
    this.goButton.disabled = true;
    dojo.connect(this.goButton, "click",
        function(event) {
            brwsr.navigateTo(brwsr.locationBox.value);
            brwsr.goButton.disabled = true;
            dojo.stopEvent(event);
        });
    navbox_right.appendChild(this.goButton);
    navbox_right.appendChild(document.createTextNode("\u00a0\u00a0"));
    // Search field
    this.locationBox = document.createElement("input");
    if (dojo.isIE) {this.locationBox.type="text";  }
    else           {this.locationBox.type="search";}
    this.locationBox.id="location";
    this.locationBox.style.cssText = "width: 130px; vertical-align: top;";
    dojo.connect(this.locationBox, "keydown", function(event) {
    if (event.keyCode == dojo.keys.ENTER) {
            brwsr.navigateTo(brwsr.locationBox.value);
            brwsr.goButton.disabled = true;
            dojo.stopEvent(event);
        } else {
            brwsr.goButton.disabled = false;
        }
    });
    // //add connection of the locationBox to a suggest search field
    // dojo.connect(this.locationBox, "keyup", function(event) {
    //         var field = brwsr.locationBox.value;
    //         if (field.length>2){
    //         gdvls.search(field,brwsr.refSeq.name);
    //         //lookupGeneNames_searchNames(field,brwsr.refSeq.name);
    //         dojo.stopEvent(event);
    //         }
    //     });

    navbox_right.appendChild(this.locationBox);

    // Suggest fields
    var suggest_field = document.createElement("div");
    suggest_field.id="suggest_field";
    suggest_field.style.cssText = "width: 130px; vertical-align: top;";
    suggest_field.style.display = "none";
    navbox_right.appendChild(suggest_field);

    navbox_right.appendChild(document.createTextNode("\u00a0\u00a0"));

    // Long tool tip
    tooltip = "You can type either a position on the chromosome, an interval or even the name of a feature here.";
    this.locationBox.title = tooltip;
    this.goButton.title    = tooltip;

    // Return a div object
    return navbox;
};

/**********************************************************************
Copyright (c) 2007-2011 The Evolutionary Software Foundation

Created by Mitchell Skinner <mitch_skinner@berkeley.edu>
Modified by Lucas Sinclair <lucas.sinclair@epfl.ch>
Modified by Yohan Jarosz <yohan.jarosz@epfl.ch>

This package and its accompanying libraries are free software; you can
redistribute it and/or modify it under the terms of the LGPL (either
version 2.1, or at your option, any later version) or the Artistic
License 2.0.  Refer to LICENSE for the full license text.
***********************************************************************/
