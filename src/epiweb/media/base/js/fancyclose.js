/*
Template Name: Influenzanet
Description: Javascript for closing Login Fancybox on changing window.location 
Author: Antwan Wiersma (http://www.prime-creation.nl/)
Version: 1.0
*/

/* Close Fancybox */

window.onbeforeunload = closeFancybox ;

function closeFancybox(){
  parent.$.fancybox.close();
}