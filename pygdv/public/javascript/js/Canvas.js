/*
 * This script will handle to load databases scores
 * for each quantitative tracks in the browser interface.
 * It will request the score to GDV with a POST request,
 * then handle the result and draw the canvas.
 */


fetched = {};
var GDV_POST_FETCHER = new GDVPostBuffer();





/**
 * simulate a buffer that receive all post to do
 * to get the scores, merge them and send them in one
 * POST when send() is called
 */
function GDVPostBuffer(){}

/**
 * initialisation of the buffer
 */
GDVPostBuffer.prototype.init = function(){
    this.fetched = {};
    this.db = [];
};

/**
 * Add a track to the drawer, if it's not already added
 * @param database - the String representing the track, the database to fetch
 * @param images - a list of image to add
 */
GDVPostBuffer.prototype.addTrack = function(database,images){
    this.fetched[database]=images;
    if(!(this.db.join().indexOf(database)>-1)){
	this.db.push(database);
    }
};

/**
 *  Get a Track by it's id. Return an empty array if the key not
 * exist.
 * @param database - the key representing the track
 */
GDVPostBuffer.prototype.getTrack = function(database){
    if(this.fetched[database]){
	return this.fetched[database];
    } else {
	return [];
    }
};

/**
 * Reinitialize the buffer
 */
GDVPostBuffer.prototype.clear = function(){
    this.init();
};

GDVPostBuffer.prototype.send = function(){
    var dbList = this.db;
    var post_buffer = this;
    dojo.forEach(dbList,function(db,i){
	    post_buffer.post(db);
	});
    this.clear();
};


/**
 * send the POSTs
 * @param database - the key representing the track
 */
GDVPostBuffer.prototype.post = function(database){
    var imgs = this.getTrack(database);
    var db = database.split('/')
    var sha1 = db[0]
    var chrzoom = db[1]
    var pData = 'sha1=' + db[0] + '&chr_zoom=' + db[1] + '&imgs=';
    var pDataL = pData.length;
    var post_buffer = this;
    var _imgs= [];
    dojo.forEach(imgs,function(item,i,arr){
	    var nb = item.nb;
	    if(!(_imgs.join().indexOf(nb)>-1)){
		_imgs.push(nb);
		if(!(post_buffer.getScore(database,nb))){
		    pData+=item.nb+",";
		} else {
		    var imd = new ImageDrawer();
		    imd.drawScores(item,this.getScore(database,item),item.color);
		}

	    }
        });
    if(pData.length>pDataL){
	pData = pData.substr(0,pData.length-1);
	drawer = new ImageDrawer();
	var xhrArgs = {
	    url: _GDV_URL_SCORES,
	    postData: pData,
	    handleAs: "json",
	    load: function(data) {
		drawer.putScore(imgs,data);
	    }
	}
	dojo.xhrPost(xhrArgs);
    } 
};




/** 
 * return the score if it's already loaded    
 * else return false
 */
GDVPostBuffer.prototype.getScore = function(db,img){
    var sc = dojo.byId("sq_"+db+"_"+img);
    if(sc){
        return sc.innerHTML;
    }
    return false;
}













/**
 * Regroups all methods to featch score &
 * draw them on a canvas
 *
 */
function ImageDrawer() {}

/**
 * initialize the canvas physically : 
 * a div named sqlite_scores will be created next                                                                                                                                                       
 * to the GenomeBrowse with the purpose to contains                                                                                                                                                      
 * all scores already loaded by GDV 
 *
 * initialize a buffer for the POST methods
 */
function initCanvas(){
    var imageDrawer = new ImageDrawer();
    imageDrawer.initDrawer();
    GDV_POST_FETCHER.init();
}

/**
 * Initialize Image drawer
 * - a div named sqlite_scores will be created next 
 * to the GenomeBrowse with the purpose to contains
 * all scores already loaded by GDV
 */
function initImageDrawer(){
    var imageDrawer = new ImageDrawer();
    imageDrawer.initDrawer();
}


/**
 * function which create and
 * add a div next to GenomeBrowser
 */
ImageDrawer.prototype.initDrawer = function(){
    var scores = document.createElement("span");
    scores.id = "sqlite_scores";
    scores.style.cssText = "display:none;";
    document.body.appendChild(scores);
};





ImageDrawer.prototype.drawScores_ = function(node,jsonText,color){
    if(jsonText){
        if(jsonText!="{}"){
	    var data = dojo.fromJson(jsonText);
	    
	    var _data_=[];
	    var p = 0;
	    var c = 0;
	    for(i in data){
		while(c<i){
		    _data_.push(data[p]);
		    c++;
		}
		c++;
		p=i;
		_data_.push(data[p]);
	    }
	    var start = + new Date();
	    var chart1 = new Highcharts.Chart({
		chart: {
		    renderTo: node,
		    type: 'bar'
		},
		title: {
		    text: 'Fruit Consumption'
		},
		xAxis: {
		    categories: ['Apples', 'Bananas', 'Oranges']
		},
		yAxis: {
		    title: {
			text: 'Fruit eaten'
		    }
		},
		series: [{
		    name: 'test2.wig',
		    data: _data_
		}]
	    });
	}
    }
}

/**
 * Draw the scores on the view
 * @param node - the HTML node to write on
 * @param jsonText - the scores
 * @param color - the color to write in
 */
