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
        if (dojo.cookie(brwsr.container.id + "-tracks") == undefined)
            { dojo.cookie(brwsr.container.id + "-tracks", null); }

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
        //brwsr.buildLeftMenu(menuleft);

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

        // Create a minimap object
        var minimap = new Minimap(brwsr,gv);
        gv.minimap = minimap;
        minimap.draw();

        // If someone calls methods on this browser object
        // before it's fully initialized, then we defer those functions until now
        for (var i = 0; i < brwsr.deferredFunctions.length; i++) {
            brwsr.deferredFunctions[i]();
        }
        brwsr.deferredFunctions = [];

        // Initializes the GDV canvas
        initCanvas();

    });
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

    var brwsr = this;

    // Buttons to sort tracks
    // var sort = dojo.create("table", {id: "tracksSort"}, tab_tracks);
    // var sorttr = dojo.create("tr", null, sort);
    // var sortByName_button = dojo.create("td", {innerHTML: "By name"}, sorttr);
    // var sortByType_button = dojo.create("td", {innerHTML: "By type"}, sorttr);
    // var sortByDate_button = dojo.create("td", {innerHTML: "By date"}, sorttr);

    // Create the container of tracks in the left menu
    var tracksAvail = dojo.create("div", {
                id: "tracksAvail",
                className: "container handles"
                }, tab_tracks);
    dojo.create("div", {
                id:"tracksExplain",
                innerHTML: "Drag and Drop tracks to view/hide"
                }, tracksAvail);

    // When a *track* is dropped into tracksAvail, add one node to the list.
    // Dojo.dnd adds a simple div by default, here we personalize the node it creates.
    var trackListCreate = function(track, hint) {
        // The little block containing the track name
        var node = dojo.create("table",
                { id: dojo.dnd.getUniqueId(),
                  className: "pane_table"} );
        var node_inner = dojo.create("table", {className : 'pane_element'}, node);
        var node_inner_tr = dojo.create("tr", {}, node_inner);
        var node_name = dojo.create("td", {className:"pane_unit", innerHTML : track.key}, node_inner_tr);
        //var node_type = dojo.create("td", {className:"pane_unit", innerHTML : track.type}, node_inner_tr);
        var node_data = dojo.create("td", {className:"pane_unit", innerHTML : track.date}, node_inner_tr);
        // In the list, wrap the list item in a container for
        // border drag-insertion-point monkeying
        if ("avatar" != hint) {
            var container = dojo.create("div", {className: "tracklist-container rightclick"});
            container.appendChild(node);
            node = container;
        }
        return {node: node, data: track, type: ["track"]};
    };

    // Make tracksAvail be a drag & drop object,
    // calling trackListCreate for each new element.
    this.trackListWidget = new dojo.dnd.Source(tracksAvail,
                       {creator: trackListCreate,
                        accept: ["track"],
                        selfAccept:false,
                        withHandles: false});

    // Callback function
    var changeCallback = function() {brwsr.view.showVisibleBlocks(true);};

    // When a track is dropped into the main window, add it to the view
    var trackCreate = function(track, hint) {
        if ("avatar" == hint) { // if inactive
            return trackListCreate(track, hint); // add a div in tracksAvail
        } else { // if to be viewed, add it to the View
            var replaceData = {refseq: brwsr.refSeq.name};
            var url = track.url.replace(/\{([^}]+)\}/g, function(match, group) {return replaceData[group];});
            var klass = eval(track.type);
            var newTrack = new klass(track, url, brwsr.refSeq,
                                     {   changeCallback: changeCallback,
                                         trackPadding: brwsr.view.trackPadding,
                                         baseUrl: brwsr.dataRoot,
                                         charWidth: brwsr.view.charWidth,
                                         seqHeight: brwsr.view.seqHeight
                                     });
            var node = brwsr.view.addTrack(newTrack);
        }
        return {node: node, data: track, type: ["track"]};
    };

    // Make this.view.zoomContainer be a drag & drop object,
    // calling trackCreate for each new element.
    this.viewDndWidget = new dojo.dnd.Source(this.view.zoomContainer,
                         { copyState: function(keyPressed,self){
                                if (keyPressed) return true;
                                else return false;
                           },
                           //copyOnly: false,
                           creator: trackCreate,
                           accept: ["track"],
                           withHandles: true
                         });

    // dojo.subscribe: "Register a function to a named topic" (??)
    dojo.subscribe("/dnd/drop", function(source,nodes,iscopy) {
        brwsr.onVisibleTracksChanged();
    });

    // Add a block in #tracksAvail if a track is dragged from the browser
    this.trackListWidget.insertNodes(false, params.trackData);     // populates tracksAvail with nodes

    // Add tracks to the view
    var oldTrackList = dojo.cookie(this.container.id + "-tracks"); // tracks already in the view
    if (params.tracks) {                       // if tracks to be added to the view
        this.showTracks(params.tracks);        //     show
    } else if (oldTrackList) {                 // else read cookie
        this.showTracks(oldTrackList);         //     refresh
    } else if (params.defaultTracks) {         // if no cookie
        this.showTracks(params.defaultTracks); //     load default
    }

    // Get a list of all inactive tracks - not loaded in the view
    this.get_menu_tracks = function(){
        var all_tracks = params.trackData; // Array
        var ntracks = all_tracks.length;
        var viewed_trackLabels = dojo.cookie(brwsr.container.id + "-tracks");
        var menu_tracks = [];
        for (var i=0; i<ntracks; i++){
            var track_i = all_tracks[i];
            if (viewed_trackLabels.split(',').indexOf(track_i.key) < 0 && track_i.key != "DNA") { // if not viewed
                menu_tracks.push(track_i);
            }
        }
        return menu_tracks;
    }

    //// Connect the buttons to sorting functions (TO BE FIXED)
    // dojo.connect(sortByName_button, 'click', function(e){
    //     //var menu_tracks = get_menu_tracks();
    //     //menu_tracks.sort(sort_by('key', true, null));
    //     //params.trackData = menu_tracks; // ? dojo.cookie("Menu-tracks") // save the new order
    //     //// remove old tracks list
    //     //dojo.forEach(dojo.byId("tracksAvail").childNodes, function(cnode,i){
    //     //    if (i!=0) dojo.destroy(cnode);
    //     //});
    //     //// insert reordered tracks list
    //     //brwsr.trackListWidget.insertNodes(false, menu_tracks);
    // });
    // dojo.connect(sortByType_button, 'click', function(e){
    //     //menu_tracks.sort('type', true, null);
    // });
    // dojo.connect(sortByDate_button, 'click', function(e){
    //     //menu_tracks.sort('date', true, parseDate);
    // });
};

