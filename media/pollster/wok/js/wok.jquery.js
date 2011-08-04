// WOK - the Web Objects Kitchen
//
//   Copyright © 2009-2010 Studio Associato Di Nunzio e Di Gregorio
//
//   Authors:
//     Federico Di Gregorio
//     Pierluigi Di Nunzio
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public Licenseas published by
// the Free Software Foundation, either version 3 of the License, or (at
// your option) any later version. See the file Documentation/GPL3 in the
// original distribution for details. There is ABSOLUTELY NO warranty.

(function($) { // MODULE: wok.jquery

$.fn.placeholder = function(cbCheck) {
    return this.each(function(i) {
        var $label, $elt = $(this);
        var pos = $elt.position(), title = $elt.attr("title");
        var isCustom = $.isFunction(cbCheck);
        if (title) {
            $label = $("<label>" + $elt.attr("title") + "</label>")
                .css({position: "absolute", top: pos.top, left: pos.left})
                .addClass("wok-placeholder ui-state-disabled")
                .insertAfter($elt)
                .click(function(evt) { isCustom ? $elt.trigger("click") : $elt.trigger("focus") });
        }
        if ($label) {
            if (isCustom) {
                $elt.focus(function(evt) { $label.hide() })
                    .blur(function(evt) { cbCheck.call($elt, "blur") ? $label.hide() : $label.show() })
                    .trigger("blur");
            }
            else {
                $elt.val($.trim($elt.val()))
                    .focus(function(evt) { $label.hide() })
                    .blur(function(evt) {
                        $elt.val() ? $label.hide() : $label.show();
                    })
                    .trigger("blur");
            }
        }
    });
};

$.fn.ellipsize = function(height, options) {
    return this.each(function(i) {
        options = $.extend({ellipsis:"…"}, options);
        var ellipsis = options.ellipsis;
        var $this = $(this);
        var $target = $this.children().last();
        if ($target.length == 0)
            $target = $this;
        if ($target != $this && $this.css('overflow') === "hidden") {
            height = $this.height();
            $this = $this.wrapInner('<div></div>').children();
        }
        var i = 0;
        while ($this.height() > height && i != -1) {
            var text = $target.text();
            i = text.lastIndexOf(' ');
            if (i >= 0)
                $target.text(text.substring(0, i) + ellipsis);
        }
    });
}

$.fn.replaceClass = function(cls1, cls2) {
    return this.each(function(i) {
        $(this).removeClass(cls1).addClass(cls2);
    });
};

$.fn.extractArgs = function(data, optionalPattern) {
    if (typeof(data) === "string") {
        optionalPattern = data;
        data = {};
    }
    data = data || {};
    if (this.length > 0) {
        var pattern = optionalPattern ? optionalPattern : "[\\w_-]+";
        var attr = $(this[0]).attr("class");
        var r = new RegExp("ref-("+pattern+")-([\\d\\w_:-]+)", 'g');
        var m = r.exec(attr);
        while (m) {
            data[m[1]] = m[2];
            m = r.exec(attr);
        }
    }
    return data;
};

$.fn.extractId = function(data, optionalPattern) {
    if (typeof(data) === "string") {
        optionalPattern = data;
        data = null;
    }
    if (this.length > 0) {
        var pattern = optionalPattern ? optionalPattern : "[\\w_-]+";
        var r = new RegExp("("+pattern+")-([\\d\\w_:-]+)");
        var attr = $(this[0]).attr("id");
        if (!attr)
             attr = $(this[0]).attr("class");
        var m = r.exec(attr);
        if (m) {
            data = data || {};
            data.type = m[1];
            data.id = m[2];
            data.selector = "#"+m[1]+"-"+m[2]
        }
    }
    return data || null;
};

$.subclass = function(name, superClass, moduleFunction, initFunction) {
    initFunction.prototype = $.extend({}, superClass.prototype, initFunction.prototype, moduleFunction());
    initFunction.prototype.constructor = initFunction;
    initFunction.prototype.constructor.name = name;
    return initFunction;
}

})(jQuery);
