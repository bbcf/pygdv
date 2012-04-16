
/**
 * The master object of the minimap
 * A hook for this is found in Browser.js
 */
function Minimap(view) {
    var minimap = this;
    this.gv = view;
    this.overview = dojo.byId("overview"); //container of the minimap
    this.height = this.overview.clientHeight - 2 * 0;
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
 * Draw the mini-track inside of the minimap
 */
Minimap.prototype.drawMinitrack = function() {
    var ctx = this.canvas.getContext('2d');
    this.reset();
    console.log("New minitrack")
};

/*
 * Draw the mini-chromosome (cytosomal bands) inside of the minimap
 */
Minimap.prototype.drawMiniChromosome = function() {
    var ctx = this.canvas.getContext('2d');
    this.reset;
    this.chr_length = this.gv.ref['length']; // chromosome length
    callback = dojo.hitch(this, function(bands) { // hitch makes it asynchronous
        this.bands = bands;
        this.count = this.bands.length;
        if(this.count === 0){
            console.info('GenRep is telling there is no bands on this chromosome.');
        };
        for (var i=0; i<this.count; i++) {
            // Compute drawing coordinates
            var pos   = this.bands[i]['band']['position'];
            var start = this.bands[i]['band']['start'] * (this.canvas.width / this.chr_length) + 1;
            var end   = this.bands[i]['band']['end']   * (this.canvas.width / this.chr_length) + 1;
            ctx.beginPath();
            if (!pos) { // 'normal' band
                ctx.rect(start, 1, end-start, this.canvas.height-2);
                last = start;
            } else if (pos == 'left')  { // first band
                roundedRectangle(ctx, start+1, 1, end-start, this.canvas.height-2, [8,0,0,8]);
            } else if (pos == 'right') { // last band
                roundedRectangle(ctx, start, 1, end-start-1, this.canvas.height-2, [0,8,8,0]);
                ctx.rect(last-1, 1, start-last+1, this.canvas.height-2);
            }
            // Fill the color depending on the stain variable
            ctx.closePath();
            ctx.lineWidth = 0;
            ctx.fillStyle = this.stains[this.bands[i]['band']['stain']];
            ctx.fill();
        }
    });
    this.gv.genrep.bands(this.gv, callback);
};

/**
 * Draws a rounded rectangle using the current state of the canvas.
 * stroke & fill: (optional) strings, color of respectively stroke and fill.
 * *radius* can either be a number (same 4 corners) or a length-4 array
 * (4 different corner radii): [bottom left, bottom right, top right, top left].
 */
function roundedRectangle(ctx, x, y, width, height, radius) {
    if (isNaN(radius) && radius.length == 4) {
        r1 = radius[0]; r2 = radius[1]; r3 = radius[2]; r4 = radius[3];
    } else {
        r1 = r2 = r3 = r4 = radius;
    }
    ctx.moveTo(x + r1, y);
    ctx.lineTo(x + width - r2, y); // bottom line
    ctx.arc(x + width - r2, y + r2, r2, 1.5*Math.PI, 0, true); // bottom right angle
    ctx.lineTo(x + width, y + height - r3); // right line
    ctx.arc(x + width - r3, y + height - r3, r3, 0, 0.5*Math.PI, true); // top right angle
    ctx.lineTo(x + r4, y + height); // top line
    ctx.arc(x + r4, y + height - r4, r4, 0.5*Math.PI, Math.PI, true); // top left angle
    ctx.lineTo(x, y + r1); // left line
    ctx.arc(x + r1, y + r1, r1, Math.PI, 1.5*Math.PI, true); // bottom left angle
}

/**
 * A dictionary linking stain attribute to RGB colors
 */
Minimap.prototype.stains = {
    'gneg':    "#cccccc", //"90-#ccc:30-#fff",
    'gpos25':  "#999999", //"90-#999:30-#ccc",
    'gpos50':  "#777777", // "90-#777:30-#999",
    'gpos75':  "#555555", // "90-#555:30-#777",
    'gpos66':  "#444444",
    'gpos33':  "#333333",
    'gpos100': "#222222", // "90-#222:30-#555",
    'acen':    "#111111" // "90-#111:30-#222"
};

