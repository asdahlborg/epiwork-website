google.load('visualization', '1', {'packages':['annotatedtimeline']});
google.setOnLoadCallback(drawChart);
var chart;

function inArray(myvalue, myarray) {
    for (var i=0; i<myarray.length; i++) {
        if (myarray[i] == myvalue) {
            return true;
        }
    }
    return false;
} 

function drawChart() {
    if (chart != undefined) {
         return;
    }
    id = document.getElementById('chart_div');
    if (id.offsetWidth == 0) {
         return;
    }

    chart = new google.visualization.AnnotatedTimeLine(
        document.getElementById('chart_div'));

    data = get_data();
    
    chart.draw(data, {
        allowRedraw: true
        ,min:0
        ,displayRangeSelector: true
        ,allValuesSuffix: ""
        ,displayExactValues: true
        ,displayZoomButtons: false
        ,scaleType: "allfixed"
        });
    filter();
}

function filter(myform) {
    drawChart();
    countryobj = document.getElementsByName("country");
    sourceobj = document.getElementsByName("source");

    // status = document.getElementById("status");
    // status.innerHTML = "";

    var countries = [];
    var sources = [];
    for (i=0; i<countryobj.length; i++) {
        if (countryobj[i].checked) {
            countries.push(countryobj[i].value);
        }
    }
    for (i=0; i<sourceobj.length; i++) {
        if (sourceobj[i].checked) {
            sources.push(sourceobj[i].value);
        }
    }

    if (countries.length > 1 && sources.length > 1) {
        alert("You cannot select multiple countries and sources. The Netherlands has been selected")
        for (i=0; i<countryobj.length; i++) {
            if (i==0) {
                countryobj[i].checked = true;
            }
            else {
                countryobj[i].checked = false;
            }
        }
        countries = ["nl"];
    }

    columns = get_columns();

    var shows = []
    var hides = []
    for (var column=0; column<columns.length; column++) {
        country = columns[column][0];
        source = columns[column][1];
        if (inArray(country, countries) && inArray(source, sources)) {
            shows.push(column);
        }
        else {
            hides.push(column);
        }
    }

    if (sources.length > 1) {
        range = chart.getVisibleChartRange()
        chart.draw(data, {
            allowRedraw: true
            ,min:0
            ,displayRangeSelector: true
            ,allValuesSuffix: ""
            ,displayExactValues: true
            ,displayZoomButtons: false
            ,scaleType: "allfixed"
            ,scaleColumns: shows
            });
        chart.setVisibleChartRange(range.start, range.end);
    }

    chart.showDataColumns(shows);
    chart.showDataColumns(shows);
    chart.hideDataColumns(hides)
}
