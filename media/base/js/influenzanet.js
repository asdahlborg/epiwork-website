/*
Template Name: Epiwork Main
Description: Javascript for deployment on the Epiwork platform 
Author: Antwan Wiersma (http://www.prime-creation.nl/)
Version: 1.0
*/

/* Google Analytics */

var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-24124829-1']);
_gaq.push(['_trackPageview']);

(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

/* Influenzanet Map Bar */

var add_link = function() {
	$(this).next('div.toggle').attr('name', name);
	$(this).html('<a href="#toggle" title="Show/hide extra information">' +
	$(this).html() + '</a>');
};

var toggle = function() {
	$(this).
		toggleClass('expanded').
		nextAll('div.toggle').slideToggle('slow');
};

var remove_focus = function() {
	$(this).blur();
};

$(document).ready (function () {
	$('._toggle').
		removeClass('_toggle').
		addClass('toggle');	
	$('._expanded').
		removeClass('_expanded').
		addClass('expanded');
	$('._show').
		removeClass('_show').
		addClass('show');
	$('.jsclose').
		removeClass('jsclose').
		addClass('close');
	$('p.toggle:not(.expanded)').nextAll('div.toggle').hide();
	$('p.toggle').each(add_link);
	$('p.toggle').click(toggle);
	$('p.toggle a').mouseup(remove_focus);
});

$(function() {
	$('a.close').click(function(){
		$('div.toggle').slideToggle('slow');
		$('.expanded').
			removeClass('expanded').
			addClass('toggle');	
		return false;
	});
});

/* Open rel="external" links in a new window */

function externalLinks() {
 if (!document.getElementsByTagName) return;
 var anchors = document.getElementsByTagName("a");
 for (var i=0; i<anchors.length; i++) {
   var anchor = anchors[i];
   if (anchor.getAttribute("href") &&
       anchor.getAttribute("rel") == "external")
     anchor.target = "_blank";
 }
}
window.onload = externalLinks;

