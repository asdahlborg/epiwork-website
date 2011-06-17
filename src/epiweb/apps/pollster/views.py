# -*- coding: utf-8 -*-

from django.http import Http404
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    raise Http404()
