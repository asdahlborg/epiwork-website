(function($) {
    // COMMON UTILITIES

    // BUILTIN VIRTUAL OPTION TYPE

    function TextRangeType(option, inf, sup, regex) {
        var self = this;

        // Public methods.

        $.extend(this, {
            option: option,
            match: function(val) {
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= sup;
                else if (!sup)
                    return inf <= val;
                return inf <= val && val <= sup;
            }
        });
    }

    function NumericRangeType(option, inf, sup, regex) {
        var self = this;

        // Public methods.

        $.extend(this, {
            option: option,
            match: function(val) {
                val = parseFloat(val);
                inf = parseFloat(inf);
                sup = parseFloat(sup);
                if (isNaN(inf) && isNaN(sup))
                    return false;
                else if (isNaN(inf))
                    return val <= sup;
                else if (isNaN(sup))
                    return inf <= val;
                else
                    return inf <= val && val <= sup;
            }
        });
    }

    function DateRangeType(option, inf, sup, regex) {
        var self = this;

        // Public methods.

        $.extend(this, {
            option: option,
            match: function(val) {
                val = Date.parse(val);
                inf = Date.parse(inf);
                sup = Date.parse(sup);
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= sup;
                else if (!sup)
                    return inf <= val;
                else
                    return inf <= val && val <= sup;
            }
        });
    }

    function DateYearsAgoType(option, inf, sup, regex) {
        var self = this;

        // Public methods.

        $.extend(this, {
            option: option,
            match: function(val) {
                val = Date.parse(val);
                inf = parseInt(inf);
                sup = parseInt(sup);
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= new Date().addYears(-sup);
                else if (!sup)
                    return new Date().addYears(-inf) <= val;
                else
                    return new Date().addYears(-inf) <= val && val <= new Date().addYears(-sup);
            }
        });
    }

    function RegularExpressionType(option, inf, sup, regex) {
        var self = this;

        // Public methods.

        $.extend(this, {
            option: option,
            match: function(val) {
                return regex && new RegExp('^'+regex+'$').test(val);
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.virtualoptions = {
        "TextRange": TextRangeType,
        "NumericRange": NumericRangeType,
        "DateRange": DateRangeType,
        "RegularExpression": RegularExpressionType,
        "DateYearsAgo": DateYearsAgoType
    };

})(jQuery);
