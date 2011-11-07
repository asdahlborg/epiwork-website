(function($) {
    window.wok.pollster.charts = {}

    function PollsterChart(container) {
        var self = this;
        self.$container = $(container);

        if (self.$container.length === 0)
            return wok.error("unable to get chart container element");

        var url = self.$container.attr('data-chart-url');
        if (!url)
            return wok.error("missing data-chart-url attribute on chart container");

        function getData(callback) {
            var params = {};
            var m = /gid=([a-z0-9-]+)/.exec(window.location.href);
            if (m && m[1])
                params = {"gid":m[1]};
            $.getJSON(url, params, function(data, textStatus, jqXHR) {
                callback(data);
            });
        }

        function draw_chart(url, containerId) {
            getData(function(data){
                var id = self.$container.attr('id');
                if (!id)
                    return wok.error("chart container element must have an id");
                data.containerId = id;
                self.wrapper = new google.visualization.ChartWrapper(data);
                self.wrapper.draw();
            });
        }

        function draw_map(url, containerId, center) {
            var jsonInput = $("#id_chartwrapper");
            var tileBase = url.replace(".json", "");

            getData(function(data) {
                var zipMapType = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return tileBase + "/tile/" +  zoom + "/" + coord.x + "/" + coord.y;
                    },
                    tileSize: new google.maps.Size(256, 256)
                });

                var c = new google.maps.LatLng(0, 0);
                var z = 1;
                var mapTypeId = google.maps.MapTypeId.TERRAIN;
                if (data && data.bounds && data.bounds.lat && data.bounds.lng) {
                    c = new google.maps.LatLng(data.bounds.lat, data.bounds.lng);
                    z = data.bounds.z;
                }
                if (data && data.center && center) {
                    c = new google.maps.LatLng(data.center.lat, data.center.lng);
                    if (data && data.bounds)
                        z = data.bounds.z;
                    else
                        z = 12;
                }
                if (data && data.bounds && data.bounds.mapTypeId) {
                    mapTypeId = data.bounds.mapTypeId;
                }

                var map = new google.maps.Map(self.$container[0], {
                    zoom: z,
                    center: c,
                    mapTypeId: mapTypeId
                });
                map.overlayMapTypes.insertAt(0, zipMapType);

                google.maps.event.addListener(map, 'click', function(evt) {
                    $.getJSON(tileBase+"/click/" + evt.latLng.lat() + "/" + evt.latLng.lng(), function(json) {
                        if (!json.zip_code_key)
                            return;
                        var html = '<div><strong>'+json.zip_code_key+'</strong><br/>';
                        for (var k in json) {
                            if (k !== "zip_code_key")
                                html += '<span>' + k + ': </span>' + json[k] + '<br/>';
                        }
                        html += '</div>';
                        var info = new google.maps.InfoWindow({
                            content: html,
                            position: evt.latLng
                        });
                        info.open(map);
                    });
                });

                if (jsonInput.length === 1) {
                    function update() {
                        var c = map.getBounds().getCenter();
                        var z = map.getZoom();
                        var mapTypeId = map.getMapTypeId();
                        var s = '{"z":'+z+',"lat":'+c.lat()+',"lng":'+c.lng()+',"mapTypeId":"'+mapTypeId+'"}';
                        jsonInput.val(s);
                    }
                    google.maps.event.addListener(map, 'bounds_changed', update);
                    google.maps.event.addListener(map, 'maptypeid_changed', update);
                }
            });
        }

        function openEditor(jsonTargetId) {
            self.editor = new google.visualization.ChartEditor();
            google.visualization.events.addListener(self.editor, 'ok', function() { 
                self.wrapper = self.editor.getChartWrapper();  
                self.wrapper.draw(self.$container.get(0));
                if (jsonTargetId) {
                    var json = self.wrapper.toJSON();
                    $('#'+jsonTargetId).val(json);
                }
            }); 
            self.editor.openDialog(self.wrapper);
        }

        // Public methods.

        $.extend(this, {
            openEditor: openEditor
        });

        if (self.$container.data("chart-type") === "google-charts")
            draw_chart(url, self.$container);
        else if (self.$container.data("chart-type") === "google-map")
            draw_map(url, self.$container, false);
        else if (self.$container.data("chart-type") === "google-map-centered")
            draw_map(url, self.$container, true);
    }

    window.wok.pollster.charts.init = function(callback) {
        google.load('visualization', '1.0', {packages: ['charteditor']});
        google.setOnLoadCallback(callback);
    };

    window.wok.pollster.charts.createCharts = function(selection) {
        $(selection).each(function() {
            var chart = new PollsterChart(this);
            $(this).data('pollster-chart', chart);
        });
    };

    window.wok.pollster.charts.activateChartEditor = function(selection) {
        $(selection).click(function(evt) {
            var id = $(this).attr('data-chart-id');
            var chart = $('#'+id).data('pollster-chart');
            var jsonTargetId = $(this).attr('data-json-target-id');
            chart.openEditor(jsonTargetId); 
            return false;
        });
    };

})(jQuery);