ImageDrawer.prototype.drawScores = function(node,jsonText,color){
    /* default color*/
    if(!color){
	color = "rgb(200,0,0)";
    }
    
    if(jsonText){
	if(jsonText!="{}"){
	    /* there is data */
	    var data = dojo.fromJson(jsonText);
	    var canvas = node;
	    var min = node.min;
	    var max = node.max;
	    var inZoom = node.inzoom;
	    
	    var drawer = this;
	    if (canvas.getContext) {
		/* get canvas & clear old if one */
		var baseWidth = 3;
		var ctx = canvas.getContext("2d");
		var cnvs_height = canvas.height;
		var cnvs_width = canvas.width;
		ctx.clearRect(0, 0, cnvs_width, cnvs_height);
		/* prepare drawing*/
                var d = max - min; // distance between min & max
		var Z = max * cnvs_height / d; // where is the zero line
		// draw zero line
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.rect(0, Z, cnvs_width, 1);
                ctx.closePath();
                ctx.fill();
		
		/* draw scores */
		ctx.fillStyle = color;
		ctx.beginPath();
		var p;
		ctx.fillStyle = 'green';
		for(var i in data){
		    if(p){
			var width = (i - p) * baseWidth;
			var real_score = data[p];
			var trans_score = - ( real_score * cnvs_height / d * inZoom );
			console.log(real_score);
			console.log(trans_score);
			console.log('z = ' + Z);
			console.log('');
			ctx.rect(p * baseWidth, Z , width, trans_score);
			//ctx.rect(p * baseWidth,drawer.getScoreForCanvas(min,max,data[p],cnvs_height,inZoom),width,cnvs_height);
		    }
		    p=i;
		}
		ctx.closePath();
                ctx.fill();
		ctx.beginPath();
		ctx.fillStyle = color;
		var width = (100-p)*baseWidth;
		var real_score = data[p];
		var trans_score = - ( real_score * cnvs_height / d * inZoom );
		ctx.rect(p * baseWidth, Z , width, trans_score);
		ctx.closePath();
		ctx.fill();
	    }
	}
    }
};
    
/**
 * convenient method wich convert the real score for a position
 * to the score which has to be displayed
 */
ImageDrawer.prototype.getScoreForCanvas = function (min,max,score, canvasHeight,inZoom){
    var coef = max - min;
    var sc = (score*canvasHeight*inZoom)/coef;
    var result = canvasHeight - sc;
    if(result<0){
	result=0;
    } 
    return result;
};
/**
 * return the score if it's already loaded
 * else return false
 */
ImageDrawer.prototype.getScore = function(db,img){
    var sc = dojo.byId('sq_' + db + '_' + img);
    if(sc){
	return sc.innerHTML;
    }
    return false;
}
       
/**
 * will send a request to gdv to fetch
 * the score for each image
 * @param images the image list
 */
ImageDrawer.prototype.getAllScores = function(images){
    var scores = dojo.byId("sqlite_scores");
    var drawer = this;
    if(images.length>0){
	var db = images[0].db;
	var imgs = GDV_POST_FETCHER.getTrack(db);
	//if an image is not in the fetched one, add it to the list
	dojo.forEach(images,function(item,i,arr){
		if(!(drawer.getScore(item.db,item.nb))){
		    if(!(imgs.join().indexOf(item.nb)>-1)){
			imgs.push(item);
		    }
		} else {
		    drawer.drawScores(item,drawer.getScore(db,item.nb),item.color);
		}
	    });
	GDV_POST_FETCHER.addTrack(db,imgs);
    }
}
   
/**
 * write scores in the DOM
 *
 */
ImageDrawer.prototype.putScore = function(images,data){
    var f = dojo.byId("sqlite_scores");
    
    for(db in data){
	
	var img_data = data[db];
	
	for(img in img_data){
	    scores = img_data[img];
	    /* look if the score is written or not */
	    id = 'sq_' + db + '_' + img;
	    if (!(dojo.byId(id))){
		var span = document.createElement("span");
		span.innerHTML = dojo.toJson(scores);
		span.id = id;
		f.appendChild(span);
	    }
	}
    }

    for(i=0;i<images.length;i++){
	var img = images[i];
	this.drawScores(img,this.getScore(img.db,img.nb),img.color);
    }
}






/**
 * draw the scale next to each quantitative tracks
 */
function drawScale(canvas){
    if (canvas.getContext) {
        var ctx = canvas.getContext("2d");
        ctx.clearRect(0,0,canvas.width,canvas.height);
	//draw white rect
	ctx.fillStyle = "rgba(255,255,255,0.7)";
	ctx.fillRect(0,0,55,canvas.height);
	//draw scale
        ctx.fillStyle = "rgb(0,0,0)";
	ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(10,0);
	ctx.lineTo(10,canvas.height);
	//grads
	var c = canvas.height/4;
	ctx.lineWidth = 1;
	ctx.moveTo(5,c);
	ctx.lineTo(15,c);
	
	ctx.moveTo(5,3*c);
	ctx.lineTo(15,3*c);
	ctx.lineWidth = 2;
	ctx.moveTo(5,2*c);
	ctx.lineTo(15,2*c);
	
        ctx.stroke();
        ctx.font = '20px monospace bold';
	ctx.fillText(parseInt(canvas.max), 12, 20);
	ctx.fillText(parseInt(canvas.min), 12, canvas.height-1);
	ctx.closePath();
    } 
    canvas.style.zIndex ="50";
}