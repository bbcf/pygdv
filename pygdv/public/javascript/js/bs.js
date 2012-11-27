(function($){
    var plugin = this;
    var bs_namespace = 'bioscript';
    /* default settings */
    var settings = {
        operation_list : {},
        root_name : 'BioScript operations',
        bs_server_url : 'http://localhost:8081/',
        form_selector : 'div.bs_form',
        show_plugin : function(plugin_id){
            alert('Click on plugin ' + plugin_id + ' .');
        },
        validation_successful : function(plugin_id, task_id){
            alert('Validation passed on plugin ' + plugin_id + '. Task launched with id ' + task_id + '.');
        }
    };
    /* inside call */
    var _incall = function(that, method, args){
        if (!(args instanceof Array)){
            args = [args];
        }
        return methods[method].apply(that, args);
    };
    /* plugin methods */
    var methods = {
        init : function(options){
            return this.each(function(){
                $.extend(settings, options);
                var $this = $(this),
                    data = $this.data(bs_namespace);

                if(!data){
                    $(this).data(bs_namespace,{
                        target : $this,
                        oplist : settings.operation_list.plugins,
                        rname : settings.root_name,
                        plugin : settings.show_plugin,
                        bsurl : settings.bs_server_url,
                        fselector : settings.form_selector,
                        vsuccess : settings.validation_successful
                    });
                    data = $this.data(bs_namespace);
                }
            });
        },
        /**
         * List Operations available in BioScript
         */
        operation_list : function(){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            // create root element
            var el = _incall($(this), '_create_menu_element', data.rname);
            // recursively add children
            var children = data.oplist.childs;
            if(children){
                var ul = $('<ul/>');
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [ul, child]);
                });
                el.append(ul);
            }
            // append all to the target
            data.target.append($('<div/>', {id : 'bs_operations_container'}).append($('<ul/>', {id : 'bs_menubar'}).append(el)));
        },

        _create_menu_element : function(name){
            return $('<li>').append('<a href="#">' + name +'</a>');
        },

        _add_childs : function(parent, child){
            var $this = $(this);
            var el = _incall($this, '_create_menu_element', child.key);
            var children = child.childs;
            if (children){
                var ul = $('<ul/>');
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [ul, child]);
                });
                el.append(ul);
            } else {
                el.id = child.id;
                _incall($this, '_bind_child', el);
            }
            parent.append(el);
        },

        _bind_child : function(el){
            var data = $(this).data(bs_namespace);
            $(el).click(function(){
                data.plugin(el.id);
            });
        },

        /**
         * hack the submit button of the BioScript
         * form to perform a JSONP query instead
         */
        hack_submit : function(){
            var data = $(this).data(bs_namespace);
            var bs_url = data.bsurl;
            var fselector = data.fselector;
            $(fselector).children('form').submit(function(e){
                e.preventDefault();

                /* fetch form id from form */
                //var fid = jQuery.parseJSON($(fselector).find('input#pp').val())['id'];

            //    $(':file').change(function(){
            //        var file = this.files[0];
            //        name = file.name;
            //        size = file.size;
            //        type = file.type;
            //        //your validation
            //    });

                /* get data from form */
                var pdata = $(this).serialize() + '&callback=bs_jsonp_cb';
                /* build form data objet to upload files if any */
                var formData = new FormData();
                var files = $(':file');
                for(var i = 0; i < files.length; i++) {
                    var fid = files[i].id;
                    var fs = files[i].files;
                    for(var j=0;j<fs.length;j++){
                        var f = fs[j];
                        if(f){
                            formData.append(fid, f);
                        }
                    }
                }
                console.log(bs_url + '/plugins/validate?' + pdata);
                /* submit query */
                $.ajax({
                        url: bs_url + '/plugins/validate?' + pdata,
                        type : 'POST',
                        datatype:'jsonp',
                        data : formData,
                        processData:false,
                        contentType:false,
                        crossDomain:true
                        });
                        return false;
                    });
        },

        /**
         * After form submit, a json is sent back from
         * BioScript server
         */
        jsonp_callback : function(jsonp){
            console.log('cbbbbb');
            var $this = $(this);
            if (jsonp){
                var val = jsonp.validation;
                if (val == 'failed'){
                    // validation failed : display the form with errors
                   var data = $(this).data(bs_namespace);
                    var fselector = data.fselector;
                    $(fselector).children('form').replaceWith(jsonp.widget);
                    _incall($this, 'hack_submit');
                } else if(val == 'success'){
                    // validation passed
                    if(jsonp.error){
                        // but there is an error
                        alert(jsonp.error);
                    } else {
                        var data = $(this).data(bs_namespace);
                        data.vsuccess(jsonp.form_id, jsonp.task_id);
                    }

                } else {
                    console.error("Callback with wrong data");
                    console.error(data);
                }
            } else {
                console.error("Callback with no data.");
            }
        }




    };

    $.fn[bs_namespace] = function(method){
        if(methods[method]){
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method){
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method "' + method + '" does not exist on jQuery.' + bs_namespace + '.');
        }
    };
})(jQuery);


function bs_jsonp_cb(data){
    console.log("bs_json_cb");
    $('body').bioscript({'jsonp_data': data}).bioscript('jsonp_callback', data);
}


function progress_handler(e){
    console.log(e);
}