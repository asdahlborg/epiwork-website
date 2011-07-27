(function($) {
    // COMMON UTILITIES

    // BUILTIN RULES

    function ShowQuestionRule(subjectOptions, objectQuestion, objectOption) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+objectQuestion);
                if ($t.length === 1 && $t.is(":hidden") && checked) {
                    $t.slideDown(
                        function() { $(this).find(':input:visible').attr('disabled', false); }
                    );
                }
                if ($t.length === 1 && $t.is(":visible") && !checked) {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
            }
        });
    }

    function HideQuestionRule(subjectOptions, objectQuestion, objectOption) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+objectQuestion);
                if ($t.length === 1 && $t.is(":visible") && checked) {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
                if ($t.length === 1 && $t.is(":hidden") && !checked) {
                    $t.slideDown(
                        function() { $(this).find(':input:visible').attr('disabled', false); }
                    );
                }
            }
        });
    }

    function ShowOptionsRule(subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.slideDown().find(':input').attr('disabled', false);
                else
                    $t.slideUp().find(':input').attr('disabled', true);
            }
        });
    }

    function HideOptionsRule(subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.slideUp().find(':input').attr('disabled', true);
                else
                    $t.slideDown().find(':input').attr('disabled', false);
            }
        });
    }

    function CheckOptionsRule(subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', true).change();
            }
        });
    }

    function UncheckOptionsRule(subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: false,

            apply: function($survey, checked) {
                var selectors = objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', false).change();
            }
        });
    }

    function ExclusiveRule(subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subject: subjectOptions,
            isExclusive: true,

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
        "Exclusive": ExclusiveRule
    };

})(jQuery);
