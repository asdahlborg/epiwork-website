(function($) {
    // MODULE: wok.pollster

    window.wok = window.wok || {
        version: '1.0',
        error: function(msg) { alert("wok error: " + msg); }
    };
    window.wok.pollster = {
        options: {
            // UI part selectors.
            canvasSelector: "#pollster-canvas",
            propertiesSelector: "#pollster-properties",
            templateClass: "survey",
            questionClass: "question"
        }
    };

    // POLLSTER SURVEY

    function PollsterRuntime(context, options) {
        context = context || document;
        options = $.extend({}, window.wok.pollster.options, options);

        var self = this;
        var $survey = $('.'+options.templateClass, context);
        var questionSelector = '.'+options.questionClass;

        var last_partecipation_data = pollster_last_partecipation_data();

        var data_types = {}, rules_by_question = {}, derived_values = {};

        pollster_fill_data_types(data_types);
        pollster_fill_rules(rules_by_question);
        pollster_fill_derived_values(derived_values);

        $survey.find('.open-option-data').attr('disabled', true);
        if (last_partecipation_data && last_partecipation_data.timestamp)
            $('.question-builtin [name=timestamp]').val(last_partecipation_data.timestamp);

        // Bind data types to question elements

        $.each(data_types, function(question, data_type) {
            data_type.bind($('#question-'+question));
        });

        // Event handlers.

        $survey.find("input").change(function(evt, extra) {
            if (evt.target.nodeName !== "INPUT")
                return;

            var $input = $(evt.target);
            var $question = $(evt.target).closest(questionSelector);
            if (!$question.length)
                return true;
            var $option = $input.closest("li");
            var isRadio = $input.is(":radio");
            var isText = $input.is(":text");
            var isHidden = $input.is("[type=hidden]");
            var qid = parseInt($question.attr("id").replace("question-",""));
            var oid = parseInt(($option.attr("id") || '').replace("option-",""));
            var checked = false;
            // some checks are disabled on synthetized 'change' event
            var synthetic = extra && extra.synthetic;

            // If the <input> is a checkbox or radio button determine its checked state.

            if ($input.is(":radio,:checkbox")) {
                checked = $input.is(":checked");
                $question.find('.open-option-data').attr('disabled', function(){
                    return !$(this).closest('li').find(":radio,:checkbox").is(':checked');
                });
            }

            // Else check regular expressions for text entries

            else if ($input.attr('pattern')) {
                var pattern = new RegExp($input.attr('pattern'));
                checked = pattern.test($input.val());
                if (!synthetic)
                    $question.toggleClass("error", !checked);
            }

            // Else just use the string inside the text entry.

            else {
                checked = $input.val() !== "";
                if (!synthetic && $question.is('.mandatory'))
                    $question.toggleClass("error", !checked);
            }

            // Invoke all rules for the rule/option combination.

            var exclusives = [];
            var rules = rules_by_question[qid] || [];
            for (var i=0 ; i < rules.length ; i++) {
                var rule = rules[i];
                if (isRadio) {
                    // checking a radio button must apply rules associated with the uncheck of
                    // all other options
                    jQuery.each(rule.subjectOptions, function(i, o) {
                        var option = $question.find('#option-'+o+' :radio');
                        rule.apply($survey, option.is(':checked'));
                    });
                }
                else if (jQuery.inArray(oid, rule.subjectOptions) >= 0) {
                    // apply rules if the current option is in the subjectOptions set
                    rule.apply($survey, checked);
                }
                else if (isText || isHidden) {
                    // do not check options for text questions
                    rule.apply($survey, checked);
                }
                if (rule.isExclusive) {
                    exclusives = exclusives.concat(jQuery.map(rule.subjectOptions, function(i){ return '#option-'+i;}));
                }
            }

            if (checked && $.inArray('#option-'+oid, exclusives) >= 0) {
                // uncheck all other options when checking an exclusive one
                var extra = { synthetic: true };
                $question.find(':radio,:checkbox').not($input).filter(':checked').attr('checked', false).trigger('change', extra);
            }
            else if (checked && exclusives.length) {
                // uncheck all exclusives when checking a non-exclusive option
                var extra = { synthetic: true };
                $question.find(exclusives.join(',')).find(':radio,:checkbox').attr('checked', false).trigger('change', extra);
            }

            // Propagate changes to derived options

            if ($input.is(':not(.derived)')) {
                var val = $input.val();
                var derived = derived_values[qid] || [];
                for (var i=0 ; i < derived.length ; i++) {
                    var $derived_input = $question.find('#option-'+derived[i].option).find(':input');
                    var match = Boolean(derived[i].match(val));
                    var checked = $derived_input.is(':checked');
                    if (match != checked) {
                        var extra = { synthetic: true };
                        $derived_input.attr('checked', match).trigger('change', extra);
                    }
                }
            }
        });

        jQuery.each(rules_by_question, function(i, by_question) {
            jQuery.each(by_question, function(i, rule) {
                rule.init($survey, last_partecipation_data);
            });
        });

        // ensure that the initial status is consistent with rules and whatnot
        var extra = { synthetic: true };
        $survey.find(":input").trigger('change', extra);
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterRuntime = function(context, options) {
        return new PollsterRuntime(context, options);
    };

})(jQuery);

