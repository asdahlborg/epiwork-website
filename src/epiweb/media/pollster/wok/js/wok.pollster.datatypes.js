(function($) {
    // COMMON UTILITIES

    // BUILTIN DATA TYPES

    function DateType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            bind: function($question) {
                $question
                    .find(':text,:date')
                    .datepicker({
                        constrainInput: true,
                        dateFormat: 'dd/mm/yy',
                        changeMonth: true,
                        changeYear: true 
                    });
            }
        });
    }

    function TextType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            bind: function($question) {
            }
        });
    }

    function NumericType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            bind: function($question) {
                $question
                    .find(':text,:number')
                    .keypress(function(evt) {
                        var key = String.fromCharCode(evt.which);
                        var regex = /[0-9]/;
                        return regex.test(key);
                    });
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.datatypes = {
        "Text": TextType,
        "Numeric": NumericType,
        "Date": DateType
    };

})(jQuery);
