import models

from datetime import datetime
from django.http import HttpResponse, Http404
from django.core import serializers

def get_activities(request):
    now = datetime.now()
    activities = models.Activity.objects.filter(
        is_active = True,
        start_date__lt = now,
        end_date__gt = now
    )
    if not activities:
        raise Http404
    activities_json = serializers.serialize(
        'json', activities, extras=('get_url', ), excludes=('content', 'url')
    )
    return HttpResponse(activities_json)

def get_activity_content(request, pk):
    try:
        activity = models.Activity.objects.get(pk = pk)
    except models.Activity.DoesNotExist, err:
        raise Http404(err)
    return HttpResponse(activity.content)
