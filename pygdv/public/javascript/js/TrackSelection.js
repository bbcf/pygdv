/**
 * Returns a list of all tracks that have been selected
 * For instance you get: ["cytoBand", "gap", "gold"]
 */
function TrackSelection_get() {
    // Get a list of all track labels
    labels = dojo.query(".track-label");
    // New list contains only labels with a true selected proprety
    var list = new Array();
    for (label in labels) {
        if (labels[label].selected) {
            list.push(labels[label].innerHTML);
        }
    }
    return list;
};


/**
 * Return a JSON of all selected tracks ordered :
 * {1:{label:file},2:{label2:file2},....}
 */
function TrackSelection_getTracks(){
    // Get a list of all track labels
    labels = dojo.query(".track-label");
    // New list contains only labels with a true selected proprety
    var json = {};
    for (i in labels) {
        var label=labels[i];
        if (label.selected) {
            for(k in trackInfo){
                var track = trackInfo[k];
                if(track.label==label.innerHTML){
                    var tmp={};
                    tmp[track.label]=track.url.slice(3,track.url.length-14);
                    json[i]=tmp;
                }
            }
        }
    }
    return json;
};

/**
 * Flips the "selected" boolean on a track label
 * and changes the background color
 * @param {event} the dojo event
 */
function TrackSelection_flip(event) {
    // Get the div object
    labelDiv = event.target;
    // Change the background color
    if (labelDiv.selected) {labelDiv.className = "track-label dojoDndHandle unselected";}
    else                   {labelDiv.className = "track-label dojoDndHandle selected";}
    // Flip the selected booleen
    labelDiv.selected = (labelDiv.selected == false);

    //update gfm form if one
    var textarea = dijit.byId("gfm_tracks");
    if(textarea){
        textarea.setValue(TrackSelection_get().join(";"));
    }
}
