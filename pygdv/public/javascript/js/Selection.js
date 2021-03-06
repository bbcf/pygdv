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
* *selections* is an array of Marquee objects.
*/
SelectionPane.prototype.draw = function(store, selections){
    var selections_table = dojo.create("table", {id:"selections_table"}, store);
    var marquees_len = selections.length;
    for (var i=0; i<marquees_len; i++){
        var marquee = selections[i]; // Marquee instance
        var selection_tr = dojo.create("tr", null, selections_table);
        var selection_subtable = dojo.create("table", {className:"selection_subtable"}, selection_tr);

        var pos_tr = dojo.create("tr", null, selection_subtable);
        var pos = dojo.create("td", {className:"position", innerHTML: marquee.chr+":"+marquee.start+"-"+marquee.end }, pos_tr);
        var del = dojo.create("td", {className:"delete"}, pos_tr);
        var desc_tr = dojo.create("tr", null, selection_subtable);
        var desc_td = dojo.create("td", {className:"description", colspan:2}, desc_tr);
        dojo.create("div", {className:"delete_img_field"}, del);
        dojo.create("div", {innerHTML:marquee.desc, className:"description_field",
                           style: {color: "grey"}}, desc_td);

        this.connect_location(pos, marquee);
        this.connect_description(desc_td, marquee);
        this.connect_delete(del, marquee, this.handler);
    }
};


/**
* If a location *domNode* is double-clicked, the view shows the associated
* portion of the genome.
*/
SelectionPane.prototype.connect_location = function(domNode, marquee){
    if(marquee){
        dojo.connect(domNode, "dblclick", function(e){
            _gdv_info.gb.navigateTo(marquee.navigateTo());
            dojo.stopEvent(e);
        });
    }
};

/*
* On loading of selections, connects each of their description field with
* an onclick description edition functionality.
*/
SelectionPane.prototype.connect_description = function(desc_field, marquee){
    var ctx = this;
    var handle = dojo.connect(desc_field, 'click', function(e){
        var textfield = dojo.query(".description_field", desc_field)[0];
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

        // Executed on blur or Enter key press
        updateDescription = function(ee){
            var key = ee.keyCode || ee.which;
            if (key==13 || key==undefined){
                marquee.desc = input.value;
                dojo.create("td", {innerHTML: marquee.desc, className:"description_field"}, input, "replace");
                ctx.connect_description(desc_field, marquee);
                ctx.handler.update_on_server();
                dojo.stopEvent(ee);
            }
        }
        dojo.connect(input, 'blur', updateDescription);
        dojo.connect(input, 'keydown', updateDescription);
        dojo.stopEvent(e);
        dojo.disconnect(handle);
    });
};

/*
* If the 'delete' closs is clicked, delete the marquee and update on server.
*/
SelectionPane.prototype.connect_delete = function(domNode, marquee, handler){
    var ctx = this;
    dojo.connect(domNode, "click", function(e){
        if (confirm('Are you sure ?')){
            handler.delete(marquee);
        }
        dojo.stopEvent(e);
    });

};







