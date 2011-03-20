/*
Template Name: Epiwork Main
Description: Javascript for deployment on the Epiwork platform 
Author: Antwan Wiersma (http://www.prime-creation.nl/)
Version: 1.0
*/

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
