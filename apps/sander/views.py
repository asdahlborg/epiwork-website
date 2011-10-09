from urllib import urlencode
from urllib2 import urlopen

from django.shortcuts import render
from django.http import HttpResponse, Http404

from cms.utils.html import clean_html

def index(request):
    url = "http://results.influenzanet.info/results.php?" + urlencode(request.GET)
    content = urlopen(url).read()
    #content = clean_html(content, full=False)
    return render(request, 'sander/sander.html' , locals())
    
