/**
* Handle the selections drawing on the container
*/

function SelectionPane(container, handler){
    this.handler = handler;
    this.store = container;
};




/**
* The selections have changed. Update them.
*/
SelectionPane.prototype.update = function(selections){
    var store = this.store;
    dojo.empty(store);
    this.draw(store, selections);
    this.handler.update_on_server();
};




/**
* Draw the selections on the given store.
*/
SelectionPane.prototype.draw = function(store, selections){
    var dtable = dojo.create("table", null, store);
    var locs_len = selections.length;
    dojo.create("tr", null, dtable);
    dojo.create("td", {innerHTML : "Chr\tstart\tend"}, dtable.firstChild);
    dojo.create("td", {innerHTML : "Description"}, dtable.firstChild);
    dojo.create("td", null, dtable.firstChild);
    for (var i=0; i<locs_len; i++){
        var ttr = dojo.create("tr", null, dtable);
        var loc = selections[i];
        var ttd = dojo.create("td", {innerHTML: loc.chr + "\t(" + loc.start + "," + loc.end + ")" }, ttr);
        var desc = dojo.create("td", {class:"description"}, ttr);
        var del = dojo.create("td", null, ttr);
        dojo.create("a",{innerHTML:"Delete", class:"delete_field",
                         style:{textDecoration:"underline", color:"blue"}}, del);
	dojo.create("div",{innerHTML : loc.desc, class:"description_field",
                           style: {color: "grey"}}, desc);
        
	this.connect_location(ttd, loc);
	this.connect_description(desc, loc);
	this.connect_delete(del, loc, this.handler);
    }
};







/**
* Connect the DOM to events 
*/
SelectionPane.prototype.connect_location = function(domNode, location){
    if(location){
	dojo.connect(domNode, "dblclick", function(e){
            //dojo.byId("genomeBrowser").genomeBrowser.navigateTo();
	    console.log(location);
	    dojo.stopEvent(e);
        });
    }
};

SelectionPane.prototype.connect_description = function(description, location){
    if(description){
	var ctx = this; 
	var handle = dojo.connect(description, 'click', function(e){
            var textfield = dojo.query(".description_field", description)[0];
            var txt = textfield.innerHTML;
            var input = dojo.create("input", {type:"text", value:txt}, textfield, "replace");
            input.focus(); 
	    input.select();
            dojo.connect(input, 'blur', function(ee){
		location.desc = input.value;
		dojo.create("td", {innerHTML: location.desc, class:"description_field"}, input, "replace");
                ctx.connect_description(description, location);
		ctx.handler.update_on_server();
                dojo.stopEvent(ee);
            });
            dojo.stopEvent(e);
            dojo.disconnect(handle);
        });
    }
};

SelectionPane.prototype.connect_delete = function(domNode, location, handler){
    var ctx = this;
    dojo.connect(domNode, "click", function(e){
        handler.delete(location);
	dojo.stopEvent(e);
    });
    
};







