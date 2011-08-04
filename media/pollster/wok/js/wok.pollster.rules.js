(function($) {
    // COMMON UTILITIES

    function get_question_data_names($survey, question, options) {
        var $question = $survey.find("#question-"+question);
        var names = [];
        if ($question.is('.question-text')) {
            names = [ $question.attr('data-shortname') ];
        }
        else if ($question.is('.question-single-choice')) {
            names = [ $question.attr('data-shortname') ];
        }
        else if ($question.is('.question-multiple-choice')) {
            if (options && options.length)
                names = jQuery.map(options, function(o){ return $question.find('#option-'+o+'-field, #option-'+o+'-field-open').attr('name'); });
            else
                names = $question.find('.choices > li').find('> :checkbox, .open-option-data').map(function() { return this.name; } );
        }
        return names;
    }

    function was_filled($survey, question, options, last_partecipation_data) {
        if (!last_partecipation_data)
            return false;
        var subject_names = get_question_data_names($survey, question, options);

        // check that at least one option was filled
        var is_filled = false;
        jQuery.each(subject_names, function(i, subject_name) {
            var subject_data = last_partecipation_data[subject_name];
            if (subject_data)
                is_filled = true;
        });
        return is_filled;
    }

    function form_element_fill($element, value) {
        $element.each(function() {
            switch (this.nodeName.toLowerCase()) {
                case "input":
                    switch (this.type) {
                        case "radio":
                            if (value == this.value)
                                this.checked = true;
                            break;
                        case "checkbox":
                            if (jQuery.isArray(value) && jQuery.inArray(value, this.value))
                                this.checked = true;
                            else if (value == this.value)
                                this.checked = true;
                            break;
                        default:
                            jQuery(this).val(value);
                        break;
                    }
                    break;
                case "select":
                    jQuery("option", this).each(function() {
                        if (this.value == value)
                            this.selected = true;
                    });
                break;
            }
        });
        return $element;
    }

    function enable_options ($options) {
        $options.each(function() {
            var $this = $(this);
            var checked = $this.find(':input:visible:not(.open-option-data)').attr('disabled', false).is(':checked')
            $this.find(':input.open-option-data').attr('disabled', !checked);
        });
    }

    // BUILTIN RULES

    function ShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if ($t.length === 1 && $t.is(":hidden") && checked) {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                }
                if ($t.length === 1 && $t.is(":visible") && !checked) {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
            }
        });
    }
    ShowQuestionRule.showQuestions = true;
    ShowQuestionRule.showOptions = false;

    function HideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if ($t.length === 1 && $t.is(":visible") && checked) {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
                if ($t.length === 1 && $t.is(":hidden") && !checked) {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                }
            }
        });
    }
    HideQuestionRule.showQuestions = true;
    HideQuestionRule.showOptions = false;

    function ShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked) {
                    $t.slideDown();
                    enable_options($t);
                }
                else {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
            }
        });
    }
    ShowOptionsRule.showQuestions = true;
    ShowOptionsRule.showOptions = true;

    function HideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (checked) {
                    $t.slideUp().find(':input').attr('disabled', true);
                }
                else {
                    $t.slideDown().find(':input').attr('disabled', false);
                    enable_options($t);
                }
            }
        });
    }
    HideOptionsRule.showQuestions = true;
    HideOptionsRule.showOptions = true;

    function CheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', true).change();
            }
        });
    }
    CheckOptionsRule.showQuestions = true;
    CheckOptionsRule.showOptions = true;

    function UncheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var $t = $survey.find(selectors);
                if (checked)
                    $t.attr('checked', false).change();
            }
        });
    }
    UncheckOptionsRule.showQuestions = true;
    UncheckOptionsRule.showOptions = true;

    function ExclusiveRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: true,

            init: function($survey, last_partecipation_data) {
            },

            apply: function($survey, checked) {
            }
        });
    }
    ExclusiveRule.showQuestions = false;
    ExclusiveRule.showOptions = false;

    function FutureFillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                if ($survey.is('.error'))
                    return;
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_partecipation_data)) {
                    var object_names = get_question_data_names($survey, self.objectQuestion, self.objectOptions);
                    jQuery.each(object_names, function(i, object_name) {
                        var object_data = last_partecipation_data[object_name];
                        form_element_fill($survey.find('[name='+object_name+']'), object_data).change();
                    });
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureFillRule.showQuestions = true;
    FutureFillRule.showOptions = true;

    function FutureShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_partecipation_data)) {
                    enable_options($t.show().find('.choices > li'));
                }
                else {
                    $t.hide().find(':input').attr('disabled', true);
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureShowQuestionRule.showQuestions = true;
    FutureShowQuestionRule.showOptions = false;

    function FutureHideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_partecipation_data)) {
                    $t.hide().find(':input').attr('disabled', true);
                }
                else {
                    enable_options($t.show().find('.choices > li'));
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureHideQuestionRule.showQuestions = true;
    FutureHideQuestionRule.showOptions = false;

    function FutureShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_partecipation_data)) {
                    enable_options($t.show());
                }
                else {
                    $t.hide().find(':input').attr('disabled', true);
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureShowOptionsRule.showQuestions = true;
    FutureShowOptionsRule.showOptions = true;

    function FutureHideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_partecipation_data)) {
                    $t.hide().find(':input').attr('disabled', true);
                }
                else {
                    enable_options($t.show());
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureHideOptionsRule.showQuestions = true;
    FutureHideOptionsRule.showOptions = true;

    function FillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions) {
        var self = this;

        // Public methods.

        $.extend(this, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            isExclusive: false,

            init: function($survey, last_partecipation_data) {
                self.last_partecipation_data = last_partecipation_data;
            },

            apply: function($survey, checked) {
                if ($survey.is('.error'))
                    return;
                if (checked) {
                    var object_names = get_question_data_names($survey, self.objectQuestion, self.objectOptions);
                    jQuery.each(object_names, function(i, object_name) {
                        var object_data = self.last_partecipation_data[object_name];
                        form_element_fill($survey.find('[name='+object_name+']'), object_data).change();
                    });
                }
            }
        });
    }
    FillRule.showQuestions = true;
    FillRule.showOptions = true;

    // MODULE INITIALIZATION

    window.wok.pollster.rules = {
        "ShowQuestion": ShowQuestionRule,
        "HideQuestion": HideQuestionRule,
        "ShowOptions": ShowOptionsRule,
        "HideOptions": HideOptionsRule,
        "CheckOptions": CheckOptionsRule,
        "UncheckOptions": UncheckOptionsRule,
        "Exclusive": ExclusiveRule,
        "FutureFill": FutureFillRule,
        "FutureShowQuestion": FutureShowQuestionRule,
        "FutureHideQuestion": FutureHideQuestionRule,
        "FutureShowOptions": FutureShowOptionsRule,
        "FutureHideOptions": FutureHideOptionsRule,
        "Fill": FillRule
    };

})(jQuery);
