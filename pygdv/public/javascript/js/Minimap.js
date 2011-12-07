/**
 * This file implements the chromosome minimap drawing.
 */

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
 * The master object of the minimap
 * A hook for this is found in Browser.js
 */
function Minimap(gv) {
    // Store the view
    this.gv = gv;
    // Define some constants
    this.padding = 4;
    // Store the overview element
    this.overview = dojo.byId("overview");
    this.height = this.overview.clientHeight - 2 * this.padding;
    // Make a raphael graphics object
    this.raph = Raphael("overview", "100%", "100%");
    // Redraw when the window is resized
    dojo.connect(window, "onresize", this, function(e) {this.draw();});
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
    this.gv.genrep.bands(callback);
};

/**
 * A dictionaty linking stain attribute
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
 * Draws the bands
 */
Minimap.prototype.draw = function() {
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
