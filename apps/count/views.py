from django.contrib.auth.models import User
from django.template import Context, Template, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

def counter(request):

    count = User.objects.count()

    return HttpResponse(count)
