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

    function ShowOptionsRule(subjectOption, objectQuestion, objectOptions) {
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

    function HideOptionsRule(subjectOption, objectQuestion, objectOptions) {
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

    function CheckOptionsRule(subjectOption, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', true).change();
            }
        });
    }

    function UncheckOptionsRule(subjectOption, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', false).change();
            }
        });
    }

    function ExclusiveRule(subjectOption, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            target: subjectOption,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                // TODO
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.rules = {
        "ShowQuestion": ShowQuestionRule,
        "HideQuestion": HideQuestionRule,
        "ShowOptions": ShowOptionsRule,
        "HideOptions": HideOptionsRule,
        "CheckOptions": CheckOptionsRule,
        "UncheckOptions": UncheckOptionsRule,
        "ExclusiveRule": ExclusiveRule
    };

})(jQuery);
