
/**
 * The master object of the minimap
 * A hook for this is found in Browser.js
 */
function Minimap(view) {
    var minimap = this;
    this.gv = view;
    this.padding = 4;
    this.overview = dojo.byId("overview"); //container of the minimap
    this.height = this.overview.clientHeight - 2 * this.padding;
    this.width = this.overview.clientWidth - 2;

    var canvas = dojo.byId("minimap");
    this.canvas = canvas;
    console.log(this.overview, this.canvas)
    // Redraw when the window is resized
    dojo.connect(window, "onresize", this, function(e) {this.draw();});
    //dojo.connect(this.overview, "onDndDrop", function(source, nodes, copy, target) {
    dojo.connect(this.overview, "onDrop", function(e) {
        alert("Create minitrack");
        this.drawMiniTrack();
    });
}

/*
 * Called on load of the page or chromosome change
 */
Minimap.prototype.draw = function() {
    if (this.canvas.getContext){
        this.reset();
        this.drawMiniChromosome();
    // Dummy image if canvas is not supported
    } else {
        this.overview.style.backgroundImage = "url('" + window.picsPathRoot + "dummy_chromosome.png')";
    }
}

/*
 * Clear the canvas and redraw contour and background filling
 */
Minimap.prototype.reset = function() {
    this.canvas.width = this.overview.clientWidth - 2;
    var ctx = this.canvas.getContext('2d');
    // Clear
    ctx.save(); ctx.setTransform(1,0,0,1,0,0);
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.restore();
    // Contour
    var h = this.canvas.height/2;
    var L = this.canvas.width;
    var lw = 0;
    ctx.lineWidth = 1+lw;
    ctx.beginPath();
    ctx.arc(h+1, h, h-lw-1, 0.5*Math.PI, 1.5*Math.PI);
    ctx.lineTo(L-h-1, lw+1);
    ctx.arc(L-h-1, h, h-lw-1, 1.5*Math.PI, 0.5*Math.PI);
    ctx.lineTo(h+1, 2*h-lw-1);
    ctx.stroke();
    // Background
    ctx.fillStyle = "#999999";
    ctx.fill();
}

/*
 * Draws the mini-track inside of the minimap
 */
Minimap.prototype.drawMinitrack = function() {
    var ctx = this.canvas.getContext('2d');
    this.reset();
    console.log("New minitrack")
};

/*
 * Draws the mini-chromosome inside of the minimap
 */
Minimap.prototype.drawMiniChromosome = function() {
    var ctx = this.canvas.getContext('2d');
    this.reset;

    // Get the cytosomal bands
    this.chr_length = this.gv.ref['length']; // chromosome length
    callback = dojo.hitch(this, function(bands) {
        this.bands = bands;
        this.count = this.bands.length;
        if(this.count === 0){
            console.info('GenRep is telling there is no bands on this chromosome.');
        };
    });
    this.gv.genrep.bands(this.gv, callback);

    // If there are no bands on the chromosome, stop
    if (this.count === 0) return;
    // Iterate over every band
    for (var i=0; i<this.count; i++) {
        // Compute drawing coordinates
        var pos   = this.bands[i]['band']['position'];
        var start = this.bands[i]['band']['start'] * (this.width / this.chr_length) + 1;
        var end   = this.bands[i]['band']['end']   * (this.width / this.chr_length) + 1;
        // Draw centromeres differently
        if (!pos) {
            ctx.rect(start, this.padding, end-start, this.height, 0);
        }
        else if (pos == 'left')  {
            r = roundedRectangle(ctx, start, this.padding, end-start, this.height, 2, "#999", "white");
            left = start;
        }
        else if (pos == 'right') {
            r = roundedRectangle(ctx, start, this.padding, end-start, this.height, "#999", "white");
            ctx.rect(left, this.padding, end-left, this.height, 9);
        }
        // Fill the color depending on the stain variable
        ctx.lineWidth = 0;
        ctx.fillStyle = this.stains[this.bands[i]['band']['stain']];
        ctx.fill();
    }
}

