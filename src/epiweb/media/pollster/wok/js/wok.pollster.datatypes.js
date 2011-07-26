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
                    })
                    .change(function(evt){
                        var $this = $(this);
                        var date = Date.parse($this.val());
                        if (date)
                            $this.val(date.toString('dd/MM/yyyy'));
                        else
                            $this.val('');
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

    function MonthYearType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            bind: function($question) {
                $question
                    .find(':text,:date')
                    .datepicker({
                        constrainInput: true,
                        dateFormat: 'mm/yy',
                        changeMonth: true,
                        changeYear: true ,
                        yearRange: '-110:+0',
                        beforeShow: function(input, inst) {
                            inst.dpDiv.addClass('month-year-only');
                            $('head').append('<style id="hide-month-year-only-calendar" type="text/css">.month-year-only .ui-datepicker-calendar { display: none; }</style>');
                            var val = $(input).val();
                            var month = parseInt(val.replace(/\/.*$/, ''));
                            var year = parseInt(val.replace(/^.*\//, ''));
                            if (year && month) {
                                setTimeout(function(){
                                    $(input).datepicker('setDate', new Date(year, month-1, 1));
                                }, 0);
                            }

                        },
                        onChangeMonthYear: function(year, month, inst) {
                            var val = month+'/'+year;
                            if (month < 10)
                                val = '0'+val;
                            $(inst.input).val(val).change();
                        },
                        onClose: function(dateText, inst) { 
                            inst.dpDiv.removeClass('month-year-only');
                            $('head #hide-month-year-only-calendar').remove();
                        }
                    })
                    .change(function(evt){
                        var $this = $(this);
                        var value = $this.val();
                        if (!value.match(/\//)) {
                            $this.val('');
                        }
                        else {
                            var date = Date.parse("01/"+value);
                            if (date)
                                $this.val(date.toString('MM/yyyy'));
                            else
                                $this.val('');
                        }
                    });
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.datatypes = {
        "Text": TextType,
        "Numeric": NumericType,
        "Date": DateType,
        "MonthYear": MonthYearType
    };

})(jQuery);
