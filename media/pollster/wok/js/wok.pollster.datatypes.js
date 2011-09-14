(function($) {
    // COMMON UTILITIES

    // BUILTIN DATA TYPES

    function DateType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            check: function($field) {
                return true;
            },
            bind: function($field) {
                $field
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
            check: function($field) {
                if (this._regex)
                    return this._regex.test($field.val());
                else
                    return true;
            },
            bind: function($field) {
                var pattern = $field.closest(".question").data("regex");
                if (pattern)
                    this._regex = new RegExp(pattern);
                else
                    this._regex = null;
            }
        });
    }

    function NumericType() {
        var self = this;
        this._regex = /[0-9]/;

        // Public methods.

        $.extend(this, {
            check: function($field) {
                var value = $field.val();
                if (value && self._regex)
                    return self._regex.test(value);
                else
                    return true;
            },
            bind: function($field) {
            }
        });
    }

    function PostalCodeType() {
        var self = this;
        if (window.pollster_get_postal_code_format)
            this._regex = new RegExp('^'+pollster_get_postal_code_format()+'$');
        else
            this._regex = null;

        // Public methods.

        $.extend(this, {
            check: function($field) {
                var value = $field.val();
                if (value && this._regex)
                    return this._regex.test(value);
                else
                    return true;
            },
            bind: function($field) {
            }
        });
    }

    function YearMonthType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            check: function($field) {
                var val = $field.val();
                var month = parseInt(val.replace(/\/.*$/, ''), 10);
                var year = parseInt(val.replace(/^.*\//, ''), 10);
                return year && month;
            },
            bind: function($field) {
                $field
                    .datepicker({
                        constrainInput: true,
                        dateFormat: 'mm/yy',
                        changeMonth: true,
                        changeYear: true ,
                        yearRange: '-110:+0',
                        beforeShow: function(input, inst) {
                            inst.dpDiv.addClass('year-month-only');
                            $('head').append('<style id="hide-year-month-only-calendar" type="text/css">.year-month-only .ui-datepicker-calendar { display: none; }</style>');
                            var val = $(input).val();
                            var month = parseInt(val.replace(/\/.*$/, ''), 10);
                            var year = parseInt(val.replace(/^.*\//, ''), 10);
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
                            inst.dpDiv.removeClass('year-month-only');
                            setTimeout(function(){
                                $('head #hide-year-month-only-calendar').remove();
                            }, 0);
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

    // used internally for builtin questions
    function TimestampType() {
        var self = this;

        // Public methods.

        $.extend(this, {
            check: function($field) {
                return true;
            },
            bind: function($field) {
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.datatypes = {
        "Text": TextType,
        "Numeric": NumericType,
        "PostalCode": PostalCodeType,
        "Date": DateType,
        "YearMonth": YearMonthType,
        "Timestamp": TimestampType
    };

})(jQuery);
