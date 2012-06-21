/**  DATATABLES */
jQuery.fn.dataTableExt.oSort['string-case-asc']  = function(x,y) {
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};
 
jQuery.fn.dataTableExt.oSort['string-case-desc'] = function(x,y) {
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};Window


$(document).ready(function() {
    $('.grid tbody tr').hover( function() {
     	$(this).find('.hidden_info').find('.tr_actions').toggleClass('table_hidden');
	//toggleClass('row_hover');
	//show_actions($(this));
    });
    $('.grid').dataTable( {
	"bStateSave" : true,
	"aaSorting": [ [0,'asc'], [1,'asc'] ],
	"bPaginate" : false,
    });
    
});

/** TOOLTIPS */
$(document).ready(function() {
    $('.tooltip_hider').hover(
	function(){
	    $('.tooltip_pane').slideDown('normal');
	},
	function(){
	    $('.tooltip_pane').slideUp('fast');
	}
    );});



/** Style */
$(document).ready(function() {
    // move some div
    $('#controls').first().append($('.dataTables_filter'));
    $('#footer').first().append($('.dataTables_info'));
    $('#footer').first().append($('.dataTables_length'));
    $('#footer').first().append($('.dataTables_paginate'));
    $('#footer').first().append($('.dataTables_length'));
    // resize the content (+ on resize)
    good_content_size();
    $(window).resize(function(){
	good_content_size();
    });
    // set status class on tracks
    $('.grid tbody tr').each(function(ind, dome){
	var status = $(dome).find('.tr_status').html();
	if (status){
	    status = status.toLowerCase();
	    if(status == 'failure'){
		$(dome).removeClass();
	    }
	    $(dome).addClass('track-' + status);
	}
    });
    // set color on parameters
    $('.grid tbody tr').each(function(ind, dome){
	var color = $(dome).find('.tr_color').html();
	if ((color) && !(color == 'None')){
	    color = color.toLowerCase();
	    $(dome).css('color', color);
	} else {
	    $(dome).css('color', 'blue');
	}
    });
    // dynamic "add user" link
    $('#add_user_c').click(function(){
	$('.add_user_c').toggle('normal')});
});

function good_content_size(){
    /** make the content of a good size */
    var new_width = $(window).width() - $('#navigation').width();
    var max = Math.max(new_width, '800') - 15;
    $('#content').width(max);
    $('.grid').width(max);
    /* calculate sizes for table columns */
    var ths = $('.grid').find('th');
    var nb = ths.length;
    var  w = max / nb - 5;
    $(ths).width(w);
};

function show_actions(node){
    /** show the actions when user hover on content */
    var c = node.attr('class');
    if (c.indexOf('row_hover') > 0){
	// create a span with actions htnl inside
	var actions = node.find('.table_hidden').find('.tr_actions').first();
	var s = $('<span class=tr_action_hover>').html(actions.html());
	// position it
	var l = node.find('td');
	var posleft = (l.eq(1).offset().left - l.eq(0).offset().left);
	s.css('left', posleft + "px");
	var postop = l.eq(0).offset().top + 6;
	s.css('top', postop + "px");
	node.append(s);
    } else {
	node.find('.tr_action_hover').remove();
    }
};



