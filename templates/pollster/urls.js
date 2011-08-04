window.urls = window.urls || {
    url: function(name, kwargs) {
        var ret = urls.urls[name];
        for( name in kwargs) {
            ret = ret.replace("{"+name+"}", kwargs[name]);
        }
        return ret;
    },

    urls: {
        {% for name, url in urls.items %}'{{name}}': '{{url}}',
        {% endfor %}
        '':''
    }
}
