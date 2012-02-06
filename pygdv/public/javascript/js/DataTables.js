jQuery.fn.dataTableExt.oSort['string-case-asc']  = function(x,y) {
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};
 
jQuery.fn.dataTableExt.oSort['string-case-desc'] = function(x,y) {
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};


$(document).ready(function() {
    // $('.grid tr').click( function() {
    //     if ( $(this).hasClass('row_selected') ){
    //         $(this).removeClass('row_selected');
    // 	} else {
    //         $(this).addClass('row_selected');
    // 	}
    // });
    
    $('.grid').dataTable( {
        "aaSorting": [ [0,'asc'], [1,'asc'] ],
	"bStateSave" : true,

	"fnCookieCallback" : function(sName, oData, sExpires, sPath){
	    console.log('cook');
	    console.log(sName);
	    console.log(oData);
	    console.log(sExpires);
	    console.log(sPath);
	},
	
	"fnDrawCallback" : function(sName, oData){
	    console.log('draw');
	    console.log(sName);
	},
	"fnServerParams" : function(sName, oData){
	    console.log('serv');
	    console.log(sName);
	    console.log(oData);
}


    });
});