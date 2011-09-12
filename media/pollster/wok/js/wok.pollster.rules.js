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

    function was_filled($survey, question, options, last_participation_data) {
        if (!last_participation_data)
            return false;
        var subject_names = get_question_data_names($survey, question, options);

        // check that at least one option was filled
        var is_filled = false;
        jQuery.each(subject_names, function(i, subject_name) {
            var subject_data = last_participation_data[subject_name];
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

    function enable_options($options) {
        $options.each(function() {
            var $this = $(this);
            var checked = $this.find(':input:visible:not(.open-option-data)').attr('disabled', false).is(':checked')
            $this.find(':input.open-option-data').attr('disabled', !checked);
        });
    }

    function get_target_signature(question, options) {
        var s = "Q" + question;
        if (options) {
            for (var i=0 ; i < options.length; i++) {
                s = s + "O" + options[i];
            }
        }
        return s;
    }

    function get_target_visibility(rule, target, v) {
        var visibility = target.state.visibility;
        var old = visibility[0] + visibility[1];

    }

    function is_active($survey, $question, rule) {
        var $options = $question.find(":checked");
        var $text = $question.find("input[type=text]:not(.open-option-data)");
        for (var i=0 ; i < $options.length ; i++) {
            var oid = parseInt(($options.eq(i).attr("id") || '').replace("option-",""));
            if ($.inArray(oid, rule.subjectOptions) >= 0)
                return true;
        }
        if ($text.length > 0 && $text.val())
            return true;

        return false;
    }

    // BUILTIN RULES

    function ShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target) {
                var $t = $survey.find("#question-"+this.objectQuestion);
                var visibility = target.state.visibility;
                var old = visibility[0] + visibility[1];
                var index = this.isSufficient ? 1 : 0;

                if (!$t.hasClass("starts-hidden"))
                    return;

                if (this.active) {
                    if (visibility[index] === 0)
                        visibility[index] = 1;
                }
                else {
                    if (visibility[index] === 1)
                        visibility[index] = 0;
                }

                if (visibility[0] + visibility[1] > 0 && old === 0) {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                }

                if (visibility[0] + visibility[1] === 0 && old > 0) {
                    $t.slideUp();
                }
            }
        });
    }
    ShowQuestionRule.showQuestions = true;
    ShowQuestionRule.showOptions = false;
    ShowQuestionRule.prototype.name = "ShowQuestionRule";

    function HideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target) {
                var $t = $survey.find("#question-"+this.objectQuestion);
                var visibility = target.state.visibility;
                var old = visibility[0] + visibility[1];
                var index = this.isSufficient ? 1 : 0;

                if ($t.hasClass("starts-hidden"))
                    return;

                if (this.active) {
                    if (visibility[index] === 0)
                        visibility[index] = -1;
                }
                else {
                    if (visibility[index] === -1)
                        visibility[index] = 0;
                }

                if (visibility[0] + visibility[1] < 0 && old === 0) {
                    $t.slideUp();
                }

                if (visibility[0] + visibility[1] === 0 && old < 0) {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                }
            }
        });
    }
    HideQuestionRule.showQuestions = true;
    HideQuestionRule.showOptions = false;
    HideQuestionRule.prototype.name = "HideQuestionRule";

    function ShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target) {
                var visibility = target.state.visibility;
                var old = visibility[0] + visibility[1];
                var index = this.isSufficient ? 1 : 0;

                if (this.active) {
                    if (visibility[index] === 0)
                        visibility[index] = 1;
                }
                else {
                    if (visibility[index] === 1)
                        visibility[index] = 0;
                }

                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (visibility[0] + visibility[1] > 0 && old === 0) {
                    $t.each(function() {
                        var $o = $(this);
                        var v = ($o.data("visibility") || 0) + 1;
                        if (v === 1) {
                            $o.slideDown(function() {
                                enable_options($o.find('.choices > li'));
                            });
                        }
                        $o.data("visibility", v);
                    });
                }

                if (visibility[0] + visibility[1] === 0 && old > 0) {
                    $t.each(function() {
                        var $o = $(this);
                        var v = ($o.data("visibility") || 0) - 1;

                        if (v === 0 && $o.hasClass("starts-hidden")) {
                            $o.slideUp();
                        }
                        $o.data("visibility", v);

                    });
                }
            }
        });
    }
    ShowOptionsRule.showQuestions = true;
    ShowOptionsRule.showOptions = true;
    ShowOptionsRule.prototype.name = "ShowOptionsRule";

    function HideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target) {
                var visibility = target.state.visibility;
                var old = visibility[0] + visibility[1];
                var index = this.isSufficient ? 1 : 0;

                if (this.active) {
                    if (visibility[index] === 0)
                        visibility[index] = -1;
                }
                else {
                    if (visibility[index] === -1)
                        visibility[index] = 0;
                }

                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (visibility[0] + visibility[1] < 0 && old === 0) {
                    $t.each(function() {
                        var $o = $(this);
                        var v = ($o.data("visibility") || 0) + 1;
                        if (v === 1) {
                            $o.slideUp();
                        }
                        $o.data("visibility", v);
                    });
                }

                if (visibility[0] + visibility[1] === 0 && old < 0) {
                    $t.each(function() {
                        var $o = $(this);
                        var v = ($o.data("visibility") || 0) - 1;

                        if (v === 0 && !$o.hasClass("starts-hidden")) {
                            $o.slideDown(function() {
                                enable_options($o.find('.choices > li'));
                            });
                        }
                        $o.data("visibility", v);
                    });
                }
            }
        });
    }
    HideOptionsRule.showQuestions = true;
    HideOptionsRule.showOptions = true;
    HideOptionsRule.prototype.name = "HideOptionsRule";

    function CheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true && old === false;
            },

            apply: function($survey, target) {
                if (!this.active || this._lock)
                    return;

                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var options = $survey.find(selectors).attr('checked', true);
                options.change();
            }
        });
    }
    CheckOptionsRule.showQuestions = true;
    CheckOptionsRule.showOptions = true;
    CheckOptionsRule.prototype.name = "CheckOptionsRule";

    function UncheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true && old === false;
            },

            apply: function($survey, target) {
                if (!this.active || this._lock)
                    return;

                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var options = $survey.find(selectors).attr('checked', false);
                options.change();
            }
        });
    }
    UncheckOptionsRule.showQuestions = true;
    UncheckOptionsRule.showOptions = true;
    UncheckOptionsRule.prototype.name = "UncheckOptionsRule";

    function ExclusiveRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: null,
            isExclusive: true,

            init: function($survey, last_participation_data) {
                var selectors = self.subjectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                $(selectors).addClass("exclusive");
            },

            activate: function($survey, $question, evt) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true &&  old === false;
            },

            apply: function($survey) {
                if (!this.active)
                    return;

                var so = this.subjectOptions;
                var extra = { synthetic: true };
                $survey.find("#question-"+this.subjectQuestion+" :checked").each(function() {
                    var oid = parseInt(($(this).closest("li").attr("id") || '').replace("option-",""))
                    if (so.indexOf(oid) < 0)
                        $(this).attr('checked', false).trigger('change', extra);
                });
            }
        });
    }
    ExclusiveRule.prototype.name = "ExclusiveRule";

    function FutureFillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                if ($survey.is('.error'))
                    return;
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_participation_data)) {
                    var object_names = get_question_data_names($survey, self.objectQuestion, self.objectOptions);
                    jQuery.each(object_names, function(i, object_name) {
                        var object_data = last_participation_data[object_name];
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
    FutureFillRule.prototype.name = "FutureFillRule";

    function FutureShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_participation_data)) {
                    enable_options($t.show().find('.choices > li'));
                }
                else {
                    $t.hide();
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureShowQuestionRule.showQuestions = true;
    FutureShowQuestionRule.showOptions = false;
    FutureShowQuestionRule.prototype.name = "FutureShowQuestionRule";

    function FutureHideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                var $t = $survey.find("#question-"+self.objectQuestion);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_participation_data)) {
                    $t.hide();
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
    FutureHideQuestionRule.prototype.name = "FutureHideQuestionRule";

    function FutureShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_participation_data)) {
                    enable_options($t.show());
                }
                else {
                    $t.hide();
                }
            },

            apply: function($survey, checked) {
            }
        });
    }
    FutureShowOptionsRule.showQuestions = true;
    FutureShowOptionsRule.showOptions = true;
    FutureShowOptionsRule.prototype.name = "FutureShowOptionsRule";

    function FutureHideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);
                if (was_filled($survey, self.subjectQuestion, self.subjectOptions, last_participation_data)) {
                    $t.hide();
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
    FutureHideOptionsRule.prototype.name = "FutureHideOptionsRule";

    function FillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                self.last_participation_data = last_participation_data;
            },

            apply: function($survey, checked) {
                if ($survey.is('.error'))
                    return;
                if (checked) {
                    var object_names = get_question_data_names($survey, self.objectQuestion, self.objectOptions);
                    jQuery.each(object_names, function(i, object_name) {
                        var object_data = self.last_participation_data[object_name];
                        form_element_fill($survey.find('[name='+object_name+']'), object_data).change();
                    });
                }
            }
        });
    }
    FillRule.showQuestions = true;
    FillRule.showOptions = true;
    FillRule.prototype.name = "FillRule";

    // MODULE INITIALIZATION

    window.wok.pollster.rules = {
        "ShowQuestion": ShowQuestionRule,
        "HideQuestion": HideQuestionRule,
        "ShowOptions": ShowOptionsRule,
        "HideOptions": HideOptionsRule,
        "CheckOptions": CheckOptionsRule,
        "UncheckOptions": UncheckOptionsRule,
        "Exclusive": ExclusiveRule,
        "Fill": FillRule,
        "FutureFill": FutureFillRule,
        "FutureShowQuestion": FutureShowQuestionRule,
        "FutureHideQuestion": FutureHideQuestionRule,
        "FutureShowOptions": FutureShowOptionsRule,
        "FutureHideOptions": FutureHideOptionsRule
    };

})(jQuery);
