(function($) {

    // COMMON UTILITIES

    function getQuestionType($element) {
        var m = /(builtin|text|single-choice|multiple-choice|matrix-select|matrix-entry)/.exec($element.attr("class"));
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

    function getQuestionIsMandatory($element) {
        return $element.is(".mandatory") ? 'true' : 'false';
    }

    function getChoiceStartsHidden($element) {
        return $element.is(".starts-hidden") ? 'true' : 'false';
    }

    function getChoiceIsOpen($element) {
        return $element.is(".open") ? 'true' : 'false';
    }

    function getRulesBySubjectQuestion($canvas, question) {
        return $canvas.find(".rule[data-subject-question='"+question+"']");
    }

    function getRulesByOption($canvas, option) {
        return $canvas.find('.rule').filter(function() {
            var $this = $(this);
            var subj = $this.attr('data-subject-options');
            var obj = $this.attr('data-object-options');
            return $.inArray(option, (obj+' '+subj).split()) >= 0;
        });
    }

    function getText($element, toRemove) {
        var text = $element.contents().filter(function(){ return this.nodeType === 3; }).text();
        if (toRemove)
            return $.trim(text.replace(toRemove, ""));
        else
            return $.trim(text);
    }

    function isIdTemporary(id) {
        if (id.match(/^.+-\d+$/))
            return false;
        return true;
    }

    function remakeIdTemporary(designer, id) {
        var t = designer.getNextTemporaryId();
        if (id.match(/^question-/))
            return 'question-N'+t;
        if (id.match(/^column-/))
            return 'column-N'+t;
        if (id.match(/^row-/))
            return 'row-N'+t;
        if (id.match(/^option-/))
            return 'option-N'+t;
        if (id.match(/^rule-/))
            return 'rule-N'+t;
        return id;
    }

    function resetIds(designer, $element) {
        var idmap = {}
        $element.find('.question, [id^="column-"], [id^="row-"], [id^="option-"], [id^="rule-"]').each(function(){
            var newId = remakeIdTemporary(designer, this.id);
            $(this).find('#'+this.id+'-field').each(function(){ this.id = newId+'-field'; });
            idmap[this.id] = newId;
            this.id = newId;
        });
        $element.find('[data-subject-options]').each(function(){
            var ids = $(this).attr('data-subject-options');
            ids = jQuery.map(ids, function(id) {
                if (idmap[id] !== undefined)
                    return idmap[id];
                return id;
            });
            $(this).attr('data-subject-options', ids.join(' '));
        });
        $element.find('[data-object-question]').each(function(){
            var id = $(this).attr('data-object-question');
            if (idmap[id] !== undefined)
                $(this).attr('data-object-question', idmap[id]);
        });
        $element.find('[data-object-options]').each(function(){
            var ids = $(this).attr('data-object-options');
            ids = jQuery.map(ids, function(id) {
                if (idmap[id] !== undefined)
                    return idmap[id];
                return id;
            });
            $(this).attr('data-object-options', ids.join(' '));
        });
    }

    // BUILTIN PROPERTY PROVIDERS

    function QuestionPropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Tool actions.

        $properties.find(".action-add-choice").click(function(evt) {
            if (self.$element === null) return true;
            var type = getQuestionType(self.$element);
            var $item;
            if (type == "single-choice" || type == "matrix-select") {
                $item = $('<li><div class="info"></div><input type="radio" value=""/><label></label></li>');
            }
            else if (type == "multiple-choice") {
                $item = $('<li><div class="info"></div><input type="checkbox" value=""/><label></label></li>');
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
                        .append('<div class="info"><input class="derived" type="checkbox" disabled="disabled"></div>')
                );
            }
            if (type == "rule") {
                self.$element.siblings(".rules").append($('<div class="rule sufficient">EMPTY RULE</div>'));
            }
        });

        $properties.find(".action-add-column").click(function(evt) {
            if (self.$element === null) return true;
            var type = getQuestionType(self.$element.closest('.question'));
            var $tmpl = $(".wok-templates .template-question-"+type+" .columns li").clone();
            self.$element.find(".columns").append($tmpl);
        });

        $properties.find(".action-add-row").click(function(evt) {
            if (self.$element === null) return true;
            var type = getQuestionType(self.$element.closest('.question'));
            var $tmpl = $(".wok-templates .template-question-"+type+" .rows li").clone();
            self.$element.find(".rows").append($tmpl);
        });

        // Events.

        $properties.find(".action-copy").click(function(evt) {
            if (self.$element === null) return true;

            var $wrapper = self.$element.closest('.question-wrapper');
            var $clone = $wrapper.clone();
            $clone.find('.selected').removeClass("selected");
            $clone.removeClass("active");
            resetIds(designer, $clone);
            $wrapper.after($clone);
        });

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;

            var $survey = self.$element.closest('.survey');
            if (isIdTemporary(self.$element.attr('id'))) {
                self.$element.closest('.question-wrapper').remove();
                getRulesBySubjectQuestion($survey, self.$element.attr('id')).remove();
            }
            else {
                self.$element.addClass('deleted');
                self.$element.closest('.question-wrapper').addClass('deleted');
                getRulesBySubjectQuestion($survey, self.$element.attr('id')).addClass('deleted');
            }
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_question_data_name]").keyup(function(evt) {
            if (self.$element === null) return true;
            var v = $(this).val().trim();
            var $e = self.$element.find(".data-name");
            $e.text(v || "??");
            $e.toggleClass('placeholder', !v);
            return false;
        });

        $properties.find("[name=field_question_title]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find(".title").text($(this).val());
            return false;
        });

        $properties.find("[name=field_question_text]").keyup(function(evt) {
            if (self.$element === null) return true;
            var $p = self.$element.find("p").first();
            var $t = $p.children("span").remove();
            $p.text($(this).val());
            $p.prepend($t);
            return false;
        });

        $properties.find("[name=field_question_tags]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-tags", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_data_type]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-data-type", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_open_option_data_type]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-open-option-data-type", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_visual]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("data-visual", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_starts_hidden]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.toggleClass('starts-hidden', $(this).val() == 'true');
            return false;
        });

        $properties.find("[name=field_question_is_mandatory]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.toggleClass('mandatory', $(this).val() == 'true');
            return false;
        });

        $properties.find("[name=field_question_regex]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find('input').attr("pattern", $(this).val());
            return false;
        });

        $properties.find("[name=field_question_error_message]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find('.error-message').text($(this).val());
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
                    .find("[name=field_question_data_type]").val($e.attr("data-data-type")).end()
                    .find("[name=field_question_open_option_data_type]").val($e.attr("data-open-option-data-type")).end()
                    .find("[name=field_question_visual]").val($e.attr("data-visual")).end()
                    .find("[name=field_question_tags]").val($e.attr("data-tags")).end()
                    .find("[name=field_question_title]").val($.trim($e.find(".title").text())).end()
                    .find("[name=field_question_text]").val(getText($e.find("p").first())).end()
                    .find("[name=field_question_data_name]").val(designer.getQuestionShortname($e)).end()
                    .find("[name=field_question_starts_hidden]").val(getQuestionStartsHidden($e)).end()
                    .find("[name=field_question_is_mandatory]").val(getQuestionIsMandatory($e)).end()
                    .find("[name=field_question_regex]").val($e.find('input').attr("pattern")).end()
                    .find("[name=field_question_error_message]").val($e.find('.error-message').text()).end()
                    .show();

                // We display visual options depending on the question type.

                var $v = $properties.find("[name=field_question_visual]");
                var visual = $e.attr("data-visual");
                var enabled;
                if (type === "text") {
                    enabled = "[value=entry]";
                }
                else if (type === "single-choice") {
                    enabled = "[value=radio],[value=dropdown]";
                }
                else if (type === "multiple-choice") {
                    enabled = "[value=check]";
                }
                $v.find("option").hide().attr('disabled', true).end()
                var visuals_shown = $v.find(enabled).attr('disabled', false).show().length;
                $v.val(visual);

                // We display the tools depending on the question type.

                if (type === "builtin") {
                    $properties.find(".property, .tool").hide();
                    $properties.find("[name=tool_rule_type]").closest(".tool").show()
                }
                else if (type === "text") {
                    $properties.find(".property, .tool, .tool option").show();
                    $properties.find("[name=tool_choice_type]").closest(".tool").hide();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").show();
                    $properties.find("[name=field_question_open_option_data_type]").closest('.property').hide();
                    $properties.find(".action-add-column, .action-add-row").closest(".tool").hide();
                }
                else if (type === "single-choice") {
                    $properties.find(".property, .tool, .tool option").show();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").hide().parent().val("rule");
                    $properties.find(".action-add-column, .action-add-row").closest(".tool").hide();
                }
                else if (type === "multiple-choice") {
                    $properties.find(".property, .tool, .tool option").show();
                    $properties.find("[name=tool_rule_type] [value='derived-value']").hide().parent().val("rule");
                    $properties.find(".action-add-column, .action-add-row").closest(".tool").hide();
                }
                else if (type === "matrix-select") {
                    $properties.find(".property, .tool, .tool option").show();
                    $properties.find("[name=tool_rule_type]").closest(".tool").hide()
                    $properties.find("[name=field_question_open_option_data_type]").closest('.property').hide();
                }
                else if (type === "matrix-entry") {
                    $properties.find(".property, .tool, .tool option").show();
                    $properties.find("[name=tool_choice_type]").closest(".tool").hide();
                    $properties.find("[name=tool_rule_type]").closest(".tool").hide()
                    $properties.find("[name=field_question_open_option_data_type]").closest('.property').hide();
                }
                $properties.find("[name=field_question_visual]").closest('.property').toggle(visuals_shown > 1);
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

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;

            var $survey = self.$element.closest('.survey');
            if (isIdTemporary(self.$element.attr('id'))) {
                self.$element.remove();
                getRulesByOption($survey, self.$element.attr('id')).remove();
            }
            else {
                self.$element.addClass('deleted');
                getRulesByOption($survey, self.$element.attr('id')).addClass('deleted');
            }
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_choice_text]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find("label").text($(this).val());
            return false;
        });

        $properties.find("[name=field_choice_description]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.attr("title", $(this).val());
            return false;
        });

        $properties.find("[name=field_choice_value]").keyup(function(evt) {
            if (self.$element === null) return true;
            var v = $(this).val().trim();
            self.$element.find(":checkbox,:radio").val(v);
            var $e = self.$element.find(".info");
            $e.text(v || "??");
            $e.toggleClass('placeholder', !v);
            return false;
        });

        $properties.find("[name=field_choice_starts_hidden]").change(function(evt) {
            if (self.$element === null) return true;
            self.$element.toggleClass("starts-hidden", $(this).val() == 'true');
            return false;
        });

        $properties.find("[name=field_choice_is_open]").change(function(evt) {
            if (self.$element === null) return true;
            if ($(this).val() == 'true') {
                self.$element.addClass("open");
                self.$element.find('label').after('<input type="text"/>');
            }
            else {
                self.$element.removeClass("open");
                self.$element.find('label + input').remove();
            }
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
                    .find("[name=field_choice_value]").val($e.find(":checkbox,:radio").val()).end()
                    .find("[name=field_choice_description]").val($e.attr("title")).end()
                    .find("[name=field_choice_starts_hidden]").val(getChoiceStartsHidden($e)).end()
                    .find("[name=field_choice_is_open]").val(getChoiceIsOpen($e)).end()
                    .show();
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    function ColumnPropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Events.

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;
            if (!self.$element.siblings().length) return true; // leave at least one column

            if (isIdTemporary(self.$element.attr('id')))
                self.$element.remove();
            else
                self.$element.addClass('deleted');
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_column_title]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find('.column-title').text($(this).val());
            return false;
        });

        // Public methods.

        $.extend(this, {
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                $properties
                    .find("[name=field_column_title]").val($e.find('.column-title').text()).end()
                    .show();
            },
            detach: function() {
                self.$element = null;
            }
        });
    }

    function RowPropertyProvider(designer, $properties) {
        var self = this, _lock = false;

        self.$element = null;

        // Events.

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;
            if (!self.$element.siblings().length) return true; // leave at least one row

            if (isIdTemporary(self.$element.attr('id')))
                self.$element.remove();
            else
                self.$element.addClass('deleted');
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_row_title]").keyup(function(evt) {
            if (self.$element === null) return true;
            self.$element.find('.row-title').text($(this).val());
            return false;
        });

        // Public methods.

        $.extend(this, {
            attach: function($e) {
                if (self.$element !== null)
                    self.detach();
                self.$element = $e;
                $properties
                    .find("[name=field_row_title]").val($e.find('.row-title').text()).end()
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
            var $option = $properties.find("[name=field_derived_value_type] option:selected");
            var text = $option.text() || 'Derived value';
            var jsclass = eval('('+$option.attr('data-js-class')+')');
            var inf = $e.attr("data-inf") || "";
            var sup = $e.attr("data-sup") || "";
            var regexp = $e.attr("data-regex") || "";

            if (jsclass.isRegularExpression)
                $element.text(text+": " + regexp).append(info);
            if (jsclass.isRange)
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
                        $o.show().attr('disabled', false);
                    else
                        $o.hide().attr('disabled', true);
                });
                $derived_value_types.val($element.attr('data-type')).change();

                var jsclass = eval('('+$derived_value_types.find(':selected').attr("data-js-class")+')');
                if (jsclass.isRegularExpression) {
                    $properties.find("[name=field_derived_value_regex]").closest(".property").show();
                    $properties.find("[name=field_derived_value_inf],[name=field_derived_value_sup]").closest(".property").hide();
                }
                if (jsclass.isRange) {
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

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;

            var $survey = self.$element.closest('.survey');
            if (isIdTemporary(self.$element.attr('id'))) {
                self.$element.remove();
                getRulesByOption($survey, self.$element.attr('id')).remove();
            }
            else {
                self.$element.addClass('deleted');
                getRulesByOption($survey, self.$element.attr('id')).addClass('deleted');
            }
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_derived_value_inf],[name=field_derived_value_sup],"
                        +"[name=field_derived_value_regex]").keyup(function(evt) {
            if (self.$element === null) return true;
            var dataName = "data-" + $(this).attr("name").replace("field_derived_value_", "");
            self.$element.attr(dataName, $(this).val());
            formatText(self.$element);
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

        function describeOption($o) {
            var v = $o.find("input").val() || $o.attr("data-value") || "??";
            var text = "Option '" + v + "'";
            if ($o.find('.derived').length)
                text = 'Derived ' + $o.text();
            return text;
        }

        function formatText($element) {
            var $selected = $properties.find("[name=field_rule_type] :selected");
            var type = $selected.text();
            var subject_options = $properties.find("[name=field_rule_subject_options] :selected");
            var object_question = $properties.find("[name=field_rule_object_question] :selected");
            var object_options = $properties.find("[name=field_rule_object_options] :selected");

            var ruleClass = eval($selected.attr('data-js-class'));

            function describeOptions(selected) {
                var ret = '*';
                if (selected.val()) {
                    var $o = $('#'+selected.first().val());
                    var i = $o.index() + 1;
                    ret = describeOption($o);
                    if (selected.length == 2)
                        ret += " + another";
                    else if(selected.length > 2)
                        ret += " +"+(selected.length-1)+" others";
                }
                return ret;
            }

            var subject = describeOptions(subject_options);
            var object = '';
            if (ruleClass.showQuestions)
                object = object_question.text();
            if (ruleClass.showOptions)
                object = "(" + describeOptions(object_options) + ") from " + object_question.text();
            $element.text(subject + " => " + type + " " + object);
        }

        function fillOptions($question, $dest) {
            $question.closest(".question-wrapper").find(".question li").each(function(i) {
                var $o = $(this);
                var text = describeOption($o);
                $dest.append($('<option></option>')
                    .text(text)
                    .attr("value", $o.attr("id"))
                );
            });
        }

        // Dynamic UI generation and properties dependencies.

        function updateUI($element) {
            var $type = $properties.find("[name=field_rule_type]");
            $type.val($element.attr("data-type")).change();

            var $isSufficient = $properties.find("[name=field_rule_is_sufficient]");
            var val = $element.hasClass('sufficient') ? "true" : "false";
            $isSufficient.val(val).change();

            var $subject_options = $properties.find("[name=field_rule_subject_options]").empty();
            var $object_question = $properties.find("[name=field_rule_object_question]").empty();

            // FIXME: Propagate options.
            $subject_options.empty();
            fillOptions($element, $subject_options);
            var ids = ($element.attr("data-subject-options") || '').split(' ');
            $subject_options.val(ids).change();

            // FIXME: Propagate options.
            $(".question-wrapper > .question:not(.question-builtin)").each(function() {
                var $q = $(this);
                $object_question.append($('<option></option>')
                    .text($q.find(".data .data-name").text()+" '"+$q.find(".data .title").text() + "'")
                    .attr("value", $q.attr("id"))
                );
            });

            $object_question.val($element.attr('data-object-question')).change();
        }

        // Events.

        $properties.find(".action-delete").click(function(evt) {
            if (self.$element === null) return true;

            if (isIdTemporary(self.$element.attr('id')))
                self.$element.remove();
            else
                self.$element.addClass('deleted');
            self.detach();
            $(this).closest('.property-group').nextAll('.property-group').andSelf().hide();
        });

        $properties.find("[name=field_rule_type]").change(function(evt) {
            if (self.$element === null) return true;
            var $this = $(this);
            var val = $this.val();
            self.$element.attr("data-type", val);
            var ruleClass = eval($this.find(':selected').attr('data-js-class'));
            $properties.find("[name=field_rule_object_question]").closest(".property").toggle(Boolean(ruleClass.showQuestions));
            $properties.find("[name=field_rule_object_options]").closest(".property").toggle(Boolean(ruleClass.showOptions));
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_rule_is_sufficient]").change(function(evt) {
            if (self.$element === null) return true;
            var $this = $(this);
            var sufficient = $this.val() == "true";
            self.$element.toggleClass('sufficient', sufficient);
            self.$element.toggleClass('required', !sufficient);
            formatText(self.$element);
            return false;
        });

        $properties.find("[name=field_rule_subject_options]").change(function(evt) {
            if (self.$element === null) return true;
            var val = $(this).val();
            if (val)
                self.$element.attr("data-subject-options", val.join(" "));
            else
                self.$element.attr("data-subject-options", '');
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
                    .find("[name=field_rule_subject_options]").val($e.attr("data-subject-options").split(' ')).end()
                    .find("[name=field_rule_object_question]").val($e.attr("data-object-question")).end()
                    .find("[name=field_rule_object_options]").val($e.attr("data-object-options").split(' ')).end()
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
        "builtin-column": ColumnPropertyProvider,
        "builtin-row": RowPropertyProvider,
        "builtin-derived-value": DerivedValuePropertyProvider,
        "builtin-rule": RulePropertyProvider
    };

})(jQuery);

