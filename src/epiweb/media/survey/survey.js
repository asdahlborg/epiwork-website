(function() {

var Survey = function() {

}

Survey.prototype = {
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

this.Survey = Survey;

})();

