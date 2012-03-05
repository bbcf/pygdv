function TrackWidget(){
    this.container = null;
};



/**
* Construct the track Widget
* @param{track} - the track
* @param{view} - the view
*/
TrackWidget.prototype.enable = function(track, view){
    // construct the label
    var trackDiv = this.label(track, view);
    
    // construct the principal ontainer for the rest of the widget
    var cont = this.principal(track, view, trackDiv);
    
    // construct the scale if the track is a signal
    this.scale(track, view, cont);

    // construct a mover for the track
    this.mover(track, view, cont, trackDiv);
    
    
    track.twidget = this;
    return trackDiv;
};



/**
* Construct the HTML track label and update the view
* @param{track} - the track
* @param{view} - the view
* @return - the HTML label DIV 
*/
TrackWidget.prototype.label = function(track, view){
    var trackDiv = dojo.create('div', {id : 'track_' + track.name,
				       className : 'track',
				      })
    
    var pos = view.getX();
    pos += 100;
    var labelDiv = dojo.create('div', {id : 'label_' + track.name,
				       style : {position : 'absolute',
						top : '0px',
						left : pos + 'px'
					       },
				       className : 'track-label dojoDndHandle'
				      }, trackDiv)
   
    trackDiv.track = track;
    view.trackLabels.push(labelDiv);
    var heightUpdate = function(height) {view.trackHeightUpdate(track.name, height);};
    track.setViewInfo(heightUpdate, view.stripeCount, trackDiv, labelDiv,  view.stripePercent, view.stripeWidth, view.pxPerBp);
    
    this.container = trackDiv;
    return trackDiv;
    
};


/*
* The HTML general container for track widget
*/
TrackWidget.prototype.principal = function(track, view, trackContainer){
    var pos = view.getX();
    var container = dojo.create('div',{style : { position : 'absolute',
						 top : '0px',
						 width : '200px',
						 height : '100px',
						 left : pos + 'px'
					       },
				       zIndex : 200,
				       className : 'trackwidget'
				      }, trackContainer);
    view.trackScales.push(container);
    return container;

};

var boundaries = function(){
    var b={};
    b['l'] = 0;
    b['t'] = 0;
    b['w'] = 0;
    b['h'] = 1000;
    return b;
};

/**
* Construct a mover for the track
* @param{track} - the track
* @param{view} - the view
* @param{container} - the widget container
* @param{trackDiv} - the track container
*/
TrackWidget.prototype.mover = function(track, view, container, trackDiv){
    var pos = view.getX() ;
    var mover = dojo.create('div', {id : 'track_mover_' + track.name,
				    style : { position : 'absolute',
				     	      top : '36px',
				    	      width : '20px',
				     	      height : '50px'
				     	    },
				    className : 'trackmover'}, container);
    var dnd;
    var c = dojo.connect(mover, 'mousedown', function(e){
	var dnd = new dojo.dnd.move.constrainedMoveable(trackDiv, {constraints : boundaries});
	dojo.connect(dnd, 'onMoveStop', function(e){
	    dnd.destroy();
	});
    });
    
};

/**
* Construct container for scale if it's an ImageTrack
* @param{track} - the track
* @param{view} - the view
* @param{trackDiv} - the track container
*/
TrackWidget.prototype.scale = function(track, view, trackContainer){
    if (!(track instanceof ImageTrack)){return;};
    
    var pos = view.getX() ;
    
    // the scale container
    var container = dojo.create('div',{
	style : { position : 'absolute',
	 	  width : '200px',
	 	  height : '100px',
	 	} 
    }, trackContainer);
    // the scale
    var scale = dojo.create('canvas', {className : 'track_scale',
				       style : 
				       { position : 'absolute',
					 top : '0px',
				       width : '15px',
				       height : '100px'
				      },
				       id : 'scale_' + track.name
				      }, container);
    
    
    // the inputs (max and min)
    var in_max = dojo.create('input', {className : 'score_input',
				       type : 'text',
				       name : 'max_score',
				       id : track.name + '_max_input'
				      }, container);
    var in_min = dojo.create('input', {className : 'score_input',
				       style : {position : 'absolute',
					   bottom : '0px'},
				       type : 'text',
				       name : 'min_score',
				       id : track.name + '_min_input'
				      }, container);
    // updates
    track.scale = scale;
    container.max = in_max;
    container.min = in_min;
    track.scale_container = container;
 
    
    return container;
};





