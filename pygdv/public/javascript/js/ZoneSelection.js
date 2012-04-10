/**
 * This file implements the horizontal selections.
 * With this, the user is able to define multiple and
 * discontinnus regions on the chromosome using
 * the marquee tool.
 * Not to be confused with selecting tracks.
 */

/**
 * The master object of the zone selection
 * A hook for this is found in Browser.js
 * @param {gv} the genome view object
 */
function ZoneSelection(gv) {
    this.gv = gv;
    this.canvas = document.createElement("canvas");
    this.canvas.id             = "zonesel_canvas";
    this.canvas.style.position = "absolute";
    this.canvas.style.zIndex   = 0;
    gv.elem.parentNode.appendChild(this.canvas);
    gv.setCursorToSelect(this.canvas);

    // Create a new marquee handler
    handler = new MarqueeHandler(this.canvas, gv, this);
    this.handler = handler;
    // Connect
    dojo.connect(this.canvas, "onmousedown", handler, handler.start);
    dojo.connect(this.canvas, "onmouseup",   handler, handler.stop);
    dojo.connect(window, "onresize", this, function(e) {
        this.handler.position();
        this.update(gv);
    });

    // Create a connector to handle update events
    this.connector = new SelConnector();

    // Add selections stored by GDV.
    // take the global variable "init_locations"
    if (init_locations){
        var ctx = this;
        dojo.addOnLoad(function(){
            ctx.addStoredSelections(init_locations, gv, handler);
        });
    }

    // //create an DOM node that will sore all selections
    // var store = document.createElement("span");
    // store.id="store_selections";
    // store.style.display="none";
    // dojo.body().appendChild(store);
};

/**
* Add the selections stored by GDV.
*/
ZoneSelection.prototype.addStoredSelections = function(selections, gv, handler){
    var l = selections.length;
    var lb = gv.minVisible();
    var fc = gv.pxPerBp;
    for (var i = 0; i<l ; i++){
        var selection = selections[i];
        var marquees = selection['locations'];
        var lm = marquees.length;
        for(var j =0;j<lm;j++){
            handler.add_marquee(marquees[j], lb, fc);
        }
    };
    handler.position();
    this.connector.afterUpdate(this, handler, handler.marquees);
};

/**
* Delete a selection
*/
ZoneSelection.prototype.delete = function(selection) {
    var handler = this.handler;
    handler.delete(selection);
    handler.position();
    this.updatedSelection();
};

/**
 * Returns a list of user made selections
 * Will print somethinig like "chr1:32712159 .. 218256629;chr2:101637029 .. 118236351"
 */
ZoneSelection.prototype.get = function() {
    var cur = this.handler.current;
    this.handler.marquees.sort(MarqueeSort);
    if(cur){
        return this.handler.marquees.map(function(m) {
            return m.chr + ':' + m.start + ' .. ' + m.end}).join(';') +
                    ";" + cur.chr + ":" + cur.start + " .. " + cur.end;
    } else {
        return this.handler.marquees.map(function(m) {
            return m.chr + ':' + m.start + ' .. ' + m.end}).join(';');
    }
};

/**
 * Called when the user clicks on the marquee tool button
 * in the upper left corner
 */
ZoneSelection.prototype.enableSel = function(event) {
    this.canvas.style.zIndex = 100;
    dojo.byId("enableSel").style.backgroundImage  = "url('" + window.picsPathRoot + "bkgnd_dark.png')";
    dojo.byId("disableSel").style.backgroundImage = "url('" + window.picsPathRoot + "bkgnd_light.png')";
    this.gv.disconnectMouse();
    this.handler.position();
    if (_gdv_pc) {
        _gdv_pc.show_selections();
    }
};

/**
 * Called when the user clicks on the move tool button
 * in the upper left corner
 */
