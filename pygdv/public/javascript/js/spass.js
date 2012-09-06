(function($){
    var plugin = this;

    /* default settings */
    var settings = {
        'sselect' : '#sselect', // secondary select field
        'mapping' : {}          // mapping from parent select field to sselect
    };
    /* inside call */
    var _incall = function(that, method){
        methods[method].apply(that,  Array.prototype.slice.call(arguments, 1));
    };
    /* plugin methods */
    var methods = {
        init : function(options){
            return this.each(function(){
                $.extend(settings, options);
                var $this = $(this),
                    data = $this.data('dynselect');
                if(!data){
                    $(this).data('dynselect',{
                        target : $this,
                        starget : $(settings.sselect)
                    });
                    data = $this.data('dynselect');
                }
            _incall($this, 'bind_event');
            });
        },

        /* bind the on change function */
        bind_event : function(){
            return this.each(function(){
                var data = $(this).data('dynselect');
                var target = data.target;
                var starget = data.starget;
                target.change(function(){
                    // get mapping
                    var mapped = settings.mapping[target.val()];
                    starget.children('option').remove();
                    if(mapped){
                        // set new mapping
                        $.each(mapped, function(i, v){
                             starget.append('<option value="' + v[0] + '">' + v[1] + '</option>');
                            })
                    }
                });
                target.trigger('change');
            });

            }
        };

    $.fn.dynselect = function(method){
        if(methods[method]){
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method){
            return methods.init.apply(this, arguments)
        } else {
            $.error('Method ' + method + 'does not exist on jQuery.tooltip');
        }
    }
})(jQuery);





window.onload = function() {
    $('#species').dynselect({
        'sselect' : '#assembly',
        'mapping' : $.parseJSON($('#smapping').val())});
};
