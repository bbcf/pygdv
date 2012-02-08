/**
 * This file is called by Browser.js when the page is loaded
 * All coordinates are interbase
 */

/**
 * subject:  what's being animated
 * callback: function to call at the end of the animation
 * time:     time for the animation to run
 */
function Animation(subject, callback, time) {
    if (subject === undefined) return;
    // Don't want a zoom and a slide going on at the same time
    if ("animation" in subject) subject.animation.stop();
    this.index = 0;
    this.time = time;
    this.subject = subject;
    this.callback = callback;
    var myAnim = this;
    this.animFunction = function() {myAnim.animate();};
    // Number of milliseconds between frames (e.g., 33ms at 30fps)
    this.animID = setTimeout(this.animFunction, 33);
    this.frames = 0;
    subject.animation = this;
}

/**
 * Undocumented
 */
Animation.prototype.animate = function () {
    if (this.finished) {
        this.stop();
        return;
    }
    // Number of milliseconds between frames (e.g., 33ms at 30fps)
    var nextTimeout = 33;
    var elapsed = 0;
    if (!("startTime" in this)) {
        this.startTime = (new Date()).getTime();
    } else {
        elapsed = (new Date()).getTime() - this.startTime;
        // Set the next timeout to be the average of the
        // frame times we've achieved so far.
        // The goal is to avoid overloading the browser
        // and getting a jerky animation.
        nextTimeout = Math.max(33, elapsed / this.frames);
    }
    if (elapsed < this.time) {
        this.step(elapsed / this.time);
        this.frames++;
    } else {
        this.step(1);
        this.finished = true;
    }
    this.animID = setTimeout(this.animFunction, nextTimeout);
};

/**
 * Undocumented
 */
Animation.prototype.stop = function() {
    clearTimeout(this.animID);
    delete this.subject.animation;
    this.callback(this);
};

/**
 * Undocumented
 */
function Slider(view, callback, time, distance) {
    Animation.call(this, view, callback, time);
    this.slideStart = view.getX();
    this.slideDistance = distance;
}

Slider.prototype = new Animation();

/**
 * Undocumented
 */
Slider.prototype.step = function(pos) {
    // Cosinus will go from 1 to -1, we want to go from 0 to 1
    var newX = (this.slideStart - (this.slideDistance *
                ((-0.5 * Math.cos(pos * Math.PI)) + 0.5))) | 0;
    newX = Math.max(Math.min(this.subject.maxLeft - this.subject.offset, newX),
                             this.subject.minLeft - this.subject.offset);
    this.subject.setX(newX);
    // Draw the zone selections
    this.subject.zoneSel.handler.update(this.subject.pxPerBp, this.subject.minVisible(), this.subject.maxVisible());
};

/**
 * Undocumented
 */
function Zoomer(scale, toScroll, callback, time, zoomLoc) {
    Animation.call(this, toScroll, callback, time);
    this.toZoom = toScroll.zoomContainer;
    var cWidth = this.toZoom.clientWidth;
    this.initialWidth = cWidth;
    // The container width when zoomFraction is 0
    this.width0 = cWidth * Math.min(1, scale);
    // The container width when zoomFraction is 1
    var width1 = cWidth * Math.max(1, scale);
    this.distance = width1 - this.width0;
    this.zoomingIn = scale > 1;
    this.center = (toScroll.getX() + (toScroll.elem.clientWidth * zoomLoc))
                  / toScroll.scrollContainer.clientWidth;
    // initialX and initialLeft can differ when we're scrolling
    // using scrollTop and scrollLeft
    this.initialX = this.subject.getX();
    this.initialLeft = parseInt(this.toZoom.style.left);
};

Zoomer.prototype = new Animation();

/**
 * Honestly I don't know what the variables are or what
 * the units are. Let's try to describe them.
 * ---pos---
 * Always goes from 0 to 1
 * ---zoomFraction---
 * Always goes from 1 to 0 (zoom out) or from 0 to 1 (zoom in)
 * ---this.distance---
 * Constant at typically about 6000 (zoom out) or 18000 (zoom in)
 * ---this.center---
 * About 0.4 when click on left and 0.6 when click on right
 * ---newWidth---
 * Typically goes from 5000 to 1000 (zoom out) or from 6000 to 30000 (zoom in)
 * ---newLeft---
 * Typically goes from 0 to 2500 (zoom out) or from 0 to -9000 (zoom in)
 * ---this.initialLeft---
 * Perfectly useless. Always 0.
 * ---this.initialWidth---
 * Constant at 12500 or sometimes 6250
 * ---this.initialX---
 * Constant often around 5600
 * ---this.width0---
 * When zooming in is identical to this.initialWidth, otherwise different
 */
Zoomer.prototype.step = function(pos) {
    var zoomFraction = this.zoomingIn ? pos : 1 - pos;
    var newWidth = ((zoomFraction * zoomFraction) * this.distance) + this.width0;
    var newLeft = (this.center * this.initialWidth) - (this.center * newWidth);
    this.toZoom.style.width = newWidth + "px";
    this.toZoom.style.left = (this.initialLeft + newLeft) + "px";
    var forceRedraw = this.toZoom.offsetTop;
    this.subject.updateTrackLabels(this.initialX - newLeft);
    // Draw the zone selections
    view = this.subject
    leftbase  = view.leftBaseBeforeZoom *(1-pos) + view.leftBaseAfterZoom *(pos)
    rightbase = view.rightBaseBeforeZoom*(1-pos) + view.rightBaseAfterZoom*(pos)
    factor    = b.view.elem.offsetWidth / (rightbase - leftbase)
    view.zoneSel.handler.update(factor, leftbase, rightbase)
};

/**
 * Create the genome view that contains the tracks
 * @example
 * var gv = new GenomeView(viewElem, 250, brwsr.refSeq, 1/200);
 * @param elem        {DOM object} The page element that the GenomeView lives in
 * @param stripeWidth {Integer}    Current scale, in pixels per bp
 * @param refseq      {?}          The reference sequence
 * @param zoomLevel   {Float}      Current scale, in pixels per bp
 */
