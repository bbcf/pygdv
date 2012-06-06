/**  DATATABLES */
jQuery.fn.dataTableExt.oSort['string-case-asc']  = function(x,y) {
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};
 
jQuery.fn.dataTableExt.oSort['string-case-desc'] = function(x,y) {
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};


$(document).ready(function() {
    $('.grid tr').click( function() {
        console.log('click');
	$(this).toggleClass('row_selected');
    } );
    $('.grid').dataTable( {
        "aaSorting": [ [0,'asc'], [1,'asc'] ],
	"bStateSave" : true,
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