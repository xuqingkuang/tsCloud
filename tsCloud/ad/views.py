# Create your views here.

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

import models
import api

@csrf_exempt
def index(request, template_name='ad/index.html'):
    ads = models.Ad.filterByRequest(request)
    if request.is_ajax() or request.REQUEST.get('is_data_request'):
        return api.get_ad(request, ads)
    categories = api.get_category(request, returns_dict=True)['data']
    selected_category = request.REQUEST.get('category_id')
    if selected_category:
        selected_category = int(selected_category)
    return render(request, template_name, {
        'ads': ads,
        'categories': categories,
        'selected_category': selected_category,
    })

def get(request, slug, template_name='detail.html'):
    try:
        ad = models.Ad.objects.get(slug = slug)
    except models.Ad.DoesNotExist, err:
        raise Http404(err)
    return render(request, template_name, {
        'ad': ad
    })
