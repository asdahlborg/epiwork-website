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

        function group_zip_by_color(data) {
            var ccol = get_column_index(data.dataTable.cols, "color");
            if (ccol === -1)
                ccol = get_column_index(data.dataTable.cols, "colour");
            var czip = get_column_index(data.dataTable.cols, "zip");

            var rows = data.dataTable.rows;
            var zips = {};
            var zips_by_color = {};
            for (var i=0, rl=rows.length ; i < rl ; i++) {
                var k = rows[i].c[ccol].v;
                var l = zips_by_color[k] || null;
                if (l === null)
                    zips_by_color[k] = l = [];
                var zip = rows[i].c[czip].v.toString();
                l.push("'"+zip+"'");
                zips[zip] = rows[i];
            }

            var all = [];
            var result = {};
            for (var k in zips_by_color) {
                var s = zips_by_color[k].join(",");
                all.push(s);
                result[k] = "(" + s + ")";
            }

            return [result, "(" + all.join(",") + ")", zips];
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
            getData(function(data) {
                // Group ZIP codes by color and create appropriate styles.
                var zbc = group_zip_by_color(data);
                var styles = []
                for (var k in zbc[0]) {
                    styles.push({
                        where: "zip_code IN " + zbc[0][k],
                        polygonOptions: {
                            fillColor: k,
                            strokeColor: k,
                            strokeWeight: "1"
                        }
                    });
                }

                // Create map and overlay layer with georeferenced zip codes.

                var opts = {
                  zoom: 8,
                  center: new google.maps.LatLng(45, 7.7),
                  mapTypeId: google.maps.MapTypeId.TERRAIN
                };

                var map = new google.maps.Map(self.$container[0], opts);

                var layer = new google.maps.FusionTablesLayer({
                    map: map,
                    styles: styles,
                    suppressInfoWindows : true,
                    query: {
                        select: 'geometry',
                        from: '1474927',
                        where: "zip_code IN " + zbc[1]
                    },
                });

                google.maps.event.addListener(layer, 'click', function(evt) {
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
        else if (self.$container.data("chart-type") === "google-fusion-map")
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
