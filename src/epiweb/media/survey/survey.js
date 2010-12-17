(function() {
var Survey = function(target, data) {
    this.target = target;
    this.modifier = data.modifier;
    this.modified = data.modified;
    this.profiles = data.profiles;
    this.responses = data.responses;
    this.conditions = data.conditions;
    this.questions = data.questions;
    this.prefills = data.prefills;
    this.prefill_target = {};
};
Survey.prototype = {
    init: function() {
        var self = this;
        var len = this.questions.length;
        this.fields = {};
        this.changed = {};
        this.parent_field = {};
        this.children_field = {};
        for (var i=0; i<len; i++) {
            var id = this.questions[i];
            var field = this.get_fields(id);
            this.fields[id] = field;
            this.changed[id] = false;
            field.change(function() {
                return self.on_change($(this));
            });
        }
        for (var i=0; i<len; i++) {
            var id = this.questions[i];
            this.update_visibility(id);
        }

        // mapping which question triggers prefill what question
        {
            var map = {};
            for (var id in this.prefills) {
                var cond = this.prefills[id];
                var items = this.get_affecting_questions(cond);
                for (var i=0; i<items.length; i++) {
                    var qid = items[i];
                    if (qid in map) {
                        map[qid].push(id);
                    }
                    else {
                        map[qid] = [id];
                    }
                }
            }
            this.prefill_target = map;
        }
    },
    get_fields: function(id) {
        var fields = this.target.find('*[name="'+id+'"]');
        if (fields.length == 0) {
            var question = this.target.find('#q_'+id);
            var items = question.find('*[name]');
            var len = items.length;
            fields = [];
            for (var i=0; i<len; i++) {
                var item = $(items[i]);
                var name = item.attr('name');
                if (name.match('^'+id+'_') != null) {
                    fields.push(item[0]);
                    this.parent_field[name] = id;
                    if (!(id in this.children_field)) {
                        this.children_field[id] = [];
                    }
                    this.children_field[id].push(item);
                }
            }
            fields = $(fields);
        }
        return fields;
    },
    on_change: function(target) {
        var name = target.attr('name');
        var id = this.parent_field[name];
        if (id == undefined) {
            id = name;
        }

        // set as changed
        this.changed[id] = true;

        // update visibility of other questions
        var modified = this.modified[id];
        if (modified != undefined) {
            var len = modified.length;
            for (var i=0; i<len; i++) {
                var mid = modified[i];
                this.update_visibility(mid);
            }
        }

        // update prefill
        var ids = this.prefill_target[id];
        if (ids != undefined) {
            for (var i=0; i<ids.length; i++) {
                this.update_prefill(ids[i]);
            }
        }

        return true;
    },
    update_visibility: function(id) {
        var cond = this.conditions[id];
        var sid = id + '__skip';
        if (cond == undefined) { return; }
        if (cond.evaluate(this)) {
            this.target.find('#'+sid).remove();
            $('#q_'+id).slideDown();
        }
        else {
            if (this.target.find('#'+sid).length == 0) {
                var sid = id + '__skip';
                var skip = $('<div class="skip" id="'+sid+'">skipped</div>');
                $('#q_'+id).after(skip);
            }
            $('#q_'+id).slideUp();
        }
    },
    update_prefill: function(id) {
        var field = this.fields[id];
        var current = field.fieldValue();
        if (!this.changed[id]) {
            var cond = this.prefills[id];
            if (cond.evaluate(this)) {
                // form value setting is not supported by jquery.form :(
                this.set_value(field, this.get_response(id));
            }
            else {
                this.set_value(field, []);
            }
        }
    },
    set_value: function(fields, values) {
        if (values == null) { return; }
        var len = fields.length;
        var first = fields[0];
        var tag = first.tagName.toLowerCase();
        var str_values = [];
        for (var i=0; i<values.length; i++) {
            str_values.push(""+values[i]);
        }
        if (tag == 'input') {
            var type = $(first).attr('type');
            if ((type == 'checkbox') || (type == 'radio')) {
                for (var i=0; i<len; i++) {
                    if ($.inArray(fields[i].value, str_values) >= 0) {
                        fields[i].checked = true;
                    }
                    else {
                        fields[i].checked = false;
                    }
                }
            }
            else if (type == 'text') {
                $(first).val(values[0]);
            }
        }
        else if (tag == 'select') {
            if (tag.attr('multiple')) {
                $(first).val(values);
            }
            else {
                $(first).val(values[0]);
            }
        }
        else {
            // unknown
        }
    },
    get_profile: function(id) {
        var value = this.profiles[id];
        if (!(value instanceof Array)) {
            value = [value];
        }
        value.sort();
        return value;
    },
    get_response: function(id) {
        var value = this.responses[id];
        if (value == null) { return null; }
        if (!(value instanceof Array)) {
            value = [value];
        }
        value.sort();
        return value;
    },
    get_question: function(id) {
        var field = this.fields[id];

        if (id in this.children_field) {
            var value = [];
            var fields = this.children_field[id];
            for (var i=0; i<fields.length; i++) {
                var f = $(fields[i]);
                var v = f.fieldValue();
                value.push(v);
            }
        }
        else {
            var value = field.fieldValue();
        }

        return value;
    },
    get_affecting_questions: function(condition) {
        var res = [];
        var stack = [];
        stack.push(condition);
        while (stack.length > 0) {
            var cond = stack.pop();
            if (!(typeof(cond) == "object")) {
                continue;
            }
            if ('args' in cond) {
                // another condition
                for (var i=0; i<cond.args.length; i++) {
                    stack.push(cond.args[i]);
                }
            }
            else if ('id' in cond) {
                // question, profile, or response
                res.push(cond.id);
            }
        }
        res = $.unique(res);
        return res;
    }
}

this.Survey = Survey;

var SurveyDefinition = {
    Profile: function(id) {
        var self = this;
        this.id = id;
        this.value = function(context) {
            return context.get_profile(self.id);
        }
    },
    Response: function(id) {
        var self = this;
        this.id = id;
        this.value = function(context) {
            return context.get_response(self.id);
        }
    },
    Question: function(id) {
        var self = this;
        this.id = id;
        this.value = function(context) {
            return context.get_question(self.id);
        }
    },
    Equal: function(a, b) {
        var self = this;
        this.a = a;
        this.b = b;
        this.args = [a, b];
        this.evaluate = function(context) {
            var a = self.a.value(context);
            var b = self.b;
            if (typeof(b) == "object") {
                b = b.value(context);
            }
            return (""+a) == (""+b);
        }
    },
    EqualIndex: function(a, index, b) {
        var self = this;
        this.a = a;
        this.index = index;
        this.b = b;
        this.args = [a, b];
        this.evaluate = function(context) {
            var a = self.a.value(context)[self.index];
            var b = self.b;
            if (typeof(b) == "object") {
                b = b.value(context);
            }
            return (""+a) == (""+b);
        }
    },
    Empty: function(a) {
        var self = this;
        this.a = a;
        this.args = [a];
        this.evaluate = function(context) {
            var a = self.a.value(context);
            return (a == null) || (a == undefined) || (a.length == 0);
        }
    },
    In: function(a, b) {
        var self = this;
        this.a = a;
        this.b = b;
        this.args = [a, b];
        this.evaluate = function(context) {
            var a = self.a.value(context);
            if (!(a instanceof Array)) {
                a = [a];
            }
            var len = a.length;
            var b = [];
            for (var i=0; i<self.b.length; i++) {
                b.push(""+self.b[i]);
            }
            for (var i=0; i<len; i++) {
                if ($.inArray(a[i], b) >= 0) {
                    return true;
                }
            }
            return false;
        }
    },
    And: function(args) {
        var self = this;
        this.args = args;
        this.evaluate = function(context) {
            var len = self.args.length;
            for (var i=0; i<len; i++) {
                var arg = self.args[i];
                if ((typeof(arg) == "boolean") && !arg) {
                    return false;
                }
                else if (!arg.evaluate(context)) {
                    return false;
                }
            }
            return true;
        }
    },
    Or: function(args) {
        var self = this;
        this.args = args;
        this.evaluate = function(context) {
            var len = self.args.length;
            for (var i=0; i<len; i++) {
                var arg = self.args[i];
                if ((typeof(arg) == "boolean") && arg) {
                    return true;
                }
                else if (arg.evaluate(context)) {
                    return true;
                }
            }
            return false;
        }
    },
    Not: function(a) {
        var self = this;
        this.a = a;
        this.args = [a];
        this.evaluate = function(context) {
            return !self.a.evaluate(context);
        }
    },
    BooleanTrue: function() {
        this.evaluate = function() {
            return true;
        }
    }
};
this.SurveyDefinition = SurveyDefinition;

var sd = SurveyDefinition;

var SurveyDefinitionGlue = {
    Profile: function(id) {
        return new sd.Profile(id);
    },
    Response: function(id) {
        return new sd.Response(id);
    },
    Question: function(id) {
        return new sd.Question(id);
    },
    Equal: function(a, b) {
        return new sd.Equal(a, b);
    },
    EqualIndex: function(a, i, b) {
        return new sd.EqualIndex(a, i, b);
    },
    Empty: function(a) {
        return new sd.Empty(a);
    },
    In: function(a, b) {
        return new sd.In(a, b);
    },
    Contains: function(a, b) {
        return new sd.Contains(a, b);
    },
    And: function() {
        return new sd.And(arguments);
    },
    Or: function() {
        return new sd.Or(arguments);
    },
    Not: function(a) {
        return new sd.Not(a);
    },
    BooleanTrue: function() {
        return new sd.BooleanTrue(arguments);
    }
}
this.SurveyDefinitionGlue = SurveyDefinitionGlue;

})();

$(document).ready(function() {
    $.datepicker.setDefaults({dateFormat: 'dd/mm/yy'});
    $('.sDateField').datepicker();
    $('.sDateField').each(function() {
        var dp = this;
        var button = '<img class="datepickerbutton" src="/+media/img/calendar.png"/>';
        $(this).after(button);
        $(this).next().click(function() {
            $(dp).datepicker('show');
        });
    });

    // scroll to the first question with error
    var err = $('div.question .errormsg').eq(0).parent();
    if (err.length > 0) {
        var top = err.position().top;
        window.scrollTo(0, top);
    }
});

