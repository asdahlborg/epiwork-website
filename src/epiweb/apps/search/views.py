from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response

def index(request):
    return render_to_response('registration/index.html',
        context_instance=RequestContext(request))

