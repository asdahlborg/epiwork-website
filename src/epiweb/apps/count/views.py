from django.contrib.auth.models import User
from django.template import Context, Template, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
import urllib

def counter(request):

    count = User.objects.count()

    return HttpResponse(count)

def list(request):

    it = urllib.urlopen("http://www.influweb.it/count/counter")
    it_c = it.read()
    
    pt = urllib.urlopen("http://www.gripenet.pt/cgear/pt.php")
    pt_c = pt.read()

    return render_to_response('count/list.html', {
        "it_c": it_c,
        "pt_c": pt_c
        },
         context_instance=RequestContext(request))
