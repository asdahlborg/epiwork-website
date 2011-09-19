(function($) {

    // DEFAULT ACTION HANDLERS

    function onCreateQuestion(evt, designer, type) {
        var $tmpl = $(".wok-templates .template-question-" + type).children().clone();
        if ($tmpl.length === 1) {
            $tmpl.attr("id", "question-N" + designer.getNextTemporaryId());
            $tmpl.attr("data-question-type", type);
            $tmpl.find("li").attr("id", "option-N" + designer.getNextTemporaryId());
            designer.getTemplate().append(
                $('<div class="question-wrapper clearfix"></div>')
                    .append($tmpl)
                    .append('<div class="rules"></div>')
                );
            designer.validate();
        }
    }

    function onSave(evt, designer) {
        var sd = designer.getSurveyData();
        var isnew = !sd.id;
        var survey = $('<div></div>')
            .attr("id", "survey-" + sd.id)
            .append($("<h1></h1>").text(sd.title).attr('data-shortname', sd.shortname).attr('data-version', sd.version))
            .append(designer.getTemplate().find(".question-wrapper").clone());
        var xml = innerXHTML($('<div></div>').append(survey)[0]);
        $.post(designer.getPostUrl(sd.id), {surveyxml: xml}, function(responseText) {
            $(evt.target).removeAttr('disabled');
            if (isnew)
                window.location = designer.getSurveyUrl($(responseText).find(".survey").attr("id").replace("survey-", ""));
            else
                window.location.reload();
        }).error(function(jqXHR, textStatus, errorThrown) { wok.error("error on save: "+errorThrown); });
    }

    // DESIGNER WINDOW

    function PollsterDesigner(context, options) {
        context = context || document;
        options = $.extend({}, window.wok.pollster.options, options);

        var self = this;
        var $canvas = $(options.canvasSelector, context);
        var $tools = $(options.toolsSelector, context);
        var $properties = $(options.propertiesSelector, context);

        $(window).resize(function(evt){
            // show scrollbars if the floating panel is too tall for the current window
            $properties.css( {'max-height': window.innerHeight-5, 'overflow-y': 'auto'});
        }).resize();
        // enable panel scrolling
        $properties.portamento({
            wrapper: $properties.parent(),
            gap: 0
        });

        var $selection = null, $question = null;

        if (!window.pollster_urls)
            return window.wok.error("can't find URLs resolver");
        if ($canvas.length === 0)
            return window.wok.error("can't find canvas element: " + options.canvasSelector);
        if ($canvas.children('.'+options.templateClass).length === 0)
            $canvas.append($('<div></div>').addClass(options.templateClass));
        var $template = $canvas.children('.'+options.templateClass);

        // Question numbering.

        function renumberQuestions() {
            self.nextTemporaryId = $template.find(".question:not(.question-builtin)").each(function(i) {
                var $q = $(this);
                var $i = $q.children(".info");
                $i.text(self.getQuestionShortname($q));
            }).length + 1;
        }

        // Initialize all property providers (builtins and overrides).

        var providers = {};
        var providerClasses = $.extend({}, window.wok.pollster.propertyProviders, options.propertyProviders);
        $properties.find(".property-group").hide().each(function(i) {
            var $propertyGroup = $(this);
            var group = $.trim($propertyGroup.attr("class").replace("property-group", ""));
            var provider = providerClasses[group];
            if (provider)
                providers[group] = new provider(self, $propertyGroup);
        });

        function getPropertyProviders($target, level) {
            if ($target && $target.length > 0) {
                if ($target.is(".choices > li") && level === 0) {
                    return [providers["builtin-choice"]];
                }
                else if ($target.is(".columns > li") && level === 0) {
                    return [providers["builtin-column"]];
                }
                else if ($target.is(".rows > li") && level === 0) {
                    return [providers["builtin-row"]];
                }
                else if ($target.is(".derived-values > li") && level === 0) {
                    return [providers["builtin-derived-value"]];
                }
                else if ($target.is(".rule") && level === 0) {
                    // Some magic, we locate and bind the question, then we return the rule builtin.
                    providers["builtin-question"].attach($target.closest(".question-wrapper").children('.'+options.questionClass));
                    return [providers["builtin-rule"]];
                }
                else if ($target.hasClass("question") && level <= 1) {
                    return [providers["builtin-question"]];
                }
                else {
                    var provider = providers["tag-"+$target[0].tagName];
                    if (provider  && (!provider.nestingLevel || provider.nestingLevel <= level))
                        return [provider];
                }
            }

            return [];
        }

        function setupProperties($target) {
            var providers = getPropertyProviders($target, 0);
            if (providers.length > 0) {
                for (var i=0 ; i < providers.length ; i++) {
                    if (providers[i].setup)
                        providers[i].setup($target);
                }
            }
        }

        function togglePropertyGroups($target) {
            $properties.find(".property-group").hide();

            // We want to break both if we reach a nesting barrier and if we reach
            // the top of the page, so we keep a running count of the nesting level
            // to pass to getPropertyProviders().

            var level = 0;

            while ($target !== null && $target.length > 0) {
                var providers = getPropertyProviders($target, level);
                if (providers.length > 0) {
                    for (var i=0 ; i < providers.length ; i++)
                        providers[i].attach($target);
                    level += 1;
                }

                if ($target.hasClass("question-wrapper"))
                    break;

                $target = $target.parent();
            }
        }

        // Event handlers.


        function onMouseDown(evt) {
            var $s = $(evt.target);
            if ($selection !== null) {
                if ($selection[0] !== $s[0]) {
                    $selection.removeClass("selected");
                    $selection.closest(".question-wrapper").removeClass("active");
                }
            }

            // Check to make sure we clicked on a valid question/field.

            $question = $s.closest(".question-wrapper").addClass("active");

            if ($question.length !== 0) {
                $selection = $s.addClass("selected");
            }
            else {
                $selection = $question = null;
            }

            togglePropertyGroups($selection);
        }

        $canvas.bind("mousedown.art", onMouseDown);

        $(".action-save").click(function(evt) {
            $(this).attr('disabled', true);
            (options.onSave || onSave)(evt, self);
            return false;
        })

        $(".action-create-question").click(function(evt) {
            var type = $(this).siblings("select").val();
            self.createQuestion(type);
            return false;
        });

        $(".sortable > *").hoverIntent(
            function() {
                var $tmpl = $(".wok-templates .sort-buttons").clone();
                $(this).append($tmpl);
            },
            function() {
                $(this).find('.sort-buttons').remove();
            }
        );

        $(".sortable .sort-buttons .up").live("click", function(){
            var $item = $(this).closest('.sortable > *');
            var $prev = $item.prev();
            if ($prev.length) {
                $item[0].parentNode.insertBefore($item[0], $prev[0]);
                $item.mouseleave();
            }
            return false;
        });

        $(".sortable .sort-buttons .down").live("click", function(){
            var $item = $(this).closest('.sortable > *');
            var $next = $item.next();
            if ($next.length) {
                $item[0].parentNode.insertBefore($next[0], $item[0]);
                $item.mouseleave();
            }
            return false;
        });

        // Public methods.

        $.extend(this, {
            getTemplate: function() {
                return $template;
            },

            getSurveyData: function() {
                return {
                    id: $properties.find("[name='survey-id']").val(),
                    title: $properties.find("[name='survey-title']").val(),
                    shortname: $properties.find("[name='survey-shortname']").val(),
                    version: $properties.find("[name='survey-version']").val()
                };
            },

            getNextTemporaryId: function() {
                var id = self.nextTemporaryId;
                self.nextTemporaryId += 1;
                return id;
            },

            getQuestionShortname: function($element) {
                var dn = $element.find(".data-name").text();
                if (dn == "??")
                    return '';
                return dn;
            },

            getSurveyUrl: function(surveyId) {
                if (surveyId)
                    return pollster_urls.url('pollster_survey_edit', {id: surveyId});
            },

            getPostUrl: function(surveyId) {
                if (surveyId)
                    return pollster_urls.url('pollster_survey_edit', {id: surveyId});
                else
                    return pollster_urls.url('pollster_survey_add');
            },

            validate: function() {
                renumberQuestions();
            },

            createQuestion: function(type) {
                (options.onCreateQuestion || onCreateQuestion)(null, this, type);
            }
        });

        // Question initialization.

        renumberQuestions();
        $template.disableSelection();
        $template.sortable({
            stop: function(evt, ui) { renumberQuestions(); }
        });

        $canvas.find(".question .derived-values li, .rule").each(function() {
            setupProperties($(this));
        });
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterDesigner = function(context, options) {
        return new PollsterDesigner(context, options);
    };

})(jQuery);

