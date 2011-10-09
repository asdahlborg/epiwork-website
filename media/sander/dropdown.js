$(document).ready(function () { 
    $('.nav li.dropdown').hover(
        function () {
            $('ul', this).stop(true, true).slideDown(300);
        }, 
        function () {
            $('ul', this).stop(true, true).slideUp(300);
        }
    );
    $('.nav li.option').hover(
        function () {
            $('ul', this).stop(true, true).slideDown(500);
            var submenu = $('ul', this).parent().next();
            submenu.css({
                'display': 'none',
            });
        }, 
        function () {
            $('ul', this).stop(true, true).slideUp(500);         
            var submenu = $('ul', this).parent().next();
            submenu.css({
                 'display': 'block'
            });
        }
    );
});