/**
 * If a track is moved from the list to the view or conversely,
 * updates the related cookies and (? visibleBlocks).
 */
Browser.prototype.onVisibleTracksChanged = function() {
    brwsr = this;
    this.view.updateTrackList();
    // Write viewed tracks in cookie "GenomeBrowser-tracks"
    var trackLabels = dojo.map(this.view.tracks, function(track) {
        return track.name;
    });
    dojo.cookie(this.container.id + "-tracks", trackLabels.join(","), {expires:60});
    // Write not viewed tracks in cookie "GenomeBrowser-menu_tracks"
    menu_tracks = this.get_menu_tracks();
    var menu_trackLabels = [];
    for (var i=0; i<menu_tracks.length; i++) {
        menu_trackLabels.push(menu_tracks[i].label);
    }
    dojo.cookie(this.container.id + "-menu_tracks", menu_trackLabels.join(","), {expires:60});

    // Menu appearing on right-click on a track element of the view.
    if (this.rClickMenu) { dojo.destroy(this.rClickMenu); }
    var trackIds = [];
    for (var i=0; i<trackLabels.length; i++)
        { trackIds.push("track_"+trackLabels[i]); }
    var rClickMenu = new dijit.Menu({
        targetNodeIds: trackIds,
    });
    this.rClickMenu = rClickMenu;
    // Connect new viewed tracks with the menu on right click
    rClickMenu.targetNodeIds = trackIds;
    console.log(this.rClickMenu)
    dojo.connect(rClickMenu, "_openMyself", function(e){
            var name = e.target.className.split(" ");
            if (name.indexOf("block") >= 0) // view, image
                { target = e.target.parentNode; }
            else if (name.indexOf("track-label") >= 0) // view, label
                { target = e.target.parentNode; }
            console.log("target:", target);
        })
    // add items to the menu and connect
    rClickMenu.addChild(new dijit.MenuItem({
        label: "View in minimap",
        onClick: function(e){
            var ntracks = trackInfo.length;
            for (var i=0; i<ntracks; i++) {
                if (target.id.split("track_")[1] == trackInfo[i].label)
                    { track = trackInfo[i]; }
            }
            console.log(track)
            gv.minimap.drawMinitrack(track)
        }
    }));

    // ?
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
    var trapLeft = Math.round((((startbp - this.view.ref.start) / length) * this.view.overviewBox.w)
                    + this.view.overviewBox.l);
    var trapRight = Math.round((((endbp - this.view.ref.start) / length) * this.view.overviewBox.w)
                    + this.view.overviewBox.l);

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

    var navbox = dojo.create("div", {id: "navbox", style: {cssText: "z-index:10;"} });
    var navbox_left = dojo.create("div", {id: "navbox_left"}, navbox);
    var navbox_middle = dojo.create("div", {id: "navbox_middle"}, navbox);
    var navbox_right = dojo.create("div", {id: "navbox_right"}, navbox);
    var navbox_slider = dojo.create("div", {id: "navbox_slider"}, navbox);

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

    // ------------Minimap - Navbox middle--------------
    var overview = dojo.create("div", {
        className: "overview",
        id: "overview",
        style: {cssText: "display: inline-block",
                margin: "3px"},
        }, navbox_middle);
    dojo.create("canvas", {
        id:"minimap",
        height: "20px",
        }, overview);
    // If a track is dropped onto the minimap location, a
    // new canvas is created and a mini-track is drawn.
    var minitrackCreate = function(track, hint) {
        var old_minimap = dojo.byId("minimap");
        if (old_minimap) dojo.destroy(old_minimap);
        var minimap_canvas = dojo.create("canvas", {
            id:"minimap",
            height: "20px",
            }, overview);
        brwsr.view.minimap.canvas = minimap_canvas;
        brwsr.view.minimap.drawMinitrack(track);
        return {node: minimap_canvas, data: track, type: ["minitrack"]};
        };
    // Activate drag & drop onto the minimap
    this.minimapWidget = new dojo.dnd.Target(overview,
        { creator: minitrackCreate,
          copyState: function(keyPressed,self){ return true; },
          copyOnly: true,
          accept: ["track"],
          withHandles: false,
        });

    // ------------Navbox right--------------
    // Zoom slider
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
    navbox_slider.title = "Change the zoom level";
    navbox_slider.appendChild(zoomSlider.domNode);
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
