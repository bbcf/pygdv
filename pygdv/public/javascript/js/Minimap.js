
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
    console.log("track_to_minitrack",track)
    var minimap = this;
    var ch = minimap.canvas.height;
    var cw = minimap.canvas.width;
    var ctx = this.canvas.getContext('2d');
    this.reset();

    // put this somewhere else
    this.chr_length = this.gv.ref['length']; // chromosome length
    track.md5 = track.url.split("/")[0];

    dojo.xhrPost({
        url: _GDV_URL_DB + '/minimap',
        postData: "type=" + track.type + "&db=" + track.md5 + "&chr_zoom=" + 100,
        load: function(x) {
            x = JSON.parse(x);
            draw_minitrack(x.data);
        }
    });
    var draw_minitrack = function(data){
        var len = data.length;
        var ch = minimap.canvas.height;
        var cw = minimap.canvas.width;
        positions = []; scores = []; scores2 = [];
        for (var i=0; i<len; i=i+2) {
            positions.push(data[i]);
            scores.push(data[i+1]);
            scores2.push(data[i+1]);
        }
        var max_score = scores2.sort(function(a,b){return b-a})[0];
        var height_ratio = ch / max_score;
        var width_ratio = cw / minimap.chr_length;
        for (var i=0; i<len/2; i++) {
            var start = positions[i] * width_ratio;
            var end   = positions[i+1] * width_ratio;
            if (!end) end = cw; // last piece
            if (scores[i] != 0) {
                var barh = 0.9 * scores[i] * height_ratio;
                ctx.beginPath();
                ctx.rect(start, ch-barh+1, end-start, barh-2);
                ctx.closePath();
                ctx.fillStyle = "black";
                ctx.fill();
            }
        }
        clearCorners(ctx, 0, 0, cw, ch, ch/2+1);
        drawContour(ctx, cw, ch);
    }
};

/*
 * Draw the mini-chromosome (cytosomal bands) inside of the minimap
 */
Minimap.prototype.drawMiniChromosome = function() {
    var ctx = this.canvas.getContext('2d');
    this.reset;
    this.chr_length = this.gv.ref['length']; // chromosome length
    var ch = this.canvas.height;
    var cw = this.canvas.width;
    var width_ratio = cw / this.chr_length;
    callback = dojo.hitch(this, function(bands) { // hitch makes it asynchronous
        this.bands = bands;
        this.count = this.bands.length;
        if(this.count === 0){ console.info('GenRep says: no bands on this chromosome.'); };
        for (var i=0; i<this.count; i++) {
            // Compute drawing coordinates
            var pos   = this.bands[i]['band']['position'];
            var start = this.bands[i]['band']['start'] * width_ratio + 1;
            var end   = this.bands[i]['band']['end']   * width_ratio + 1;
            var stain = this.stains[this.bands[i]['band']['stain']];
            var gradient = ctx.createLinearGradient(0,0,0,this.canvas.height);
            gradient.addColorStop(0.7,stain[0]);
            gradient.addColorStop(0.3,stain[1]);
            ctx.beginPath();
            ctx.rect(start, 1, end-start, this.canvas.height-2);
            ctx.closePath();
            ctx.lineWidth = 0;
            ctx.fillStyle = gradient;
            ctx.fill();
        }
        clearCorners(ctx, 0, 0, this.canvas.width, this.canvas.height, this.canvas.height/2+1);
        drawContour(ctx, this.canvas.width, this.canvas.height);
    });
    this.gv.genrep.bands(this.gv, callback);
};

/*
 * After drawing the minimap, round the corners at extremities.
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

