$.get("/count/list", function(data) { $('#inetbarcontent').html(data); } );

$(document).ready(function() {
	$('#inetbarclick').click( function() {
		if ($('#inetbarcontent').css('display') == 'none') {
			$('#inetbarcontent').slideDown();
		}
		else {
			$('#inetbarcontent').slideUp();
		}
	});
});