ZoneSelection.prototype.disableSel = function(event) {
    this.canvas.style.zIndex = 0;
    dojo.byId("enableSel").style.backgroundImage  = "url('" + window.picsPathRoot + "bkgnd_light.png')";
    dojo.byId("disableSel").style.backgroundImage = "url('" + window.picsPathRoot + "bkgnd_dark.png')";
    this.gv.connectMouse();
};

/**
 * Called when the user is scrolling
 */
ZoneSelection.prototype.update = function(gv) {
    this.handler.update(gv.pxPerBp, gv.minVisible(), gv.maxVisible());
};

/**
 * Called after an update of the selection
 */
ZoneSelection.prototype.updatedSelection = function(){
    var handler = this.handler;
    var marquees = handler.marquees;
    //marquees.sort(MarqueeSort);
    this.connector.afterUpdate(this, handler, marquees);
};

/**
* Update the selection on the server
*/
ZoneSelection.prototype.update_on_server = function(){
    var xhrArgs = {
        url : _GDV_SEL_URL + '/save',
        postData : 'project_id=' + _gdv_info.project_id + '&color=grey&description="desc crip tion"&locations='
                                 + dojo.toJson(this.handler.marquees),
        error : function(data){ console.error(data); }
    };
    dojo.xhrPost(xhrArgs);
};






/**
 * Represents a selection
 * @params {x1} the start of the selection in pixels
 * @params {x2} the end   of the selection in pixels
 */
function Marquee(x1, x2, chr) {
    this.x1 = x1;      // Start in pixels
    this.x2 = x2;      // End in pixels
    this.alpha = 0.15; // Transparency
    this.chr   = chr; // The chromosome
    this.start = null; // Start in basepairs
    this.end   = null; // End in basepairs
    this.desc  = ''; // Description
};

/**
 * Reorders the coordinates if they are in the wrong direction
 */
Marquee.prototype.order = function() {
    if (this.x1 > this.x2) {
        tmp = this.x1;
        this.x1 = this.x2;
        this.x2 = tmp;
    }
};

/**
 * Return a String representation of a Marquee
 */
Marquee.prototype.display = function() {
    return this.chr + '(' + this.start + ', ' + this.end + ')';
};
/**
 * Changes alpha and finds base pairs
 */
Marquee.prototype.fixate = function(gv) {
    // Change transparency
    this.alpha = 0.35;
    // A selection must be at least one pixel thick
    if (this.x1 == this.x2) {
        this.x2 += 1;
    }
    // What are the coordinates of the selection
    factor = gv.pxPerBp;
    leftbase = gv.minVisible();
    this.start = Math.round(leftbase + (this.x1 / factor));
    this.end   = Math.round(leftbase + (this.x2 / factor));
    // Save the chromosome
    this.chr = gv.ref.name;
};

Marquee.prototype.navigateTo = function() {
    var c = (this.end - this.start) / 2;
    return this.chr + ':' + (this.start - c) + '..' + (this.end + c);
}


/**
 * Updates x1 and x2 using this.start and this.end
 */
Marquee.prototype.update = function(factor, leftbase) {
    this.x1 = Math.round((this.start - leftbase) * factor)
    this.x2 = Math.round((this.end   - leftbase) * factor)
    // A selection must be at least one base pair thick
    if (this.x1 == this.x2) {
        this.x2 = this.x1 + 1;
    }
};

/**
 * This object will handle all marquees created
 * by the user
 * @param{canvas} the canvas DOM element
 * @param {gv} the GenomeView object
 * @param{zoneSelection} the parent object
 */
function MarqueeHandler(canvas, gv, zoneSelection) {
    this.zoneSel = zoneSelection;
    this.marquees = [];            // list of all marquees
    this.canvas   = canvas;        // the canvas
    this.gv       = gv;            // the genome view
    this.height   = null;          // the height
    this.current  = null;          // the current marquee
    if (canvas.getContext) {this.context = canvas.getContext("2d");}
    else {console.error("This browser doesn't support canvases");}
};

/**
 * Delete a marquee
 */
