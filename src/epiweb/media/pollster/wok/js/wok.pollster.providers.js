(function($) {

    // COMMON UTILITIES

    function getQuestionType($element) {
        var m = /(text|single-choice|multiple-choice)/.exec($element.attr("class"));
        if (m)
            return m[1];
        else
            return "";
    }

    function getQuestionDataType($element) {
        return $element.attr("data-data-type") || "1";
    }

    function getQuestionStartsHidden($element) {
        return $element.is(".starts-hidden") ? 'true' : 'false';
    }

    function getChoiceStartsHidden($element) {
        return $element.is(".starts-hidden") ? 'true' : 'false';
    }

    function getText($element, toRemove) {
        var text = $element.contents().filter(function(){ return this.nodeType === 3; }).text();
        if (toRemove)
            return $.trim(text.replace(toRemove, ""));
        else
            return $.trim(text);
    }

    // BUILTIN PROPERTY PROVIDERS

    function QuestionPropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        /* function changeVisual(visual) {
            var $e = self.$element;
            if (visual === "radio") {
                if ($e.find("select").length === 0)
                    return;
                var $x = $('<ul></ul>');
                $e.find("select option").each(function() {
                    $x.append()
                });
            }
        }*/

        // Tool actions.

        $properties.find(".action-add-choice").click(function(evt) {
            if (self.$element === null) return true;
            var type = getQuestionType(self.$element);
            var $item;
            if (type == "single-choice") {
                $item = $('<li><input type="radio" value=""/><label></label><div class="info"></div></li>');
            }
            else if (type == "multiple-choice") {
                $item = $('<li><input type="checkbox" value=""/><label></label><div class="info"></div></li>');
            }
            self.$element.find(".choices").append($item.attr("id", "option-N" + designer.getNextTemporaryId()));
        });

        $properties.find(".action-add-rule").click(function(evt) {
            if (self.$element === null) return true;

            var type = $(this).siblings("select").val();

            if (type == "derived-value") {
                self.$element.find(".derived-values").append(
                    $('<li></li>')
                        .attr("id", "option-N" + designer.getNextTemporaryId())
                        .text("EMPTY (click to edit)")
                        .append('<div class="info"></div>')
                );
            }
            if (type == "rule") {
                self.$element.siblings(".rules").append($('<div class="rule">EMPTY RULE</div>'));
            }
        });

        // Events.

        $properties.find("[name=field_question_shortname]").keyup(function(evt) {
            if (self.$element === null) return true;
            var v = $(this).val();
            self.$element.attr("data-shortname", v);
            self.$element.children(".info").text(v);
            return false;
        });

        $properties.find("[name=field_question_title]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find(".title").text($(this).val());
            return false;
        });

        $properties.find("[name=field_question_text]").keyup(function(evt) {
            if (self.$element === null) return true;
            var $p = self.$element.find("p");
            var $t = $p.children("span").remove();
            $p.text($(this).val());
            $p.prepend($t);
            return false;
        });

        $properties.find("[name=field_question_data_type]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-data-type", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_starts_hidden]").change(function(evt) {
            if (self.$element === null) return true;
            if ($(this).val() == 'true')
                self.$element.addClass("starts-hidden");
            else
                self.$element.removeClass("starts-hidden");
            return false;
        });

        // Public methods.

        $.extend(this, {
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                var type = getQuestionType($e);
                $properties
                    .find("[name=field_question_type]").val(type).end()
                    .find("[name=field_question_data_type]").val($e.attr("data-data-type")).end()
                    .find("[name=field_question_title]").val($.trim($e.find(".title").text())).end()
                    .find("[name=field_question_text]").val(getText($e.find("p"))).end()
                    .find("[name=field_question_shortname]").val(designer.getQuestionShortname($e)).end()
                    .find("[name=field_question_starts_hidden]").val(getQuestionStartsHidden($e)).end()
                    .show();

                // We display visual options depending on the question type.

                var $v = $properties.find("[name=field_question_visual]");
                if (type === "text") {
                    $v.find("option").hide().end().find("[value=entry]").show().parent().val("entry");
                }
                else if (type === "single-choice") {
                    var visual = $e.find("select").length === 1 ? "select" : "radio";
                    $v.find("option").hide().end().find("[value=radio],[value=dropdown]").show().parent().val(visual);
                }
                else if (type === "multiple-choice") {
                    $v.find("option").hide().end().find("[value=check]").show().parent().val("check");
                }

                // We display the tools depending on the question type.

                if (type === "text") {
                    $properties.find("[name=tool_choice_type]").closest(".tool").hide();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").show();
                }
                else if (type === "single-choice") {
                    $properties.find("[name=tool_choice_type]").closest(".tool").show();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").hide().parent().val("rule");
                }
                else if (type === "multiple-choice") {
                    $properties.find("[name=tool_choice_type]").closest(".tool").show();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").hide().parent().val("rule");
                }
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    function ChoicePropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Events.

        $properties.find("[name=field_choice_text]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find("label").text($(this).val());
            return false;
        });

        $properties.find("[name=field_choice_value]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find("input").val($(this).val());
            self.$element.find(".info").text($(this).val());
            return false;
        });

        $properties.find("[name=field_choice_starts_hidden]").change(function(evt) {
            if (self.$element === null) return true;
            if ($(this).val() == 'true')
                self.$element.addClass("starts-hidden");
            else
                self.$element.removeClass("starts-hidden");
            return false;
        });

        // Public methods.

        $.extend(this, {
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                $properties
                    .find("[name=field_choice_text]").val($e.find("label").text()).end()
                    .find("[name=field_choice_value]").val($e.find("input").val()).end()
                    .find("[name=field_choice_starts_hidden]").val(getChoiceStartsHidden($e)).end()
                    .show();
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    function DerivedValuePropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Derived value formatting.

        function formatText($element) {
            var $e = $element;
            var info = $e.find(".info").remove();
            var text = $properties.find("[name=field_derived_value_type] option:selected").text();
            var inf = $e.attr("data-inf") || "";
            var sup = $e.attr("data-sup") || "";
            var regexp = $e.attr("data-regex") || "";

            // TODO: Find a way to not hard-code "5" here.
            if ($e.attr("data-type") === "5")
                $element.text(text+": " + regexp).append(info);
            else
                $element.text(text+": [" + inf + "," + sup + "]").append(info);
        }

        // Dynamic UI generation and property dependencies.

        function updateUI($element, updateType) {
            if (!_lock) {
                _lock = true;

                // FIXME: Propagate options.
                var type = getQuestionDataType($element.closest(".question"));
                // We show only the correct types in the field_derived_value_type dropdown.
                // Note that we should make sure to also select the first valid option and
                // to set the current virtual option type to the selected value.
                var found = false;
                var $derived_value_types = $properties.find("[name=field_derived_value_type]");
                $derived_value_types.find("option").each(function() {
                    var $o = $(this);
                    if ($o.attr("data-linked-data-type") === type)
                        $o.show();
                    else
                        $o.hide();
                });
                $derived_value_types.val($element.attr('data-type')).change();

                // TODO: Find a way to not hard-code "5" here.

                if ($element.attr("data-type") === "5") {
                    $properties.find("[name=field_derived_value_regex]").closest(".property").show();
                    $properties.find("[name=field_derived_value_inf],[name=field_derived_value_sup]").closest(".property").hide();
                }
                else {
                    $properties.find("[name=field_derived_value_regex]").closest(".property").hide();
                    $properties.find("[name=field_derived_value_inf],[name=field_derived_value_sup]").closest(".property").show();
                }

                _lock = false;
            }
        }

        $properties.closest(".property-groups").find("[name=field_question_data_type]").change(function(evt) {
            if (self.$element === null) return true;
            updateUI(self.$element, true);
            return false;
        });

        // Events.

        $properties.find("[name=field_derived_value_inf],[name=field_derived_value_sup],"
                        +"[name=field_derived_value_regex]").keyup(function(evt) {
            if (self.$element === null) return true;
            var dataName = "data-" + $(this).attr("name").replace("field_derived_value_", "");
            self.$element.attr(dataName, $(this).val());
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_derived_value_value]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-value", $(this).val());
            self.$element.find(".info").text($(this).val());
            return false;
        });

        $properties.find("[name=field_derived_value_type]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-type", $(this).val());
            updateUI(self.$element);
            formatText(self.$element);
            return false;
        });

        // Public methods.

        $.extend(this, {
            setup: function($e) {
                var old = self.$element;
                self.$element = $e;
                updateUI($e);
                formatText($e);
                self.$element = old;
            },
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                $properties
                    .find("[name=field_derived_value_type]").val($e.attr("data-type")).end()
                    .find("[name=field_derived_value_regex]").val($e.attr("data-regex")).end()
                    .find("[name=field_derived_value_inf]").val($e.attr("data-inf")).end()
                    .find("[name=field_derived_value_sup]").val($e.attr("data-sup")).end()
                    .find("[name=field_derived_value_value]").val($e.attr("data-value")).end()
                    .show();
                updateUI($e, !$e.attr("data-type"));
                formatText(self.$element);
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    function RulePropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Derived value formatting.

        function formatText($element) {
            var type = $properties.find("[name=field_rule_type] :selected").text();
            var subject_option = $properties.find("[name=field_rule_subject_option] :selected");
            var object_question = $properties.find("[name=field_rule_object_question] :selected");
            var object_options = $properties.find("[name=field_rule_object_options] :selected");

            var subject = '';
            if (subject_option.val())
                subject = subject_option.text();
            var object = object_question.text();
            if (object_options.length > 0)
                object = object_options.length + " Options from " + object_question.text();

            $element.text(subject + " => " + type + " " + object);
        }

        function fillOptions($question, $dest) {
            $question.closest(".question-wrapper").find(".question li").each(function(i) {
                var $o = $(this);
                var v = $o.find("input").val() || $o.attr("data-value") || "NO VALUE";
                $dest.append($('<option></option>')
                    .text("Option " + (i+1) + " [" + v + "]")
                    .attr("value", $o.attr("id"))
                );
            });
        }

        // Dynamic UI generation and properties dependencies.

        function updateUI($element) {
            var $type = $properties.find("[name=field_rule_type]");
            $type.val($element.attr("data-type")).change();

            var $subject_option = $properties.find("[name=field_rule_subject_option]").empty();
            var $object_question = $properties.find("[name=field_rule_object_question]").empty();

            // FIXME: Propagate options.
            $subject_option.empty();
            fillOptions($element, $subject_option);
            $subject_option.val($element.attr("data-subject-option")).change();

            // FIXME: Propagate options.
            $(".question-wrapper > .question").each(function() {
                var $q = $(this);
                $object_question.append($('<option></option>')
                    .text($q.find(".number").text()+" "+$q.find(".title").text() + " [" + $q.children(".info").text() + "]")
                    .attr("value", $q.attr("id"))
                );
            });

            $object_question.val($element.attr('data-object-question')).change();
        }

        // Events.

        $properties.find("[name=field_rule_type]").change(function(evt) {
            if (self.$element === null) return true;
            var val = $(this).val();
            self.$element.attr("data-type", val);
            // TODO: don't hard-code "3" and "4" here.
            $properties.find("[name=field_rule_object_options]").closest(".property").toggle(val === "3" || val === "4");
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_rule_subject_option]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-subject-option", $(this).val());
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_rule_object_question]").change(function(evt) {
            if (self.$element === null) return true;
            var val = $(this).val();
            self.$element.attr("data-object-question", val);
            var $question = self.$element.closest('.survey').find('#'+val);
            var $options = $properties.find('[name=field_rule_object_options]').empty();
            fillOptions($question, $options);
            var selected = (self.$element.attr("data-object-options") || '').trim().split(/\s+/);
            $options.val(selected).change();
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_rule_object_options]").change(function(evt) {
            if (self.$element === null) return true;
            var val = $(this).val();
            if (val)
                self.$element.attr("data-object-options", val.join(" "));
            else
                self.$element.attr("data-object-options", '');
            formatText(self.$element);
            return false;
        });

        // Public methods.

        $.extend(this, {
            setup: function($e) {
                var old = self.$element;
                self.$element = $e;
                updateUI($e);
                formatText($e);
                self.$element = old;
            },
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                updateUI($e);
                $properties
                    .find("[name=field_rule_type]").val($e.attr("data-type")).end()
                    .find("[name=field_rule_trigger]").val($e.attr("data-trigger")).end()
                    .find("[name=field_rule_question]").val($e.attr("data-question")).end()
                    .find("[name=field_rule_option]").val($e.attr("data-option")).end()
                    .show();
                formatText($e);
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    // MODULE INITIALIZATION

    window.wok.pollster.propertyProviders = {
        "builtin-question": QuestionPropertyProvider,
        "builtin-choice": ChoicePropertyProvider,
        "builtin-derived-value": DerivedValuePropertyProvider,
        "builtin-rule": RulePropertyProvider
    };

})(jQuery);