function GenomeView(elem, stripeWidth, refseq, zoomLevel) {
    // Copy variables that are sent to the function
    this.ref = refseq;
    this.pxPerBp = zoomLevel;
    this.stripeWidth = stripeWidth;
    this.elem = elem;

    // Measure text width of the browser for the closest zoom level
    var widthTest = document.createElement("div");
    widthTest.className = "sequence";
    widthTest.style.visibility = "hidden";
    var widthText = "12345678901234567890123456789012345678901234567890";
    widthTest.appendChild(document.createTextNode(widthText));
    elem.appendChild(widthTest);
    this.charWidth = widthTest.clientWidth / widthText.length;
    this.seqHeight = widthTest.clientHeight;
    elem.removeChild(widthTest);

    // Measure the height of some arbitrary text in whatever font this
    // shows up in (set by an external CSS file)
    var heightTest = document.createElement("div");
    heightTest.className = "pos-label";
    heightTest.style.visibility = "hidden";
    heightTest.appendChild(document.createTextNode("42"));
    elem.appendChild(heightTest);
    this.posHeight = heightTest.clientHeight;
    elem.removeChild(heightTest);

    // Add an arbitrary 100% padding between the position labels and the
    // topmost track
    this.topSpace = 2 * this.posHeight;

    // The scrollContainer is the element that changes position
    // when the user scrolls
    this.scrollContainer = document.createElement("div");
    this.scrollContainer.id = "container";
    this.scrollContainer.style.cssText = "position: absolute; left: 0px; top: 0px;";
    elem.appendChild(this.scrollContainer);

    // We have a separate zoomContainer as a child of the scrollContainer.
    // they used to be the same element, but making zoomContainer separate
    // enables it to be narrower than this.elem
    // The zoomContainer will contains all the track divs
    this.zoomContainer = document.createElement("div");
    this.zoomContainer.id = "zoomContainer";
    this.zoomContainer.style.cssText = "position: absolute; left: 0px; top: 0px; height: 100%;";
    this.scrollContainer.appendChild(this.zoomContainer);

    // Width, in pixels, of the "regular" (not min or max zoom) stripe
    this.regularStripe = stripeWidth;

    // Width, in pixels, of stripes at closest zoom (based on the sequence
    // character width). The number of characters per stripe is
    // somewhat arbitrarily set at stripeWidth/10
    this.fullZoomStripe = this.charWidth * (stripeWidth / 10);

    // Overview and minimap box
    this.overview = dojo.byId("overview");
    this.overviewBox = dojo.marginBox(this.overview);

    // Lists of all tracks
    this.tracks = [];
    this.uiTracks = [];
    this.trackIndices = {};

    // Set up size state (zoom levels, stripe percentage, etc.)
    this.sizeInit();

    // Distance, in pixels, from the beginning of the reference sequence
    // to the beginning of the first active stripe
    // should always be a multiple of stripeWidth
    this.offset = 0;

    // Largest value for the sum of this.offset and this.getX()
    // this prevents us from scrolling off the right end of the ref seq
    this.maxLeft = this.bpToPx(this.ref.end) - this.dim.width;

    // Smallest value for the sum of this.offset and this.getX()
    // this prevents us from scrolling off the left end of the ref seq
    this.minLeft = this.bpToPx(this.ref.start);

    // Distance, in pixels, between each track
    this.trackPadding = 20;

    // Extra margin to draw around the visible area, in multiples of the visible area
    // E.g. 0=draw only the visible area; 0.1=draw an extra 10% around the visible area, etc.
    this.drawMargin = 0.2;

    // Slide distance (pixels) * slideTimeMultiple + 200 = milliseconds for slide
    // E.g. 1=one pixel per millisecond average slide speed; larger numbers are slower
    this.slideTimeMultiple = 0.8;
    this.trackHeights = [];
    this.trackTops = [];
    this.trackLabels = [];

    // Add scale list & zoom
    this.trackScales = [];
    //this.trackZooms = [];
    // Undocumented
    this.prevCursors = [];

    // List of objects to wait on after animations
    this.waitElems = [document.body, elem];

    // Setup cursor functions
    this.setCursorToGrab      = function(e) {if (dojo.isSafari) {e.style.cursor = '-webkit-grab';}
                                            else                {e.style.cursor = 'move';}};
    this.setCursorToGrabbing  = function(e) {if (dojo.isSafari) {e.style.cursor = '-webkit-grabbing';}
                                            else                {e.style.cursor = 'move';}};
    this.setCursorToSelect    = function(e) {e.style.cursor = 'crosshair';}
    this.eventCursorGrab      = function(e) {this.setCursorToGrab(e.target);}
    this.eventCursorGrabbing  = function(e) {this.setCursorToGrabbing(e.target);}
    this.eventCursorSelect    = function(e) {this.setCursorToSelect(e.target);}
    
    this.setCursorToGrab(this.elem)

    // The locationThumb is the currently viewed zone indicator on the minimap
    this.locationThumb = document.createElement("div");
    this.locationThumb.className = "locationThumb";
    this.overview.appendChild(this.locationThumb);
    this.locationThumbMover = new dojo.dnd.move.parentConstrainedMoveable(this.locationThumb, {area: "margin", within: true});
    dojo.connect(this.locationThumbMover, "onMoveStop",  this, "thumbMoved");
    this.setCursorToGrab(this.locationThumb)
    dojo.connect(this.locationThumbMover, "onMouseDown", this, this.eventCursorGrabbing)
    this.locationThumb.title = "The red rectangle represents the currently viewed region of the chromosome."

    // If you click on the minimap somewhere outside of
    // the locationThumb, you want to move there.
    dojo.connect(this.overview, "onmousedown", this, function(e) {this.centerAtBase(Math.round((e.layerX/e.target.offsetWidth)*this.ref.end));});

    // Copy the self object
    var view = this;

    // CSS scrolling will be used if we detect IE
    if (dojo.isIE) {setUpViewWithCSS(view);   }
    else           {setUpViewWithoutCSS(view);}

    // Set up drag stop event
    view.dragEnd = function(event) {
        dojo.forEach(view.dragEventHandles, dojo.disconnect);
        view.dragging = false;
        view.eventCursorGrab(event)
        document.body.style.cursor = "default";
        dojo.stopEvent(event);
        view.showCoarse();
        view.scrollUpdate();
        view.showVisibleBlocks(true);
    };

    // Copy DOM objects
    var htmlNode = document.body.parentNode;
    var bodyNode = document.body;

    // We stop the drag if the mouse gets out of the browser window
    view.checkDragOut = function(event) {
        if (!(event.relatedTarget || event.toElement)
            || (htmlNode === (event.relatedTarget || event.toElement))
            || (bodyNode === (event.relatedTarget || event.toElement)))
            view.dragEnd(event);
    };

    // The function triggered when the user drags the view space
    view.dragMove = function(event) {
	view.setPosition({
            x: view.winStartPos.x - (event.clientX - view.dragStartPos.x),
            y: view.winStartPos.y - (event.clientY - view.dragStartPos.y)
        });
        view.zoneSel.update(view);
        dojo.stopEvent(event);
    };

    // When the mouse button is clicked but not released
    view.mouseDown = function(event) {
	if(event.target.className == "score_input"){
            return false;
	}
        if ("animation" in view) {
            if (view.animation instanceof Zoomer) {
                dojo.stopEvent(event);
                return;
            } else {
                view.animation.stop();
            }
        }
        if (Util.isRightButton(event)) {return};
        dojo.stopEvent(event);
        if (event.shiftKey || event.ctrlKey) {return};
        view.dragEventHandles =
             [
             dojo.connect(document.body, "mouseup",   view.dragEnd),
             dojo.connect(document.body, "mousemove", view.dragMove),
             dojo.connect(document.body, "mouseout",  view.checkDragOut)
             ];
        view.dragging = true;
        view.dragStartPos = {x: event.clientX,
                     y: event.clientY};
        view.winStartPos = view.getPosition();
        view.eventCursorGrabbing(event)
    };
    view.connectMouse    = function() {this.mouseConnection = dojo.connect(view.elem, "mousedown", view.mouseDown);};
    view.disconnectMouse = function() {dojo.disconnect(this.mouseConnection);};
    view.connectMouse();

    // Double click event
    dojo.connect(view.elem, "dblclick", function(event) {
        if (view.dragging) return;
        if ("animation" in view) return;
        var zoomLoc = (event.pageX - dojo.coords(view.elem, true).x) / view.dim.width;
        if (event.shiftKey) {
            view.zoomOut(event, zoomLoc, 2);
        } else {
            view.zoomIn(event, zoomLoc, 2);
        }
        dojo.stopEvent(event);
    });
    // Undocumented
    view.afterSlide = function() {
        view.showCoarse();
        view.scrollUpdate();
        view.showVisibleBlocks(true);
    };
    view.zoomCallback = function() { view.zoomUpdate(); };

     // Using the scroll wheel to move
    var wheelScrollTimeout = null;
    var wheelScrollUpdate = function() {
        view.showVisibleBlocks(true);
        wheelScrollTimeout = null;
    };
    view.wheelScroll = function(e) {
        var oldY = view.getY();
        // Arbitrary 60 pixel vertical movement per scroll wheel event
        var newY = Math.min(Math.max(0, oldY - 60 * Util.wheel(e)), view.containerHeight - view.dim.height);
        view.setY(newY);
        // The timeout is so that we don't have to run showVisibleBlocks
        // for every scroll wheel click (we just wait until so many ms
        // after the last one).
        if (wheelScrollTimeout)
            clearTimeout(wheelScrollTimeout);
            // 100 milliseconds since the last scroll event is an arbitrary
            // cutoff for deciding when the user is done scrolling
            // (set by a bit of experimentation)
        wheelScrollTimeout = setTimeout(wheelScrollUpdate, 100);
        dojo.stopEvent(e);
    };
    dojo.connect(view.scrollContainer, "mousewheel",     view.wheelScroll, false);
    dojo.connect(view.scrollContainer, "DOMMouseScroll", view.wheelScroll, false);

    // This track is the location indicator bar at the top that
    // tells the user what are the coordinates in base pairs
    // of the currently view zone
    var trackDiv = document.createElement("div");
    trackDiv.className = "track";
    trackDiv.style.height = this.posHeight + "px";
    trackDiv.id = "static_track";
    this.staticTrack = new StaticTrack("static_track", "pos-label", this.posHeight);
    this.staticTrack.setViewInfo(function(height) {}, this.stripeCount,
                                 trackDiv, undefined, this.stripePercent,
                                 this.stripeWidth, this.pxPerBp);
    this.zoomContainer.appendChild(trackDiv);
    this.waitElems.push(trackDiv);

    // This track contains the small gray lines that form
    // a grid and help the user know the location of every
    // element on the location indicator
    var gridTrackDiv = document.createElement("div");
    gridTrackDiv.className = "track";
    gridTrackDiv.style.cssText = "top: 0px; height: 100%;";
    gridTrackDiv.id = "gridtrack";
    var gridTrack = new GridTrack("gridtrack");
    gridTrack.setViewInfo(function(height) {}, this.stripeCount,
                          gridTrackDiv, undefined, this.stripePercent,
                          this.stripeWidth, this.pxPerBp);
    this.zoomContainer.appendChild(gridTrackDiv);

    // Do something to show the location indicator
    this.uiTracks = [this.staticTrack, gridTrack];
    dojo.forEach(this.uiTracks, function(track) {
        track.showRange(0, this.stripeCount - 1,
                        Math.round(this.pxToBp(this.offset)),
                        Math.round(this.stripeWidth / this.pxPerBp),
                        this.pxPerBp);
    }, this);

    // Undocumented
    this.zoomContainer.style.paddingTop = this.topSpace + "px";

    // Get the assembly ID
    this.nr_assembly_id = dojo.byId('nr_assembly_id').innerHTML;

    // Create a zone selection object
    var zoneSel = new ZoneSelection(view);
    view.zoneSel = zoneSel;

    // Create a genrep object
    var genrep = new GenRep();
    view.genrep = genrep;

    // Default image in case minimap doesn't work
    dojo.byId("overview").style.backgroundImage  = "url('" + window.picsPathRoot + "dummy_chromosome.png')";

    // Create a minimap object
    var minimap = new Minimap(view);
    view.minimap = minimap;
    minimap.update()

    // Undocumented
    GDV_POST_FETCHER.send();
}

