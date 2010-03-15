(function() {
var InfluenzaNetBar = function(id) {
    this.id = id;
    this.target = $('#'+id);
}
InfluenzaNetBar.prototype = {
    init: function() {
        var self = this;
        $(document).ready(function() {
            self._init_bar();
        });
    },
    _init_bar: function() {
        var self = this;
        var html = '';
        html += '<div id="inetbar"><div id="inetbarheader">';
        html += '<p><span class="logo"><img src="/+media-ggm/inetbar/influenzanet_top_logo.gif"/></span>';
        html += '<span class="label">Influenzanet is a system to monitor the activity of influenza-like-illness (ILI) with';
        html += 'the aid of volunteers via the internet</span></p></div>';
        html += '<div id="inetbarcontent" style="display:none">';
        html += '<div id="inetbarleft"><p><a href="http://www.epiwork.eu/"><img src="http://www.degrotegriepmeting.nl/images/design_extra/epiwork_logo.jpg"/></a></p>';
        html += '<p>Developing the framework for an epidemic forecast infrastructure.</p>';
        html += '<p><a href="http://www.epiwork.eu/">http://www.epiwork.eu/</a></p>';
        html += '<p><img src="http://www.degrotegriepmeting.nl/images/design_extra/seventh_framework_logo.jpg"/></p>';
        html += '<p>The Seventh Framework Programme (FP7) bundles all research-related EU initiatives.</p></div>';
        html += '<div id="inetbarright"><p>Participating countries and volunteers:</p><ul>';
        html += '<li><a href="http://www.degrotegriepmeting.nl/"><img src="http://www.degrotegriepmeting.nl/images/country_flags/nl.gif"/></a> 20947</li>';
        html += '<li><a href="http://www.degrotegriepmeting.nl/"><img src="http://www.degrotegriepmeting.nl/images/country_flags/be.gif"/></a> 5843</li>';
        html += '<li><a href="http://www.degrotegriepmeting.nl/images/country_flags/pt.gif"><img src="http://www.degrotegriepmeting.nl/images/country_flags/pt.gif"/></a> 5481</li>';
        html += '<li><a href="http://www.influweb.it/index.php"><img src="http://www.degrotegriepmeting.nl/images/country_flags/vlag_italie.gif"/></a> 3022</li>';
        html += '<li><a href="http://www.degrotegriepmeting.nl/images/country_flags/mexicokl.jpg"><img src="http://www.degrotegriepmeting.nl/images/country_flags/mexicokl.jpg"/></a> 3950</li>';
        html += '<li><a href="http://www.gripenet.com.br/"><img src="http://www.degrotegriepmeting.nl/images/country_flags/brazilkl.jpg"/></a> 370</li>';
        html += '<li><a href="http://www.flusurvey.org.uk/"><img src="http://www.degrotegriepmeting.nl/images/country_flags/uk_kl.jpg"/></a> 5555</li>';
        html += '<li><a href="http://www.flutracking.net/"><img src="http://www.degrotegriepmeting.nl/images/country_flags/australia_kl.jpg"/></a> 7776</li>';
        html += '</ul></div>';
        html += '<div id="inetbarmain"><p>InfluenzaNet is a system to monitor the activity of influenza-like-illness (ILI) with the aid of volunteers via the internet. It has been operational in The Netherlands and Belgium (since 2003), Portugal (since 2005) and Italy (since 2008), and the current objective is to implement InfluenzaNet in more European countries. In contrast with the traditional system of sentinel networks of mainly primary care physicians coordinated by the European Influenza Surveillance Scheme (EISS), InfluenzaNet obtains its data directly from the population. This creates a fast and flexible monitoring system whose uniformity allows for direct comparison of ILI rates between countries.</p>'; 
        html += '<p>Any resident of a country where InfluenzaNet is implemented can participate by completing an online application form, which contains various medical, geographic and behavioural questions. Participants are reminded weekly to report any symptoms they have experienced since their last visit. The incidence of ILI is determined on the basis of a uniform case definition.</p></div>';
        html += '<br style="clear:both"/></div></div>';
        this.target.html(html);
        this.panel = this.target.find('#inetbarcontent');
        this.target.find('#inetbar .logo img').click(function() {
            self._toggle();
        });
    },
    _toggle: function() {
        if (this.panel.css('display') == 'none') {
            this.panel.slideDown();
        }
        else {
            this.panel.slideUp();
        }
    }
}
this.InfluenzaNetBar = InfluenzaNetBar;
})();
