function inetbar_toggle() {
    alert('inetbar toggle');
}

function inetbar_init() {
    $('#inetbar .logo img').click(function() {
        inetbar_toggle();
    });
}

function searchbar_init() {
    var obj = $('#searchbar input[name="q"]');
    obj[0].value = "< zoekwoord + enter >"
    obj.focus(function() {
        this.value = '';
    });
    obj.blur(function() {
        if (this.value == '') {
            this.value = "< zoekwoord + enter >";
        }
    });
}

$(document).ready(function() {
    inetbar_init();
    searchbar_init();
});