MarqueeHandler.prototype.delete = function(marquee){
    var marquees = this.marquees;
    for(i in marquees){
        var m = marquees[i];
        if(m.chr == marquee.chr && m.start == marquee.start){
            marquees.splice(i,1);
            return;
        }
    }
};


/**
 * Positions the canvas.
 */
MarqueeHandler.prototype.position = function() {
    // Find the coordinates of the viewElem
    gv = this.gv;
    mywidth  = gv.elem.clientWidth;
    myheight = gv.elem.clientHeight;
    myleft   = gv.elem.offsetLeft;
    mytop    = gv.elem.offsetTop;
    // Set the height and width
    this.canvas.width  = mywidth;
    this.canvas.height = myheight;
    this.canvas.style.width  = mywidth  + 'px';
    this.canvas.style.height = myheight + 'px';
    // Top and left
    this.canvas.style.top  = mytop  + 'px';
    this.canvas.style.left = myleft + 'px';
    // Record the height
    this.height = myheight;
    // Redraw
    this.update(gv.pxPerBp, gv.minVisible(), gv.maxVisible());
};

/**
 * Starts a new selection.
 * Maybe make a new marquee or maybe get an existing one
 * and store it in the current slot. Finally, as the mouse moves,
 * we draw and draw until mouseout or mouseup.
 * @params {event} a MouseEvent object
 */
MarqueeHandler.prototype.start = function(event) {
    this.current = this.getMarquee(event.layerX);
    this.draw(this.marquees.filter(
        function(m) {
            return MarqueeFilter(m, this.gv)
        }
    ).concat(this.current));
    dojo.forEach(this.connections, function(c) {
        dojo.disconnect(c);
    });
    this.connections =
    [dojo.connect(this.canvas, "onmousemove", this, this.moving),
     dojo.connect(this.canvas, "onmouseout",  this, this.stop)];
};

/**
 * Add a marquee.
 */
MarqueeHandler.prototype.add_marquee = function(selection, leftbase, factor) {
    var start = selection['start'];
    var end = selection['end'];
    var x1 = (start - leftbase) * factor;
    var x2 = (end - leftbase ) * factor;
    var m = new Marquee(x1, x2, selection['chr']);
    m.start = start;
    m.end = end;
    m.id = selection['id'];
    m.desc = selection['desc'];
    this.mergeMarquee(m);
    this.marquees.push(m);
};

/**
 * Returns the current marquee if the cursor
 * is on a drawed marquee, else creates a new marquee
 * @params {x0} cursor left on the canvas
 * Strange: without the "return false", the function gets called twice ?
 */
MarqueeHandler.prototype.getMarquee = function(x0) {
    len = this.marquees.length
    for(var i=0; i<len; i++){
        m = this.marquees[i]
        if (m.chr != this.gv.ref.name) {
            continue;
        }
        // not the right chr
        if ((m.x1 <= x0) && (x0 <= m.x2)) {        // the cursor is on a marquee
            m.alpha = 0.15;                        // change transparency
            if (x0-m.x1 > m.x2-x0) { m.x2 = x0; }    // closer to left edge
            else { m.x1 = m.x2; m.x2 = x0; }         // closer to right edge
            return this.marquees.splice(i, 1)[0];  // remove that marquee
        }
    }
    return new Marquee(x0, x0);
};

/**
 * Update the canvas as the mouse moves
 * @params {event} a MouseEvent object
 */
MarqueeHandler.prototype.moving = function(event) {
    // Update current marquee
    this.current.x2 = event.layerX;
    // Redraw both existing and current marquee
    this.draw(this.marquees.filter(
        function(m) {
            return MarqueeFilter(m, this.gv)
        }).concat(this.current))
};

/**
 * Draws marquees on the canvas
 * @params {marquees} a list of marquees
 */
