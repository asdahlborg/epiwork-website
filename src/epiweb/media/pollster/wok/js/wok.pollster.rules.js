(function($) {
    // COMMON UTILITIES

    // BUILTIN RULES

    function ShowQuestionRule(subjectOption, objectQuestion, objectOption) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+objectQuestion);
                if ($t.length === 1 && $t.is(":hidden") && checked)
                    $t.slideDown();
                if ($t.length === 1 && $t.is(":visible") && !checked)
                    $t.slideUp();
            }
        });
    }

    function HideQuestionRule(subjectOption, objectQuestion, objectOption) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+objectQuestion);
                if ($t.length === 1 && $t.is(":visible") && checked)
                    $t.slideUp();
                if ($t.length === 1 && $t.is(":hidden") && !checked)
                    $t.slideDown();
            }
        });
    }

    function ShowOptionRule(subjectOption, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.slideDown();
                else
                    $t.slideUp();
            }
        });
    }

    function HideOptionRule(subjectOption, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,
            
            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.slideUp();
                else
                    $t.slideDown();
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.rules = {
        "ShowQuestion": ShowQuestionRule,
        "HideQuestion": HideQuestionRule,
        "ShowOption": ShowOptionRule,
        "HideOption": HideOptionRule
    };

})(jQuery);
