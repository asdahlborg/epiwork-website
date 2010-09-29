(function() {

// {{{
var Survey2 = function() {

}

Survey2.prototype = {
    prefix: "q_",
    id: {},
    ids: [],
    qtotal: 0,
    qcon: {}, // question condition
    set_questions: function(qids) {
        this.qids = qids;
        var len = qids.length;
        this.qtotal = len;
        for (var i=0; i<len; i++) {
            var qid = qids[i];
            var id = this.prefix + qid;
            this.id[qid] = id;
            this.ids.push(id);
            this.qcon[id] = undefined;
        }
    },
    init: function() {
        var len = this.qtotal;
        for (var i=0; i<len; i++) {
            var id = this.ids[i];
            if (this.qcon[id] != undefined) {
                $('#'+id).hide();
            }
        }
        this.toggle_all();
    },
    set_condition: function(qid, con) {
        var id = this.id[qid];
        this.qcon[id] = con;
    },
    trim: function(str) {
        // from http://blog.stevenlevithan.com/archives/faster-trim-javascript
        // License: MIT License (http://blog.stevenlevithan.com/archives/faster-trim-javascript#comment-13674)
        var	str = str.replace(/^\s\s*/, ''),
        	ws = /\s/,
        	i = str.length;
        while (ws.test(str.charAt(--i)));
        return str.slice(0, i + 1);
    },
    toggle: function(qid) {
        var visible = this.eval[qid]();
        console.log(qid, visible);
        if (visible) { $('#'+this.id[qid]).show(); }
        else { $('#'+this.id[qid]).hide(); }
    },
    toggle_all: function() {
        for (var i=0; i<this.qtotal; i++) {
            this.toggle(this.qids[i]);
        }
    },

    Q: function(qid) {
        var id = this.id[qid];
        return $('#'+id+' *[name="'+qid+'"]').fieldValue();
    },
    NotEmpty: function(values) { 
        var empty = false;
        var len = values.length;
        for (var i=0; i<len; i++) {
            empty |= this.trim(values[i]) == '';
        }
        return !empty && len != 0;
    },
    OneOf: function(values, options) {
        if (values.length == 0) { return false; }
        var value = values[0];
        var len = options.length;
        for (var i=0; i<len; i++) {
            if (options[i] == value) {
                return true;
            }
        }
        return false;
    },
}

// }}}

var Survey = function(id, prefix) {
    this.id = id;
    this.base = $('#'+id);
    this.prefix = prefix;
}

Survey.prototype = {
    affected: {},
    rule: {},

    qids: [],
    
    init: function() {
        var self = this;
        var len = this.qids.length;
        for (var i=0; i<len; i++) {
            var qid = this.qids[i];

            // onchange event
            this.base.find('*[name="'+qid+'"]').change(function(e) {
                var qid = $(e.target).attr('name');
                self.changed(qid);
            });

            // default visibility
            this.update_visibility(qid);

            // default values
            if (this.blank[qid] == undefined) {
                this.blank[qid] = false;
            }
            if (this.affected[qid] == undefined) {
                this.affected[qid] = new Array();
            }
        }
    },

    changed: function(qid) {
        var list = this.affected[qid];
        var len = list.length;
        for (var i=0; i<len; i++) {
            var qid = list[i];
            this.update_visibility(qid);
        }
    },

    update_visibility: function(qid) {
        var ev = this.rule[qid]();
        var target = this.base.find('#'+this.prefix+qid);
        var curr = target.css('display');
        if (ev && (curr == 'none')) { this.show(target); }
        else if (!ev && (curr == 'block')) { this.hide(target); }
    },

    show: function(target) {
        var id = target.attr('id');
        var sid = id+'__skip';
        var skip = this.base.find('#'+sid);
        skip.remove();
        target.slideDown();
    },
    hide: function(target) {
        var id = target.attr('id');
        var sid = id+'__skip';
        target.after('<div class="skip" id="'+sid+'">skipped</div>');
        target.slideUp();
    },

    _prepare: function(v) {
        var t = typeof v;
        if (!$.isArray(t)) {
            if ((t == 'number') || (t == 'string')) {
                return [v];
            }
        }
        return v;
    },

    get_invalids: function() {
        var len = this.qids.length;
        var res = [];
        for (var i=0; i<len; i++) {
            var qid = this.qids[i];
            var empty = this.Is(this.Value(qid), this.Empty());
            var visible = this.rule[qid]();
            var allow_blank = this.blank[qid];
            if (visible && empty && !allow_blank) {
                res.push(qid);
            }
        }
        return res;
    },
    validate: function() {
        return this.get_invalids().length == 0;
    },

    Empty: function() {
        return [];
    },
    Is: function(a, b) {
        a = this._prepare(a);
        b = this._prepare(b);
        var la = a.length;
        var lb = b.length;

        var ia = 0, ib = 0;
        while (true) {
            if (ia >= la) { break; }
            if (ib >= lb) { break; }
            
            var va = a[ia];
            var vb = b[ib];

            if (va != vb) { return false; }
            ia++; ib++;
        }

        return (la-ia) == (lb-ib);
    },
    IsNot: function(a, b) {
        return !this.Is(a, b);
    },
    IsIn: function(a, list) {
        a = this._prepare(a);    
        var len = a.length;
        var len2 = list.length;
        if ((len == 0) || (len2 == 0)) { return false; }
        for (var i=0; i<len; i++) {
            var val = a[i];
            var found = false;
            for (var j=0; j<len2; j++) {
                if (val == list[j]) { found = true; break; }
            }
            if (!found) { return false; }
        }

        return true;
    },                           
    Value: function(qid) {       
        var values = this.base.find('*[name="'+qid+'"]').fieldValue();
                             
        // strip out empty strings
        var len = values.length;
        var res = [];            
        for (var i=0; i<len; i++) {
            var value = values[i];
            if (typeof value == 'string') {
                value = $.trim(value);
                if (value != '') {
                    res.push(value);
                }
            }
            else {
                res.push(value);
            }
        }

        return res;
    },
    Profile: function(pid) {
        return this.profiles[pid];
    },
    Previous: function(pid) {
        return this.previous[pid];
    },
}

this.Survey = Survey;

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
    var id = $('div.question .errormsg').eq(0).parent().attr('id')
    if (id != undefined) {
        location.hash = '#' + id
    }

});