/**
 * Sets up view functions with CSS scrolling
 */
function setUpViewWithCSS(view) {
    view.x = -parseInt(view.scrollContainer.style.left);
    view.y = -parseInt(view.scrollContainer.style.top);
    view.getX = function() {return view.x;};
    view.getY = function() {return view.y;};
    view.getPosition = function() {return { x: view.x, y: view.y };};
    view.rawSetX = function(x) {
        view.scrollContainer.style.left = -x + "px"; view.x = x;
    };
    view.setX = function(x) {
        view.x = Math.max(Math.min(view.maxLeft - view.offset, x), view.minLeft - view.offset);
        view.x = Math.round(view.x);
        view.updateTrackLabels(view.x);
        view.scrollContainer.style.left = -view.x + "px";
    };
    view.rawSetY = function(y) {
        view.scrollContainer.style.top = -y + "px"; view.y = y;
    };
    view.setY = function(y) {
        view.y = Math.min((y < 0 ? 0 : y), view.containerHeight- view.dim.height);
        view.y = Math.round(view.y);
        view.updatePosLabels(view.y);
        view.scrollContainer.style.top = -view.y + "px";
    };
    view.rawSetPosition = function(pos) {
        view.scrollContainer.style.left = -pos.x + "px";
        view.scrollContainer.style.top = -pos.y + "px";
    };
    view.setPosition = function(pos) {
        view.x = Math.max(Math.min(view.maxLeft - view.offset, pos.x), view.minLeft - view.offset);
        view.y = Math.min((pos.y < 0 ? 0 : pos.y), view.containerHeight - view.dim.height);
        view.x = Math.round(view.x);
        view.y = Math.round(view.y);
        view.updateTrackLabels(view.x);
        view.updatePosLabels(view.y);
        view.scrollContainer.style.left = -view.x + "px";
        view.scrollContainer.style.top = -view.y + "px";
    };
}

