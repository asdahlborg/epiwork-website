from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import SurveyChartPlugin
from .utils import get_user_profile
from django.utils.translation import ugettext as _

class CMSSurveyChartPlugin(CMSPluginBase):
    model = SurveyChartPlugin
    name = _("Survey Chart")
    render_template = "pollster/cms_survey_chart.html"

    def render(self, context, instance, placeholder):
        request = context['request']
        global_id = request.GET.get('gid', None)
        profile = None
        if global_id:
            profile = get_user_profile(request.user.id, global_id)
        context.update({
            'profile': profile,
            'chart': instance.chart,
            'object': instance,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(CMSSurveyChartPlugin)
