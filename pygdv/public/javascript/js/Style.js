/**  DATATABLES */
jQuery.fn.dataTableExt.oSort['string-case-asc']  = function(x,y) {
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};
 
jQuery.fn.dataTableExt.oSort['string-case-desc'] = function(x,y) {
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};Window





/**
LAYOUT
*/

$(document).ready(function() {
    
    $('body').layout({
	north__size:120,
	west__size: 180,
	spacing_open : 0 ,
	west__spacing_open : 1 ,
	south__size: 35,
    });
});


$(document).ready(function() {
    $('.crud_table .grid tbody tr').hover( function() {
     	$(this).find('.hidden_info').find('.tr_actions').toggleClass('table_hidden');
	//toggleClass('row_hover');
	//show_actions($(this));
    });

    // $('.grid tbody tr').click( function() {
    // 	$('.grid tbody tr').find('.hidden_info').find('.tr_info').hide();
    // 	// $(this).find('.hidden_info').find('.tr_info').toggle('normal');
    // 	var info = $(this).find('.hidden_info').find('.tr_info');
    // 	if($(info).children().length > 0){
    // 	    var posnode = $(this).offset().left;
    // 	    var w = $(document).width() - posnode;
    // 	    var min = Math.min('500', w);
    // 	    $(info).css('width', min + "px");
    // 	    $(info).toggle('fast');
	    
    // 	}

    
 

    $('.crud_table .grid').dataTable( {
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
    //good_content_size();
    $(window).resize(function(){
	//good_content_size();
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
    // $('.grid tbody tr').each(function(ind, dome){
    // 	var color = $(dome).find('.tr_color').html();
    // 	if ((color) && !(color == 'None')){
    // 	    color = color.toLowerCase();
    // 	    $(dome).css('color', color);
    // 	} else {
    // 	    $(dome).css('color', 'blue');
    // 	}
    // });
    // dynamic forms
    $('#add_user_c').click(function(){
	$('.add_user_c').toggle('normal')});
    $('#add_circle_c').click(function(){
	$('.add_circle_c').toggle('normal')});
    $('#add_track_c').click(function(){
	$('.add_track_c').toggle('normal')});
});

function good_content_size(left){
    /** make the content of a good size */
    var new_width = $(window).width() - $('#left_stack').width();
    var max = Math.max(new_width, '800') ;
    $('#content').width(max);

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