/**
 * Sets up view functions without CSS scrolling
 */
function setUpViewWithoutCSS(view) {
    view.x = view.elem.scrollLeft;
    view.y = view.elem.scrollTop;
    view.getX = function() {return view.x;};
    view.getY = function() {return view.y;};
    view.getPosition = function() {return { x: view.x, y: view.y };};
    view.rawSetX = function(x) {
        view.elem.scrollLeft = x; view.x = x;
    };
    view.setX = function(x) {
        view.x = Math.max(Math.min(view.maxLeft - view.offset, x), view.minLeft - view.offset);
        view.x = Math.round(view.x);
        view.updateTrackLabels(view.x);
        view.elem.scrollLeft = view.x;
    };
    view.rawSetY = function(y) {
        view.elem.scrollTop = y; view.y = y;
    };
    view.rawSetPosition = function(pos) {
        view.elem.scrollLeft = pos.x; view.x = pos.x;
        view.elem.scrollTop = pos.y; view.y = pos.y;
    };
    view.setY = function(y) {
        view.y = Math.min((y < 0 ? 0 : y), view.containerHeight - view.dim.height);
        view.y = Math.round(view.y);
        view.updatePosLabels(view.y);
        view.elem.scrollTop = view.y;
    };
    view.setPosition = function(pos) {
        view.x = Math.max(Math.min(view.maxLeft - view.offset, pos.x), view.minLeft - view.offset);
        view.y = Math.min((pos.y < 0 ? 0 : pos.y), view.containerHeight - view.dim.height);
        view.x = Math.round(view.x);
        view.y = Math.round(view.y);
        view.updateTrackLabels(view.x);
        view.updatePosLabels(view.y);
        view.elem.scrollLeft = view.x;
        view.elem.scrollTop = view.y;
    };
}

/**
 * Moves the view by (distance times the width of the view) pixels
 */
GenomeView.prototype.slide = function(distance) {
    if (this.animation) this.animation.stop();
    this.trimVertical();
    // Slide for an amount of time that's a function of the distance being
    // traveled plus an arbitrary extra 200 milliseconds so that
    // short slides aren't too fast (200 chosen by experimentation)
    new Slider(this,
               this.afterSlide,
               Math.abs(distance) * this.dim.width * this.slideTimeMultiple + 200,
               distance * this.dim.width);
};

/**
 * Undocumented
 */
GenomeView.prototype.setLocation = function(refseq, startbp, endbp) {
    if (startbp === undefined) startbp = this.minVisible();
    if (endbp === undefined) endbp = this.maxVisible();
    if ((startbp < refseq.start) || (startbp > refseq.end))
        startbp = refseq.start;
    if ((endbp < refseq.start) || (endbp > refseq.end))
        endbp = refseq.end;
    // Change chromosome
    if (this.ref != refseq) {
        this.ref = refseq;
        var removeTrack = function(track) {
            if (track.div && track.div.parentNode)
            track.div.parentNode.removeChild(track.div);
        };
        dojo.forEach(this.tracks, removeTrack);
        dojo.forEach(this.uiTracks, function(track) { track.clear(); });
        this.overviewTrackIterate(removeTrack);
        this.sizeInit();
        this.setY(0);
        this.containerHeight = this.topSpace;
        // Update and redraw the chromosome minimap
        this.minimap.update()
    }
    this.pxPerBp = Math.min(this.dim.width / (endbp - startbp), this.charWidth);

    // Set the new zoom level
    this.curZoom = Util.findNearest(this.zoomLevels, this.pxPerBp);

    // Update the position of the zoom slider
    dijit.byId("zoom_slider")._setValueAttr(this.curZoom);

    if (Math.abs(this.pxPerBp - this.zoomLevels[this.zoomLevels.length - 1]) < 0.2) {
        // The cookie-saved location is in round bases, so if the saved
        // location was at the highest zoom level, the new zoom level probably
        // won't be exactly at the highest zoom (which is necessary to trigger
        // the sequence track), so we nudge the zoom level to be exactly at
        // the highest level if it's close.
        // Exactly how close is arbitrary; 0.2 was chosen to be close
        // enough that people wouldn't notice if we fudged that much.
        console.log("nudging zoom level from %d to %d", this.pxPerBp, this.zoomLevels[this.zoomLevels.length - 1]);
        this.pxPerBp = this.zoomLevels[this.zoomLevels.length - 1];
    }
    this.stripeWidth = (this.stripeWidthForZoom(this.curZoom) / this.zoomLevels[this.curZoom]) * this.pxPerBp;
    this.instantZoomUpdate();
    this.centerAtBase((startbp + endbp) / 2, true);
};

/**
 * Undocumented
 */
GenomeView.prototype.stripeWidthForZoom = function(zoomLevel) {
    if ((this.zoomLevels.length - 1) == zoomLevel) {
        return this.fullZoomStripe;
    } else if (0 == zoomLevel) {
        return this.minZoomStripe;
    } else {
        return this.regularStripe;
    }
};

/**
 * Undocumented
 */
GenomeView.prototype.instantZoomUpdate = function() {
    this.scrollContainer.style.width =
        (this.stripeCount * this.stripeWidth) + "px";
    this.zoomContainer.style.width =
        (this.stripeCount * this.stripeWidth) + "px";
    this.maxOffset =
        this.bpToPx(this.ref.end) - this.stripeCount * this.stripeWidth;
    this.maxLeft = this.bpToPx(this.ref.end) - this.dim.width;
    this.minLeft = this.bpToPx(this.ref.start);
};

/**
 * Undocumented
 */
