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
    var selections_table = dojo.create("table", {id:"selections_table"}, store);
    var locs_len = selections.length;
    for (var i=0; i<locs_len; i++){
        var loc = selections[i];
        var selection_tr = dojo.create("tr", null, selections_table);
        var selection_subtable = dojo.create("table", {class:"selection_subtable"}, selection_tr);

        var postr = dojo.create("tr", null, selection_subtable);
        var pos = dojo.create("td", {class:"position", innerHTML: loc.chr+":"+loc.start+"-"+loc.end }, postr);
        var del = dojo.create("td", {class:"delete"}, postr);
        var desctr = dojo.create("tr", null, selection_subtable);
        var desc = dojo.create("td", {class:"description", colspan:2}, desctr);
        dojo.create("div", {innerHTML:"&nbsp", class:"delete_img_field"}, del);
        dojo.create("div", {innerHTML:"Enter description", class:"description_field",
                           style: {color: "grey"}}, desc);

        this.connect_location(pos, loc);
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
            _gdv_info.gb.navigateTo(location.navigateTo());
            dojo.stopEvent(e);
        });
    }
};

SelectionPane.prototype.connect_description = function(description, location){
    if(description){
    var ctx = this;
    var handle = dojo.connect(description, 'click', function(e){
            var textfield = dojo.query(".description_field", description)[0];
            var textfield_content = textfield.innerHTML;
            var textfield_width = textfield.parentNode.offsetWidth;
            var textfield_height = textfield.parentNode.offsetHeight;
            var input = dojo.create("input",
                            { type:"text",
                              value:textfield_content,
                              style: {width: (textfield_width-6)+"px",
                                      height: (textfield_height-6)+"px"},
                            }, textfield, "replace");
            input.focus();
            input.select();

            updateDescription = function(ee){
                var key=ee.keyCode || ee.which;
                if (key==13 || key==undefined){
                    location.desc = input.value;
                    dojo.create("td", {innerHTML: location.desc, class:"description_field"}, input, "replace");
                    ctx.connect_description(description, location);
                    ctx.handler.update_on_server();
                    dojo.stopEvent(ee);
                }
            }
            dojo.connect(input, 'blur', updateDescription);
            dojo.connect(input, 'keydown', updateDescription);
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







