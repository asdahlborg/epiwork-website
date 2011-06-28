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

        var rules_by_question = {}, derived_values = {};

        pollster_fill_rules(rules_by_question);
        //pollster_fill_derived_values(derived_values);

        // Event handlers.

        $survey.find("input").change(function(evt) {
            if (evt.target.nodeName !== "INPUT")
                return;

            var $input = $(evt.target);
            var $question = $(evt.target).closest(questionSelector);
            var isRadio = $input.is(":radio");
            var qid = parseInt($question.attr("id").replace("question-",""));
            var oid = parseInt($input.closest("li").attr("id").replace("option-",""));
            var checked = false;

            // If the <input> is a checkbox or radio button determine its checked state.

            if ($input.is(":radio,:checkbox")) {
                checked = $input.is(":checked");
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
                if (rule.subject === oid)
                    rule.apply($survey, checked);
                else if (isRadio)
                    rule.apply($survey, false);
                if (rule.isExclusive)
                    exclusives.push('#option-'+rule.subject);
            }

            if (checked && $.inArray('#option-'+oid, exclusives) >= 0) {
                // uncheck all other options when checking an exclusive one
                $question.find(':radio,:checkbox').not($input).filter(':checked').attr('checked', false).change();
            }
            else if (checked && exclusives) {
                // uncheck all exclusives when checking a non-exclusive option
                $question.find(exclusives.join(',')).find(':radio,:checkbox').attr('checked', false).change();
            }
        });
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterRuntime = function(context, options) {
        return new PollsterRuntime(context, options);
    };

})(jQuery);