GenomeView.prototype.centerAtBase = function(base, instantly) {
    base = Math.min(Math.max(base, this.ref.start), this.ref.end);
    if (instantly) {
        var pxDist = this.bpToPx(base);
        var containerWidth = this.stripeCount * this.stripeWidth;
        var stripesLeft = Math.floor((pxDist - (containerWidth / 2)) / this.stripeWidth);
        this.offset = stripesLeft * this.stripeWidth;
        this.setX(pxDist - this.offset - (this.dim.width / 2));
        this.trackIterate(function(track) { track.clear(); });
        this.showVisibleBlocks(true);
        this.showCoarse();
    } else {
        var startbp = this.pxToBp(this.x + this.offset);
        var halfWidth = (this.dim.width / this.pxPerBp) / 2;
        var endbp = startbp + halfWidth + halfWidth;
        var center = startbp + halfWidth;
        if ((base >= (startbp  - halfWidth))
            && (base <= (endbp + halfWidth))) {
                // We're moving somewhere nearby, so move smoothly
                if (this.animation) this.animation.stop();
                var distance = (center - base) * this.pxPerBp;
            this.trimVertical();
                // Slide for an amount of time that's a function of the
                // distance being traveled plus an arbitrary extra 200
                // milliseconds so that short slides aren't too fast
                // (200 chosen by experimentation)
                new Slider(this, this.afterSlide,
                           Math.abs(distance) * this.slideTimeMultiple + 200,
                           distance);
        } else {
            // We're moving far away, move instantly
            this.centerAtBase(base, true);
        }
    }
};

/**
 * Undocumented
 */
GenomeView.prototype.minVisible = function() {
    return this.pxToBp(this.x + this.offset);
};

/**
 * Undocumented
 */
GenomeView.prototype.maxVisible = function() {
    return this.pxToBp(this.x + this.offset + this.dim.width);
};

/**
 * Undocumented
 */
GenomeView.prototype.showCoarse = function() {
    this.onCoarseMove(this.minVisible(), this.maxVisible());
};

/**
 * Undocumented
 */
GenomeView.prototype.onCoarseMove = function() {};

/**
 * Undocumented
 */
GenomeView.prototype.thumbMoved = function(mover) {
    var pxLeft = parseInt(this.locationThumb.style.left);
    var pxWidth = parseInt(this.locationThumb.style.width);
    var pxCenter = pxLeft + (pxWidth / 2);
    this.centerAtBase(((pxCenter / this.overviewBox.w) * (this.ref.end - this.ref.start)) + this.ref.start);
    this.setCursorToGrab(this.locationThumb)
};

/**
 * Undocumented
 */
GenomeView.prototype.checkY = function(y) {
    return Math.min((y < 0 ? 0 : y), this.containerHeight - this.dim.height);
};

/**
 * Undocumented
 */
GenomeView.prototype.updatePosLabels = function(newY) {
    if (newY === undefined) {newY = this.getY()};
    this.staticTrack.div.style.top = newY + "px";
};

/**
 * Undocumented
 */
GenomeView.prototype.updateTrackLabels = function(newX) {
    if (newX === undefined) newX = this.getX();
    for (var i = 0; i < this.trackLabels.length; i++){
        this.trackLabels[i].style.left = newX + 100 + "px";
        var ts = this.trackScales[i];
        if(ts){
            ts.style.left = newX + "px";
        }
        // var tz = this.trackZooms[i];
        // if(tz){
        //     tz.style.left = newX - 70  +"px";
        // }
    }
};

/**
 * Undocumented
 */
GenomeView.prototype.showWait = function() {
    var oldCursors = [];
    for (var i = 0; i < this.waitElems.length; i++) {
        oldCursors[i] = this.waitElems[i].style.cursor;
        this.waitElems[i].style.cursor = "wait";
    }
    this.prevCursors.push(oldCursors);
};

/**
 * Undocumented
 */
GenomeView.prototype.showDone = function() {
    var oldCursors = this.prevCursors.pop();
    for (var i = 0; i < this.waitElems.length; i++) {
        this.waitElems[i].style.cursor = oldCursors[i];
    }
};

/**
 * Undocumented
 */
GenomeView.prototype.pxToBp = function(pixels) {
    return pixels / this.pxPerBp;
};

/**
 * Undocumented
 */
GenomeView.prototype.bpToPx = function(bp) {
    return bp * this.pxPerBp;
};

/**
 * Undocumented
 */
