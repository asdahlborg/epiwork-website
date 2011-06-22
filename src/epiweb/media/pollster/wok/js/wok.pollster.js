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

        console.log('PollsterRuntime', context, options, self, $survey, questionSelector);

        pollster_fill_rules(rules_by_question);
        //pollster_fill_derived_values(derived_values);

        // Event handlers.

        console.log('rules_by_question', rules_by_question);

        $survey.find("input").change(function(evt) {
            console.log(evt.target, evt.target.nodeName);

            if (evt.target.nodeName !== "INPUT")
                return;

            var $input = $(evt.target);
            var $question = $(evt.target).closest(questionSelector);
            var isRadio = $input.is("[type=radio]");
            var qid = parseInt($question.attr("id").replace("question-",""));
            var oid = parseInt($input.closest("li").attr("id").replace("option-",""));
            var checked = false;

            // If the <input> is a checkbox or radio button determine its checked state.

            if ($input.is("[type=radio],[type=checkbox]")) {
                checked = $input.is(":checked");
            }

            // Else use a derived value or just the string inside the text entry.

            else {
                checked = $input.val() !== "";
            }

            console.log(qid, oid, checked);

            // Invoke all rules for the rule/option combination.

            var rules = rules_by_question[qid];
            if (rules && rules.length > 0) {
                for (var i=0 ; i < rules.length ; i++) {
                    if (rules[i].target === oid)
                        rules[i].apply($survey, checked);
                    else if (isRadio)
                        rules[i].apply($survey, false);
                }
            }
        });
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterRuntime = function(context, options) {
        return new PollsterRuntime(context, options);
    };

})(jQuery);

