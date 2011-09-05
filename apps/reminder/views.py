from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from .models import UserReminderInfo

@login_required
def unsubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True})
        info.active = False
        info.save()
        return render_to_response('reminder/unsubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('reminder/unsubscribe.html', locals(), context_instance=RequestContext(request))
    

    