MarqueeHandler.prototype.draw = function(list) {
    // Extract variables
    var context = this.context;
    var height = this.height;
    var canvas = this.canvas;
    // Redraw every marquee in the list
    context.clearRect(0, 0, canvas.width, canvas.height)
    dojo.forEach(list, function(m) {
        context.fillStyle = 'rgba(0,0,0,0.2);'
        context.globalAlpha = 0.2;
        if (m.x1 < m.x2) {context.fillRect(m.x1, 0, m.x2-m.x1, height);}
        else             {context.fillRect(m.x2, 0, m.x1-m.x2, height);}
    });
};

/**
 * Ends the selection
 * @params {event} a MouseEvent object
 */
MarqueeHandler.prototype.stop = function(event) {
    if (this.current == null) {return false;}
    this.current.x2 = event.layerX;    // Set final left
    this.current.order()                // If reverse order, invert
    this.mergeMarquee(this.current);    // Maybe merge or maybe not
    this.current.fixate(this.gv)        // Find base pairs
    this.marquees.push(this.current);   // Add it to the list
    this.current = null;                // Delete it
    // A final draw of the visible ones
    this.draw(this.marquees.filter(function(m) {
        return MarqueeFilter(m, this.gv);
    }));
    // Free the mouse actions
    dojo.forEach(this.connections, function(c) {
        dojo.disconnect(c);
    });
    this.zoneSel.updatedSelection();
};

/**
 * Merge the current marquee if it overlaps
 * with any other marquee on the same chr
 * @params{current} the current marquee
 */
MarqueeHandler.prototype.mergeMarquee = function(current) {
    // Find all marquees that are overlapping
    overlapping = []
    for (var i = this.marquees.length - 1; i >=0; i--) {
        m = this.marquees[i]
        if ((m.chr == this.gv.ref.name) && (m.x1 <= current.x2) && (m.x2 >= current.x1))
            {overlapping.push(this.marquees.splice(i,1)[0])}
    }
    // Find largest overlaping interval
    x1 = current.x1; x2 = current.x2
    var desc = [];
    dojo.forEach(overlapping, function(m) {
        if (m.desc) {desc.push(m.desc);}
        if (m.x1 < x1) {x1 = m.x1;}
        if (m.x2 > x2) {x2 = m.x2;}
    });
    if(desc){current.desc = desc.join(' | ');}
    current.x1 = x1; current.x2 = x2
};

/**
 * Called when the user is scrolling or sliding or zooming
 */
MarqueeHandler.prototype.update = function(factor, leftbase, rightbase) {
    // Update the coordinates in pixels of every marquee
    // and draw only those that can be seen
    var ctx = this;
    this.draw(this.marquees.filter(function(m) {
        if (m.chr != ctx.gv.ref.name) {return false;}
        m.update(factor, leftbase);
        return ((m.end > leftbase) && (m.start < rightbase));
    }));
};

/**
 * Used for filtering marquees
 * Will return true only if m can be seen
 * It needs the genome view as an input
 */
MarqueeFilter = function(m, gv) {
    return (m.end > this.gv.minVisible()) && (m.start < this.gv.maxVisible()) && (m.chr == this.gv.ref.name);
};

/**
 * This object will connect all events linked to the update
 * of the selection
 */
function SelConnector(){
}

/**
 * Called after an update of the selection
 * @param{zoneSel} - the zone selection object
 * @param{handler} - the handler of all marquees
 * @param{selections} - the marquees
 */
SelConnector.prototype.afterUpdate = function(zoneSel, handler, selections){
    selections.sort(MarqueeSort);
    zoneSel.sel_pane.update(selections);
};


/**
 * Used for sorting marquees
 */
MarqueeSort = function(a, b) {
    var chroms = _gdv_info.gb.chromList.childNodes;
    L = chroms.length;
    var chromlist = []
    for (var i=0; i<L; i++){
        chromlist.push(chroms[i].value);
    }
    var achr = chromlist.indexOf(a.chr);
    var bchr = chromlist.indexOf(b.chr);
    if (achr == bchr) {
        if (a.x1 == b.x1) return 0;
        else if (a.x1 < b.x1) return -1;
        else return 1;
    }
    else if (achr <  bchr) return -1;
    else return  1;
    return  0;
}


