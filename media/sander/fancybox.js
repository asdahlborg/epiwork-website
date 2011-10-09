$(document).ready(function() {

    /* This is basic - uses default settings */
    
    $("a#single_image").fancybox();
    
    /* Using custom settings */
    
    $("a#inline").fancybox({
        'hideOnContentClick': true
    });

    /* Apply fancybox to multiple items */
    
    $("a.group").fancybox({
        'transitionIn'  :   'elastic',
        'transitionOut' :   'elastic',
        'speedIn'       :   600, 
        'speedOut'      :   200, 
        'overlayShow'   :   false,
        'titleShow'     :   false,
        'height'        :   450,
        'width'         :   750,
        'scrolling'     :   true,
        'autoScale'     :   false,
        'autoDimensions':   false,
        'cyclic'        :   true
    });
    
});
