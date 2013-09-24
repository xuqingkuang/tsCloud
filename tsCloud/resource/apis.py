from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils import simplejson
from django.core import serializers
import urllib, urllib2
import models

import qiniu.rs

__all__ = ('generate_short_url', 'get_categories', 'get_resources', 'get_recommendations', 'get_storage_token')

def generate_short_url(request, slug):
    """
    Generate short URL.

    Method:
        GET
    Response:
        JSON
    Request Format:
        http://[HOST]/resource/api/[RESOURCE_SLUG]/generate_short_url.json
    Parameters:
        slug - [String]
    Example:
        Request - http://www.thundersoft.com:9978/resource/api/JGc6J80g7Zi/generate_short_url.json
        Response - {"data": {"url": "http://x.co/2Hiuk"}}
    """
    try:
        res = models.Resource.objects.get(slug = slug)
    except models.Resource.DoesNotExist, err:
        raise Http404(err)
    download_url = res.get_download_url()
    if request.REQUEST.get('source'):
        download_url = download_url + '?source=' + request.REQUEST['source']
    absolute_url = request.build_absolute_uri(download_url)
    response = urllib2.urlopen(settings.SHORT_URL_SERVICE % (absolute_url)).read()
    response_data = {
        'data': {
            'url': response
        }
    }
    return HttpResponse(simplejson.dumps(response_data))

def get_categories(request, format, slug = None):
    """
    Get categories, with slug parameters will get children categories.

    Method:
        GET
    Response:
        [JSON, XML]
    Request Format:
        http://[HOST]/resource/api/[SLUG]/get_categories.[FORMAT]
    Parameters:
        slug - [String]
    Example:
        Request - http://www.thundersoft.com:9978/resource/api/ycamera-app/get_categories.json
    """
    if slug:
        try:
            parent_category = models.Category.objects.get(slug = slug)
        except models.Category.DoesNotExist, err:
            raise Http404(err)
        categories = parent_category.get_children()
    else:
        categories = models.Category.objects.filter(parent = None)
    return HttpResponse(serializers.serialize(
        format,
        categories,
        fields=('name', 'slug', 'need_count')
    ))

def get_resources(request, format, category_slug=None):
    """
    Get resources belong to a category

    Method:
        GET
    Response:
        [JSON, XML]
    Request Format:
        http://[HOST]/resource/api/[CATEGORY_SLUG]/get_resources.[FORMAT]
    Parameters:
        category_slug - [String]
    Example:
        Request - http://www.thundersoft.com:9978/resource/api/ycamera-app/get_resources.json
    """
    if not category_slug and not request.REQUEST.get('q'):
        raise Http404('Search parameters is required')
    if category_slug:
        try:
            category = models.Category.objects.get(slug = category_slug)
        except models.Category.DoesNotExist, err:
            raise Http404(err)
        relations = category.get_relation_models()
        resources = category.resource_set.all()
    else:
        resources = models.Resource.objects.all()
        relations = ('category', )
    if request.REQUEST.get('q'):
        query = simplejson.loads(request.REQUEST['q'])
        resources = resources.filter(**query)
    resources = resources.filter(is_active = True)
    return HttpResponse(serializers.serialize(
        format, resources,
        excludes = ('slug', 'download_url', ),
        extras = ('get_icon_url', 'get_download_url'),
        relations = relations,
    ))

def get_recommendations(request, format, category_slug=None):
    """
    Get recommendations
    
    Method:
        GET
    Response:
        [JSON, XML]
    Request Format:
        http://[HOST]/resource/api/[CATEGORY_SLUG]/get_recommendations.[FORMAT]
    Parameters:
        category_slug - [String]
    Example:
        Request - http://www.thundersoft.com:9978/resource/api/ycamera-app/get_recommendations.json
    """
    if not category_slug and not request.REQUEST.get('q'):
        raise Http404('Search parameters is required')
    if category_slug:
        try:
            category = models.Category.objects.get(slug = category_slug)
        except models.Category.DoesNotExist, err:
            raise Http404(err)
        recommendations = category.recommendation_set.all()
    else:
        recommendations = models.Recommendation.objects.all()
    if request.REQUEST.get('q'):
        query = simplejson.loads(request.REQUEST['q'])
        recommendations = recommendations.filter(**query)
    recommendations = recommendations.filter(resource__is_active = True)
    return HttpResponse(serializers.serialize(
        format, recommendations,
        extras = ('get_icon_url', 'get_desc', 'get_download_url'),
        relations = ('category', 'resource')
    ))

def get_storage_token(request, bucket_name = 'cam001-userdata'):
    """
    Get remote storage token

    Method:
        GET
    Response:
        JSON
    Request Format:
        http://[HOST]/resource/api/[BUCKET_NAME]/get_storage_token.json
    Parameters:
        bucket_name - [String]
    Example:
        Request - http://www.thundersoft.com:9978/resource/api/cam001-userdata/get_storage_token.json
    """
    policy = qiniu.rs.PutPolicy(bucket_name)
    token = policy.token()
    return HttpResponse(simplejson.dumps({
        'storage': 'qiniu',
        'token': token,
    }))

def help(request):
    html = '<!DOCTYPE html> \
    <html> \
    <head> \
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" /> \
        <title>ThunderSoft Resources APIs</title> \
    </head> \
    <body> \
        <h1>ThunderSoft Resources APIs</h1> \
        <h2>Contents</h2> \
        <ol> \
    '

    for func_name in __all__:
        func = globals()[func_name]
        html += '<li><a href="#%s">%s</a></li>' % (func_name, func_name)
    html += '</ol>'

    for func_name in __all__:
        func = globals()[func_name]
        html += '<h2><a name="%s">%s</a></h2><pre>%s</pre>' % (func_name, func_name, func.__doc__)
    html += '</html>'
    return HttpResponse(html)
