window.pollster_urls = window.pollster_urls || {
    url: function(name, kwargs) {
        var ret = pollster_urls.urls[name];
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
