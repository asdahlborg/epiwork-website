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

        var data_types = {}, rules_by_question = {}, derived_values = {};

        pollster_fill_data_types(data_types);
        pollster_fill_rules(rules_by_question);
        pollster_fill_derived_values(derived_values);

        $survey.find('.open_option_data').attr('disabled', true);

        // Bind data types to question elements

        $.each(data_types, function(question, data_type) {
            data_type.bind($('#question-'+question));
        });

        // Event handlers.

        $survey.find("input").change(function(evt) {
            if (evt.target.nodeName !== "INPUT")
                return;

            var $input = $(evt.target);
            var $question = $(evt.target).closest(questionSelector);
            var $option = $input.closest("li");
            var isRadio = $input.is(":radio");
            var qid = parseInt($question.attr("id").replace("question-",""));
            var oid = parseInt(($option.attr("id") || '').replace("option-",""));
            var checked = false;

            // If the <input> is a checkbox or radio button determine its checked state.

            if ($input.is(":radio,:checkbox")) {
                checked = $input.is(":checked");
                $question.find('.open_option_data').attr('disabled', true);
                $option.find('.open_option_data').attr('disabled', !checked);
            }

            // Else check regular expressions for text entries

            else if ($input.attr('pattern')) {
                var pattern = new RegExp($input.attr('pattern'));
                checked = pattern.test($input.val());
                $question.toggleClass("error", !checked);
            }

            // Else use a derived value or just the string inside the text entry.

            else {
                checked = $input.val() !== "";
            }

            // Invoke all rules for the rule/option combination.

            var exclusives = [];
            var rules = rules_by_question[qid] || [];
            for (var i=0 ; i < rules.length ; i++) {
                var rule = rules[i];
                if (jQuery.inArray(oid, rule.subject) >= 0)
                    rule.apply($survey, checked);
                else if (isRadio)
                    rule.apply($survey, false);
                if (rule.isExclusive)
                    exclusives.push('#option-'+oid);
            }

            if (checked && $.inArray('#option-'+oid, exclusives) >= 0) {
                // uncheck all other options when checking an exclusive one
                $question.find(':radio,:checkbox').not($input).filter(':checked').attr('checked', false).change();
            }
            else if (checked && exclusives) {
                // uncheck all exclusives when checking a non-exclusive option
                $question.find(exclusives.join(',')).find(':radio,:checkbox').attr('checked', false).change();
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
                        $derived_input.attr('checked', match).change();
                    }
                }
            }
        });
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterRuntime = function(context, options) {
        return new PollsterRuntime(context, options);
    };

})(jQuery);

