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
            $.getJSON(url, {}, function(data, textStatus, jqXHR) {
                callback(data);
            });
        }

        function get_column_index(cols, id) {
            var index = -1;
            for (var i=0 ; i < cols.length ; i++) {
                if (cols[i].id === id)
                    index = i;
            }

            if (index === -1)
                return wok.error("can't find '" + id + "' column");
            else
                return index;
        }

        // On "OK" save the chart to a <div> on the page.

        function draw_chart(url, containerId, callback) {
            getData(function(data){
                var id = self.$container.attr('id');
                if (!id)
                    return wok.error("chart container element must have an id");
                data.containerId = id;
                self.wrapper = new google.visualization.ChartWrapper(data);
                if (callback)
                    callback(self.wrapper);
                self.wrapper.draw();
            });
        }

        function draw_map(url, containerId, callback) {
            var tileBase = url.replace(".json", "");

            getData(function(data) {
                var zipMapType = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return tileBase + "/tile/" +  zoom + "/" + coord.x + "/" + coord.y;
                    },
                    tileSize: new google.maps.Size(256, 256)
                });

                var map = new google.maps.Map(self.$container[0], {
                    zoom: 8,
                    center: new google.maps.LatLng(45, 7.7),
                    mapTypeId: google.maps.MapTypeId.TERRAIN
                });
                map.overlayMapTypes.insertAt(0, zipMapType);


                /* google.maps.event.addListener(layer, 'click', function(evt) {
                    var d = zbc[2][evt.row.zip_code.value];
                    var cols = data.dataTable.cols;
                    var html = '<div><strong>'+evt.row.zip_code.value+'</strong><br/>';
                    for (var i=0 ; i < cols.length ; i++) {
                        if (cols[i].id != "zip" && cols[i].id != "color" && cols[i].id != "colour") {
                            html += '<span>' + cols[i].label + ': </span>' + d.c[i].v + '<br/>';
                        }
                    }
                    html += '</div>';

                    var info = new google.maps.InfoWindow({
                        content: html,
                        position: evt.latLng
                    });
                    info.open(map);
                });
                */
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
            draw_map(url, self.$container);
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
