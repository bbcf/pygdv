/**
LAYOUT
*/

$(document).ready(function() {



    var outlayout = $('body').layout({
	    north__size:120,
	    west__size: 180,
	    spacing_open : 0 ,
	    west__spacing_open : 1 ,
	    south__size: 35
    });

    var ls = $('#left_stack');
    if (ls.length > 0){
        ls.layout({
            spacing_open : 0,
            south_size : 35
        });
    }


});
