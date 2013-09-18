from django.http import Http404
from django.shortcuts import render

from models import PhoneInfo, Data

# Create your views here.

def all(request, template_name='photo/index.html'):
    ds = Data.objects.select_related('phone').all()
    ps = PhoneInfo.objects.all()
    if ds.count > 0:
        pi = ds[0].phone
    else:
        pi = None

    return render(request, template_name, {
        'data': ds,
        'phones': ps,
        'phone_info': pi,
    })

def get(request, slug, template_name='photo/get.html'):
    # FIXME: Can get request hash here, so not available.
    # back_link = request.META.get('HTTP_REFERER')
    ds = Data.objects.select_related('phone').filter(slug = slug)
    if not ds:
        raise Http404('Page not found')
    d = ds[0]

    # TODO: Ignore counts of the man who uploaded the data
    # TODO: Ignore counts who visit the page multiple times.
    d.views += 1
    d.save()
    return render(request, template_name, {
        # 'back_link': back_link,
        'data': d,
    })
