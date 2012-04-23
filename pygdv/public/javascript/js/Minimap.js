
/**
 * The master object of the minimap
 * A hook for this is found in Browser.js
 */
function Minimap(browser,view) {
    var minimap = this;
    this.brwsr = browser;
    this.gv = view;
    this.overview = dojo.byId("overview"); //container of the minimap
    this.height = this.overview.clientHeight;
    this.width = this.overview.clientWidth - 2;
    this.canvas = dojo.byId("minimap");
    // Redraw when the window is resized
    dojo.connect(window, "onresize", this, function(e) {this.draw();});
    dojo.connect(this.overview, "onmouseover", function(e) {
        browser.minimapWidget.copyOnly = true;
        //browser.minimapWidget.copyState = function(keyPressed,self){ return true; };
        //console.log("true")
    });
    dojo.connect(this.overview, "onmouseout", function(e) {
        browser.minimapWidget.copyOnly = false;
        //browser.minimapWidget.copyState = function(keyPressed,self){ return false; };
        //console.log("false")
    });
    dojo.connect(this.brwsr.minimapWidget, "onDrop", function(source, nodes, copy) {
        //copy = true;
        //console.log("e",source, nodes, copy, browser.minimapWidget.copyState, browser.minimapWidget.copyOnly)
    });
}

/*
 * (Re-)draw the minimap on load of the page or chromosome change
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
 * Draw the grey border of the minimap.
 */
function drawContour(ctx, width, height){
    var h = height/2;
    var L = width;
    ctx.strokeStyle = "#444";
    ctx.beginPath();
    ctx.arc(h, h, h-1, 0.5*Math.PI, 1.5*Math.PI);
    ctx.lineTo(L-h, 1);
    ctx.arc(L-h, h, h-1, 1.5*Math.PI, 0.5*Math.PI);
    ctx.lineTo(h, 2*h-1);
    ctx.closePath();
    ctx.stroke();
};

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
    drawContour(ctx, this.canvas.width, this.canvas.height);
    ctx.fillStyle = "#999999";
    ctx.fill();
}

/*
 * Draw the mini-track inside of the minimap
 */
Minimap.prototype.drawMinitrack = function(track) {
    var minimap = this;
    var ctx = this.canvas.getContext('2d');
    this.reset();
    console.log("New minitrack");

    dojo.xhrPost({
        url: _GDV_URL_DB + '/minimap',
        postData: track.db,
        load: function(data) {
            draw_minitrack(data);
        }
    });

    // Testing
    var data = [1,1.4, 12,3.1, 24,5.6, 36,1.1, 45,7.8, 78,3,2]; //[pos,score,pos,score,...]
    draw_minitrack(data);

    var draw_minitrack = function(data){
        var clen = data.length;
        var barw = clen / 2*data.chr_length;
        var barh = minimap.canvas.height;
        for (var i=0; i<clen; i=i+2) {
            var pos = data[i] * (minimap.canvas.width / minimap.chr_length) + 1;
            var score = data[i+1];
            ctx.beginPath();
            ctx.rect(pos, 0, pos+barw, y+barh);
            ctx.closePath();
            ctx.fillStyle("black");
            ctx.fill();
        }
    }
    drawContour(ctx, this.canvas.width, this.canvas.height);
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
        if(this.count === 0){ console.info('GenRep says: no bands on this chromosome.'); };
        for (var i=0; i<this.count; i++) {
            // Compute drawing coordinates
            var pos   = this.bands[i]['band']['position'];
            var start = this.bands[i]['band']['start'] * (this.canvas.width / this.chr_length) + 1;
            var end   = this.bands[i]['band']['end']   * (this.canvas.width / this.chr_length) + 1;
            var stain = this.stains[this.bands[i]['band']['stain']];
            var gradient = ctx.createLinearGradient(0,0,0,this.canvas.height);
            gradient.addColorStop(0.7,stain[0]);
            gradient.addColorStop(0.3,stain[1]);
            ctx.beginPath();
            ctx.rect(start, 1, end-start, this.canvas.height-2);
            ctx.closePath();
            ctx.lineWidth = 0;
            ctx.fillStyle = gradient; //stain[1];
            ctx.fill();
        }
        clearCorners(ctx, 0, 0, this.canvas.width, this.canvas.height, this.canvas.height/2+1);
        drawContour(ctx, this.canvas.width, this.canvas.height);
    });
    this.gv.genrep.bands(this.gv, callback);
};

/*
 * After drawing the mini chromosome, round the corners at extremities.
 */
function clearCorners(ctx, x, y, width, height, r) {
    var clearCorner = function(ctx, x, y, r) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x+r, y);
        ctx.arc(x+r, y+r, r, 1.5*Math.PI, 1*Math.PI, true)
        ctx.closePath();
        ctx.fill();
    };
    ctx.save();
    ctx.fillStyle = "#dedede";
    clearCorner(ctx, x, y, r); // top left
    ctx.translate(0,height);
    ctx.rotate(1.5*Math.PI);
    ctx.fillStyle = "#cfcfcf";
    clearCorner(ctx, x, y, r); // bottom left
    ctx.translate(0,width);
    ctx.rotate(1.5*Math.PI);
    ctx.fillStyle = "#cfcfcf";
    clearCorner(ctx, x, y, r); // bottom right
    ctx.translate(0,height);
    ctx.rotate(1.5*Math.PI);
    ctx.fillStyle = "#dedede";
    clearCorner(ctx, x, y, r); // top right
    ctx.restore();
}

/**
 * A dictionary linking stain attribute to RGB colors, to draw the mini chromosome.
 */
Minimap.prototype.stains = {
    'gneg':    ["#ccc","#fff"], //"90-#ccc:30-#fff",
    'gpos25':  ["#999","#ccc"], //"90-#999:30-#ccc",
    'gpos50':  ["#777","#999"], // "90-#777:30-#999",
    'gpos75':  ["#555","#777"], // "90-#555:30-#777",
    'gpos66':  ["#444","#666"],
    'gpos33':  ["#333","#555"],
    'gpos100': ["#222","#444"], // "90-#222:30-#555",
    'acen':    ["#111","#333"], // "90-#111:30-#222"
};