GenomeView.prototype.sizeInit = function() {
    this.dim = {width: this.elem.clientWidth, height: this.elem.clientHeight};

    // Create the minimap indicator box
    this.overviewBox = dojo.marginBox(this.overview);

    // Scale values, in pixels per bp, for all zoom levels
    this.zoomLevels = [1/500000, 1/200000, 1/100000, 1/50000, 1/20000, 1/10000, 1/5000, 1/2000, 1/1000, 1/500, 1/200, 1/100, 1/50, 1/20, 1/10, 1/5, 1/2, 1, 2, 5, this.charWidth];

    // Make sure we don't zoom out too far
    while (((this.ref.end - this.ref.start) * this.zoomLevels[0])
           < this.dim.width) {
        this.zoomLevels.shift();
    }
    this.zoomLevels.unshift(this.dim.width / (this.ref.end - this.ref.start));

    // Width, in pixels, of stripes at min zoom (so the view covers
    // the whole ref seq)
    this.minZoomStripe = this.regularStripe * (this.zoomLevels[0] / this.zoomLevels[1]);

    // Undocumented
    this.curZoom = 0;
    while (this.pxPerBp > this.zoomLevels[this.curZoom])
        this.curZoom++;
    this.maxLeft = this.bpToPx(this.ref.end) - this.dim.width;

    delete this.stripePercent;
    // 25, 50, 100 don't work as well due to the way scrollUpdate works
    var possiblePercents = [20, 10, 5, 4, 2, 1];
    for (var i = 0; i < possiblePercents.length; i++) {
        // We'll have (100 / possiblePercents[i]) stripes.
        // multiplying that number of stripes by the minimum stripe width
        // gives us the total width of the "container" div.
        // (or what that width would be if we used possiblePercents[i]
        // as our stripePercent)
        // That width should be wide enough to make sure that the user can
        // scroll at least one page-width in either direction without making
        // the container div bump into the edge of its parent element, taking
        // into account the fact that the container won't always be perfectly
        // centered (it may be as much as 1/2 stripe width off center)
        // So, (this.dim.width * 3) gives one screen-width on either side,
        // and we add a regularStripe width to handle the slightly off-center
        // cases.
        // The minimum stripe width is going to be halfway between
        // "canonical" zoom levels; the widest distance between those
        // zoom levels is 2.5-fold, so halfway between them is 0.7 times
        // the stripe width at the higher zoom level
        if (((100 / possiblePercents[i]) * (this.regularStripe * 0.7))
            > ((this.dim.width * 3) + this.regularStripe)) {
            this.stripePercent = possiblePercents[i];
            break;
        }
    }

    // Undocumented
    if (this.stripePercent === undefined) {
        console.warn("stripeWidth too small: " + this.stripeWidth + ", " + this.dim.width);
        this.stripePercent = 1;
    }

    // Undocumented
    var oldX;
    var oldStripeCount = this.stripeCount;
    if (oldStripeCount) oldX = this.getX();
    this.stripeCount = Math.round(100 / this.stripePercent);

    // Undocumented
    this.scrollContainer.style.width = (this.stripeCount * this.stripeWidth) + "px";
    this.zoomContainer.style.width = (this.stripeCount * this.stripeWidth) + "px";

    // Undocumented
    var blockDelta = undefined;
    if (oldStripeCount && (oldStripeCount != this.stripeCount)) {
        blockDelta = Math.floor((oldStripeCount - this.stripeCount) / 2);
        var delta = (blockDelta * this.stripeWidth);
        var newX = this.getX() - delta;
        this.offset += delta;
        this.updateTrackLabels(newX);
        this.rawSetX(newX);
    }

    this.trackIterate(function(track, view) {
        track.sizeInit(view.stripeCount, view.stripePercent, blockDelta);
    });

    // Undocumented
    var newHeight = parseInt(this.scrollContainer.style.height);
    newHeight = (newHeight > this.dim.height ? newHeight : this.dim.height);

    // Undocumented
    this.scrollContainer.style.height = newHeight + "px";
    this.containerHeight = newHeight;

    // Undocumented
    var refLength = this.ref.end - this.ref.start;

    // posSize is hidden but helps guess what width
    // it takes to write the largest possible position
    var posSize = document.createElement("div");
    posSize.className = "overview-pos";
    posSize.appendChild(document.createTextNode(Util.addSeperator(this.ref.end)));
    posSize.style.visibility = "hidden";
    this.overview.appendChild(posSize);

    // We want the stripes to be at least as wide as the position labels,
    // plus an arbitrary 20% padding so it's clear which grid line
    // a position label corresponds to.
    var minStripe = posSize.clientWidth * 1.2;
    this.overviewPosHeight = posSize.clientHeight;
    this.overview.removeChild(posSize);
    for (var n = 1; n < 30; n++) {
        // http://research.att.com/~njas/sequences/A051109
        // JBrowse uses this sequence (1, 2, 5, 10, 20, 50, 100, 200, 500...)
        // as its set of zoom levels.  That gives nice round numbers for
        // bases per block, and it gives zoom transitions that feel about the
        // right size to me. -MS
        this.overviewStripeBases = (Math.pow(n % 3, 2) + 1) * Math.pow(10, Math.floor(n/3));
        this.overviewStripes = Math.ceil(refLength / this.overviewStripeBases);
        if ((this.overviewBox.w / this.overviewStripes) > minStripe) break;
        if (this.overviewStripes < 2) break;
    }

    // Undocumented
    var overviewStripePct = 100 / (refLength / this.overviewStripeBases);
    var overviewHeight = 0;
    this.overviewTrackIterate(function (track, view) {
        track.clear();
        track.sizeInit(view.overviewStripes,
               overviewStripePct);
            track.showRange(0, view.overviewStripes - 1,
                            0, view.overviewStripeBases,
                            view.overviewBox.w /
                            (view.ref.end - view.ref.start));
    });
};

/**
 * Undocumented
 */
GenomeView.prototype.overviewTrackIterate = function(callback) {
    var overviewTrack = this.overview.firstChild;
    do {
        if (overviewTrack && overviewTrack.track)
        callback(overviewTrack.track, this);
    } while (overviewTrack && (overviewTrack = overviewTrack.nextSibling));
};

/**
 * Undocumented
 */
GenomeView.prototype.trimVertical = function(y) {
    if (y === undefined) y = this.getY();
    var trackBottom;
    var trackTop = this.topSpace;
    var bottom = y + this.dim.height;
    for (var i = 0; i < this.tracks.length; i++) {
        if (this.tracks[i].shown) {
            trackBottom = trackTop + this.trackHeights[i];
            if (!((trackBottom > y) && (trackTop < bottom))) {
                this.tracks[i].hideAll();
            }
            trackTop = trackBottom + this.trackPadding;
        }
    }
};

/**
 * Zooms in or out a given number of steps.
 * A positive number of steps means zoom in.
 * A negative number of steps means zoom out.
 */
GenomeView.prototype.zoomSteps = function(e, zoomLoc, steps) {
    // If something is already happening, drop
    if (this.animation) return;

    // Number of steps must be bounded
    if (steps == 0) return;
    if (steps >  0) {steps = Math.min(steps, (this.zoomLevels.length - 1) - this.curZoom);}
    else            {steps = Math.max(steps, -this.curZoom);}

    // showWait turns the mouse cursor into the "wait" cursor
    // then the post-zoom function "zoomUpdate" calls
    // the "showDone" that turns the mouse cursor back.
    this.showWait();
    var pos = this.getPosition();
    this.trimVertical(pos.y);
    var scale = this.zoomLevels[this.curZoom + steps] / this.pxPerBp;

    // Holds the current zoom level as an int
    this.oldZoom  = this.curZoom;
    this.curZoom += steps;

    // Update the position of the zoom slider
    dijit.byId("zoom_slider")._setValueAttr(this.curZoom);

    // zoomLoc is a number on [0,1] that indicates
    // the fixed point of the zoom
    if (zoomLoc === undefined) zoomLoc = 0.5;

    // If  we are zooming out, we must check the distance to
    // the edge of the chromosome and maybe change zoomLoc in
    // consequence
    if (steps < 0) {
        var edgeDist = this.bpToPx(this.ref.end) - (this.offset + pos.x + this.dim.width);
        zoomLoc = Math.max(zoomLoc, 1 - (((edgeDist * scale) / (1 - scale)) / this.dim.width));
        edgeDist = pos.x + this.offset - this.bpToPx(this.ref.start);
        zoomLoc = Math.min(zoomLoc, ((edgeDist * scale) / (1 - scale)) / this.dim.width);
    }

    // Pixel per base pairs
    var fixedBp = this.pxToBp(pos.x + this.offset + (zoomLoc * this.dim.width));
    this.pxPerBp = this.zoomLevels[this.curZoom];

    // Min and max left
    if (steps > 0) {this.maxLeft = (this.pxPerBp * this.ref.end) - this.dim.width;}
    else           {this.minLeft = this.pxPerBp * this.ref.start;}

    // Iterate over every track
    for (var track = 0; track < this.tracks.length; track++)
        this.tracks[track].startZoom(this.pxPerBp,
                                     fixedBp - ((zoomLoc * this.dim.width) / this.pxPerBp),
                                     fixedBp + (((1 - zoomLoc) * this.dim.width) / this.pxPerBp));

    // Copy self object
    var self = this;

    // The base pair coordinates for futher use
    self.leftBaseBeforeZoom  = (this.x + this.offset) / this.zoomLevels[this.oldZoom]
    self.leftBaseAfterZoom   = fixedBp - ((zoomLoc * this.dim.width) / this.pxPerBp)
    self.rightBaseBeforeZoom = (this.x + this.offset + this.dim.width) / this.zoomLevels[this.oldZoom]
    self.rightBaseAfterZoom  = fixedBp + (((1 - zoomLoc) * this.dim.width) / this.pxPerBp)

    // Zooms take an arbitrary 700 milliseconds, which feels about right
    // to me, although if the zooms were smoother they could probably
    // get faster without becoming off-putting. -MS
    new Zoomer(scale, this, function() {self.zoomUpdate(zoomLoc, fixedBp);}, 700, zoomLoc);
}

