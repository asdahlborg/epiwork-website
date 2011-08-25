from django.conf import settings
from django import http
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django import forms

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")

    Django's standard 500 error handler does not serve MEDIA_URL correctly; this one does
    """
    t = loader.get_template(template_name)
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL
    })))

def test_search(request):
    class SearchForm(forms.Form):
        q = forms.CharField(label="Search")

    query = 'highlighted'
    page = {
        'object_list': [
            {'object': "Resultaat nr. 1", 'get_stored_fields': {'summary': 'this word is highlighted in some way'}},
            {'object': "Resultaat nr. 2", 'get_stored_fields': {'summary': 'this word is highlighted in some way'}},
            {'object': "Resultaat nr. 3", 'get_stored_fields': {'summary': 'this word is highlighted in some way'}},
        ],
        'previous_page_number': 1,
        'next_page_number': 3,
        'has_next': True,
        'has_previous': True,
    }
    form = SearchForm()
    return render_to_response('search/search.html', locals(), context_instance=RequestContext(request))
