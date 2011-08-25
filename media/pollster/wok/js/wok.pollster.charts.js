(function($) {
    window.wok.pollster.charts = {}

    function PollsterChart(container) {
        var self = this;
        self.$container = $(container);

        if (self.$container.length === 0)
            return wok.error("unable to get chart container element");

        var url = self.$container.attr('data-chart-url');
        if (!url)
            return wok.error("missing data-chart-ref attribute on chart container");

        function getData(callback) {
            $.getJSON(url, {}, function(data, textStatus, jqXHR) {
                callback(data);
            });
        }

        // On "OK" save the chart to a <div> on the page.
        function draw(url, containerId, callback) {
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
        };

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

        draw(url, self.$container); 
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