/**
 * Zooms to a given level, independently of the current zoom level.
 * @example brwsr.view.zoomTo(5);
 * @param zoomLevel {Integer} an integer between 0 and 19, indicating the new zoom level to be set.
 */
GenomeView.prototype.zoomTo = function(zoomLevel) {
    this.zoomSteps(undefined, undefined, zoomLevel - this.curZoom);
}

/**
 * Zooms in a given number of steps
 */
GenomeView.prototype.zoomIn = function(e, zoomLoc, steps) {
    if (steps === undefined) steps = 1;
    this.zoomSteps(e, zoomLoc, steps)
};

/**
 * Zooms out a given number of steps
 */
GenomeView.prototype.zoomOut = function(e, zoomLoc, steps) {
    if (steps === undefined) steps = 1;
    this.zoomSteps(e, zoomLoc, -steps)
};

/**
 * Undocumented
 */
GenomeView.prototype.zoomUpdate = function(zoomLoc, fixedBp) {
    var eWidth = this.elem.clientWidth;
    var centerPx = this.bpToPx(fixedBp) - (zoomLoc * eWidth) + (eWidth / 2);
    this.stripeWidth = this.stripeWidthForZoom(this.curZoom);
    this.scrollContainer.style.width =
        (this.stripeCount * this.stripeWidth) + "px";
    this.zoomContainer.style.width =
        (this.stripeCount * this.stripeWidth) + "px";
    var centerStripe = Math.round(centerPx / this.stripeWidth);
    var firstStripe = (centerStripe - ((this.stripeCount) / 2)) | 0;
    this.offset = firstStripe * this.stripeWidth;
    this.maxOffset = this.bpToPx(this.ref.end) - this.stripeCount * this.stripeWidth;
    this.maxLeft = this.bpToPx(this.ref.end) - this.dim.width;
    this.minLeft = this.bpToPx(this.ref.start);
    this.zoomContainer.style.left = "0px";
    this.setX((centerPx - this.offset) - (eWidth / 2));
    dojo.forEach(this.uiTracks, function(track) { track.clear(); });
    for (var track = 0; track < this.tracks.length; track++)
    this.tracks[track].endZoom(this.pxPerBp, Math.round(this.stripeWidth / this.pxPerBp));

    // The post-zoom start base will be: this.pxToBp(this.offset + this.getX())
    // The end base will be: this.pxToBp(this.offset + this.getX() + this.dim.width))
    this.showVisibleBlocks(true);
    this.showDone();
    this.showCoarse();
};

/**
 * Undocumented
 */
GenomeView.prototype.scrollUpdate = function() {
    var x = this.getX();
    var numStripes = this.stripeCount;
    var cWidth = numStripes * this.stripeWidth;
    var eWidth = this.dim.width;
    // dx: horizontal distance between the centers of
    // this.scrollContainer and this.elem
    var dx = (cWidth / 2) - ((eWidth / 2) + x);
    // If dx is negative, we add stripes on the right, if positive,
    // add on the left.
    // We remove stripes from the other side to keep cWidth the same.
    // The end goal is to minimize dx while making sure the surviving
    // stripes end up in the same place.
    var dStripes = (dx / this.stripeWidth) | 0;
    if (0 == dStripes) return;
    var changedStripes = Math.abs(dStripes);
    var newOffset = this.offset - (dStripes * this.stripeWidth);
    if (this.offset == newOffset) return;
    this.offset = newOffset;
    this.trackIterate(function(track) { track.moveBlocks(dStripes); });
    var newX = x + (dStripes * this.stripeWidth);
    this.updateTrackLabels(newX);
    this.rawSetX(newX);
    var firstVisible = (newX / this.stripeWidth) | 0;
};

/**
 * Undocumented
 */
GenomeView.prototype.trackHeightUpdate = function(trackName, height) {
    var y = this.getY();
    if (! trackName in this.trackIndices) return;
    var track = this.trackIndices[trackName];
    if (Math.abs(height - this.trackHeights[track]) < 1) return;
    // If the bottom of this track is a above the halfway point,
    // and we're not all the way at the top,
    if ((((this.trackTops[track] + this.trackHeights[track]) - y) < (this.dim.height / 2)) && (y > 0) ) {
        // Scroll so that lower tracks stay in place on screen
        this.setY(y + (height - this.trackHeights[track]));
    }
    this.trackHeights[track] = height;
    this.tracks[track].div.style.height = (height + this.trackPadding) + "px";
    var nextTop = this.trackTops[track];
    if (this.tracks[track].shown) nextTop += height + this.trackPadding;
    for (var i = track + 1; i < this.tracks.length; i++) {
        this.trackTops[i] = nextTop;
        this.tracks[i].div.style.top = nextTop + "px";
        if (this.tracks[i].shown)
            nextTop += this.trackHeights[i] + this.trackPadding;
    }
    this.containerHeight = Math.max(nextTop, this.getY() + this.dim.height);
    this.scrollContainer.style.height = this.containerHeight + "px";
};

/**
 * Undocumented
 */