/**
 * Draws a rounded rectangle using the current state of the canvas.
 * stroke & fill: (optional) strings, color of respectively stroke and fill
 */
function roundedRectangle(ctx, x, y, width, height, radius, stroke, fill) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    if (stroke) {
        ctx.fillStyle = stroke;
        ctx.stroke();
    }
    if (fill) {
        ctx.fillStyle = fill;
        ctx.fill();
    }
}






/**
 * Called when the page is loaded
 * or the chromosome is changed.
 * The bands will be reloaded and redrawn
 */
Minimap.prototype.update = function() {
    // Get the chromsome total length
    this.chr_length = this.gv.ref['length'];
    // Get the cytosomal bands
    callback = dojo.hitch(this, function(bands) {
        this.bands = bands;
        this.count = this.bands.length;
        if(this.count === 0){
            console.info('GenRep is telling there is no bands on this chromosome.');
        };
        dojo.byId('overview').style.backgroundImage = "";
        this.draw();
    });
    var gv = this.gv;
    gv.genrep.bands(gv, callback);
};

/**
 * A dictionary linking stain attribute
 * to RGB colors
 */
Minimap.prototype.stains = {
    'gneg':    "90-#ccc:30-#fff",
    'gpos25':  "90-#999:30-#ccc",
    'gpos50':  "90-#777:30-#999",
    'gpos75':  "90-#555:30-#777",
    'gpos100': "90-#222:30-#555",
    'acen':    "90-#111:30-#222"
};

/**
 * Extension of the Rapheal library to
 * add custom rounded rectangles
 * roundedRectangle(x, y, width, height, upper_left_corner, upper_right_corner, lower_right_corner, lower_left_corner)
 * Credits: http://tinyurl.com/3jd6er9
 */
Raphael.fn.roundedRectangle = function (x, y, w, h, r1, r2, r3, r4){
  var array = [];
  array = array.concat(["M",x,r1+y, "Q",x,y, x+r1,y]);
  array = array.concat(["L",x+w-r2,y, "Q",x+w,y, x+w,y+r2]);
  array = array.concat(["L",x+w,y+h-r3, "Q",x+w,y+h, x+w-r3,y+h]);
  array = array.concat(["L",x+r4,y+h, "Q",x,y+h, x,y+h-r4, "Z"]);
  return this.path(array);
};

/**
 * Draws the bands
 */
Minimap.prototype.draw_old = function() {
    // Clear the canvas
    this.raph.clear();
    // Update the element width
    this.width = this.overview.clientWidth - 2;
    // Check that we have bands
    if (this.count === 0) {
        r = this.raph.rect(2, this.padding, this.width - 2, this.height, 9);
        r.attr({fill: '90-#999:30-#ccc'});
        return;
    }
    // Iterate over every band
    for (var i=0; i<this.count; i++) {
        // Compute drawing coordinates
        var pos   = this.bands[i]['band']['position'];
        var start = this.bands[i]['band']['start'] * (this.width / this.chr_length) + 1;
        var end   = this.bands[i]['band']['end']   * (this.width / this.chr_length) + 1;
        // Draw centromeres differently
        if (!pos) {
            r = this.raph.rect(start, this.padding, end-start, this.height, 0);
        }
        else if (pos == 'left')  {
            r = this.raph.roundedRectangle(start, this.padding, end-start, this.height, 9, 0, 0, 9);
            left = start;
        }
        else if (pos == 'right') {
            r = this.raph.roundedRectangle(start, this.padding, end-start, this.height, 0, 9, 9, 0);
            this.raph.rect(left, this.padding, end-left, this.height, 9);
        }
        // Fill the color depending on the stain variable
        r.attr({fill: this.stains[this.bands[i]['band']['stain']]});
        r.attr({'stroke-width': '0'});
    }
};

