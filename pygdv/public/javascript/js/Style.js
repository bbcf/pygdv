/**  DATATABLES */
jQuery.fn.dataTableExt.oSort['string-case-asc']  = function(x,y) {
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};
 
jQuery.fn.dataTableExt.oSort['string-case-desc'] = function(x,y) {
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};Window


$(document).ready(function() {
    $('.grid tbody tr').click( function() {
     	$(this).toggleClass('row_selected');
    } );
    $('.grid tbody tr').hover( function() {
     	$(this).toggleClass('row_hover');
	show_actions($(this));
    });
    $('.grid').dataTable( {
	"bStateSave" : true,
	"aaSorting": [ [0,'asc'], [1,'asc'] ],
	
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
    
});

function good_content_size(){
    var new_width = $(window).width() - $('#navigation').width();
    var max = Math.max(new_width, '800');
    $('#content').width( max - 15 );
    $('.crud_table').width('100%');
};

function show_actions(node){
    var c = node.attr('class');
    if (c.indexOf('row_hover') > 0){
	// create a span with actions htnl inside
	var actions = node.find('.table_hidden').find('.tr_actions').first();
	var d = actions.attr('display');
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