GenomeView.prototype.showVisibleBlocks = function(updateHeight, pos, startX, endX) {
    if (pos === undefined) pos = this.getPosition();
    if (startX === undefined) startX = pos.x - (this.drawMargin * this.dim.width);
    if (endX === undefined) endX = pos.x + ((1 + this.drawMargin) * this.dim.width);
    var leftVisible = Math.max(0, (startX / this.stripeWidth) | 0);
    var rightVisible = Math.min(this.stripeCount - 1, (endX / this.stripeWidth) | 0);
    var bpPerBlock = Math.round(this.stripeWidth / this.pxPerBp);
    var startBase = Math.round(this.pxToBp((leftVisible * this.stripeWidth)+ this.offset));
    var containerStart = Math.round(this.pxToBp(this.offset));
    var containerEnd = Math.round(this.pxToBp(this.offset + (this.stripeCount * this.stripeWidth)));
    this.trackIterate(function(track, view) {
                          track.showRange(leftVisible, rightVisible, startBase, bpPerBlock, view.pxPerBp, containerStart, containerEnd);
                      });
    GDV_POST_FETCHER.send();
    // A move event is ending
    // Update the zone selection
    this.zoneSel.update(this);
};

/**
 * Undocumented
 */
GenomeView.prototype.addTrack = function(track) {
    var trackNum = this.tracks.length;
    var labelDiv = document.createElement("div");
    labelDiv.id = "label_" + track.name;
    this.trackLabels.push(labelDiv);
    var trackDiv = document.createElement("div");
    trackDiv.className = "track";
    trackDiv.id = "track_" + track.name;
    trackDiv.track = track;
    var view = this;
    var heightUpdate = function(height) {view.trackHeightUpdate(track.name, height);};
    track.setViewInfo(heightUpdate, this.stripeCount, trackDiv, labelDiv,  this.stripePercent, this.stripeWidth, this.pxPerBp);
    labelDiv.style.position = "absolute";
    labelDiv.style.top = "0px";
    var tmp = this.getX() + 100;
    labelDiv.style.left = tmp + "px";
    trackDiv.appendChild(labelDiv);
    
    //creating the scale and the zoom buttons
    //depending of the track type
    if(track instanceof ImageTrack){
        // #scale
	var container = document.createElement('DIV');
        container.style.position = "absolute";
        container.style.top = "0px";
        var newPos = this.getX() ;
        container.style.left = newPos + "px";
        container.style.width = "200px";
        container.style.height = "100px";
	
	var scale = document.createElement("canvas");
        scale.className = "track_scale";
        scale.style.position = "absolute";
        scale.style.top = "0px";
        // var newPos = this.getX() ;
        // scale.style.left = newPos+"px";
	scale.style.width = "15px";
        scale.style.height = "100px";
        scale.id = "scale_"+track.name;
        container.appendChild(scale);
	track.setScale(scale);
        
       
	// #inputs

	var input_max = document.createElement('input');
	input_max.className = 'score_input';
	input_max.type = 'text';
	input_max.name = 'max_score';
	input_max.id = track.name + '_max_input';
	container.max = input_max;
	container.appendChild(input_max);
	var input_min = document.createElement('input');
	input_min.className = 'score_input';
	input_min.type = 'text';
	input_min.name = 'min_score'
	input_min.style.bottom = '0px';
	container.min = input_min;
	container.appendChild(input_min);
		
    
	
	trackDiv.appendChild(container);
        track.scale_container = container;
	this.trackScales.push(container);

    }

    // A label starts unselected
    labelDiv.className = "track-label dojoDndHandle unselected";

    // When you click the label of a track
    // you select it or unselect it
    dojo.connect(labelDiv, "click", function(event){
        // Change the background color
        if (labelDiv.selected) {labelDiv.className = "track-label dojoDndHandle unselected"}
        else                   {labelDiv.className = "track-label dojoDndHandle selected"}
        // Flip the selected boolean
        labelDiv.selected = (labelDiv.selected == false);

        //update gfm form if one
        var textarea = dijit.byId("gfm_tracks");
        if(textarea){
            textarea.setValue(TrackSelection_get().join("; "));
        }
        dojo.stopEvent(event);
    });
    //TrackSelection_flip);

    // At first it is unselected
    labelDiv.selected = false;

    //add the right click menu context
    var gdv_id=track.gdv_id;
    // if(gdv_id){
    //     dojo.addOnLoad(function() {
    //         var pMenu = new dijit.Menu({
    //         targetNodeIds: [labelDiv.id]
    //         });
    //         pMenu.addChild(new dijit.MenuItem({
    //         label: "Configure track",
    //         onClick: function() {
    //                 window.open(_GDV_URL+"/configure_track?id="+gdv_id);
    //         }
    //         }));
    //         pMenu.startup();
    //     });
    // }

        return trackDiv;
};


/**
 * Executes the given function on every user inputed
 * track and on every interface track
 */
GenomeView.prototype.trackIterate = function(callback) {
    var i;
    for (i = 0; i < this.uiTracks.length; i++)
        callback(this.uiTracks[i], this);
    for (i = 0; i < this.tracks.length; i++)
        callback(this.tracks[i], this);
};

/**
 * This function must be called whenever tracks in the GenomeView
 * are added, removed, or reordered
 */
GenomeView.prototype.updateTrackList = function() {
    // New list to replace old one
    var tracks = [];

    // After a track has been dragged, the DOM is the only place
    // that knows the new ordering
    var containerChild = this.zoomContainer.firstChild;
    do {
    // This test excludes UI tracks, whose divs don't have a track property
        if (containerChild.track){
            tracks.push(containerChild.track);
    }
    } while ((containerChild = containerChild.nextSibling));

    //get the tracks unfolded
    // var list = dojo.query(".gdv_up_track").forEach(function(node, index, arr){
    //         var t = node.parentNode.parentNode.track;
    //         if(t){
    //         tracks.push(t);
    //         }
    //     });;

    // Update list
    this.tracks = tracks;
    var newIndices = {};
    var newHeights = new Array(this.tracks.length);
    for (var i = 0; i < tracks.length; i++) {
    newIndices[tracks[i].name] = i;
        if (tracks[i].name in this.trackIndices) {
            newHeights[i] = this.trackHeights[this.trackIndices[tracks[i].name]];
        } else {
            newHeights[i] = 0;
        }
        this.trackIndices[tracks[i].name] = i;
    }
    this.trackIndices = newIndices;
    this.trackHeights = newHeights;
    var nextTop = this.topSpace;
    for (var i = 0; i < this.tracks.length; i++) {
        this.trackTops[i] = nextTop;
        this.tracks[i].div.style.top = nextTop + "px";
        if (this.tracks[i].shown)
            nextTop += this.trackHeights[i] + this.trackPadding;
    }
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
