import models, random, re

from django.http import HttpResponse, Http404
from django.utils import simplejson
from django.core import serializers
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

def __veresion_cmp(version1, version2):
    def normalize(v):
        ss = [x for x in filter(lambda ch: ch in '0123456789.', v).split(".")]
        normalized = []
        for s in ss:
            if s:
                normalized.append(int(s))
        return normalized
    return cmp(normalize(version1), normalize(version2))

@csrf_exempt
def get_ad(request, ads = None):
    #try:
    #    request_json  = simplejson.loads(request.POST['post_json'])
    #except:
    #    return HttpResponse(simplejson.dumps({
    #        'res': 1,
    #        'msg': 'JSON decode error'
    #    }))

    if not ads:
        ads = models.Ad.filterByRequest(request)

    def generate_return_object(ads):
        return_obj = {
            'res': 0,
            'data': [],
            'length': len(ads),
        }
        for ad in ads:
            ad = {
                'ad_id': ad.pk,
                'flag': ad.flag,
                'category_name': ad.category.name,
                'category_id': ad.category_id,
                'supplier_name': ad.supplier.name,
                'supplier_id': ad.supplier_id,
                'title': ad.title,
                'description_240x240': ad.description_240x240,
                'description_240x480': ad.description_240x480,
                'description_480x240': ad.description_480x240,
                'description_480x480': ad.description_480x480,
                'description_480x762': ad.description_480x762,
                'price_market': ad.price_market,
                'price_supplier': ad.price_supplier,
                'banner_240x240': request.build_absolute_uri(ad.banner_240x240.url),
                'banner_240x480': request.build_absolute_uri(ad.banner_240x480.url),
                'banner_480x240': request.build_absolute_uri(ad.banner_480x240.url),
                'banner_480x480': request.build_absolute_uri(ad.banner_480x480.url),
                'banner_480x762': request.build_absolute_uri(ad.banner_480x762.url),
                'banner_text': ad.banner_text,
                'banner_color': ad.banner_color,
                'ad_link': ad.ad_link or request.build_absolute_uri(ad.get_internal_related_ad_link()),
            }
            return_obj['data'].append(ad)
        return return_obj
    
    def generate_top_objects(ads):
        return_list = []
        for ad in ads:
            if ad.flag:
                return_list.append(ad)
        return return_list

    def randon_choice_ads(ads, top, limit = 20):
        i = len(top);
        ads_length = len(ads)
        return_list = top
        if ads_length < limit:
            limit = ads_length
        while i < limit:
            ad = random.choice(ads)
            try:
                return_list.index(ad)
            except ValueError:
                return_list.append(ad)
                i += 1;
        return return_list

    if not request.query:
        top_ads = generate_top_objects(ads)
        ads = randon_choice_ads(ads, top_ads)
    return HttpResponse(simplejson.dumps(generate_return_object(ads)))

def get_apps(request):
    """
    
    """
    apps = models.App.objects.filter(is_active = True)
    if request.REQUEST.get('device_id'):
        apps = apps.exclude(phone__device_id = request.REQUEST['device_id'])
    if not apps:
        raise Http404('No app data found.')
    apps = apps.order_by('?')[0]
    selected_apps = models.App.objects.filter(pk = apps.pk)
    return HttpResponse(serializers.serialize('json', selected_apps))

@csrf_exempt
def post_apps(request):
    """
    Sample request JSON
    {
        "vender": [VENDER],
        "model": [MODEL],
        "device_id": [MEID],
        "apps": [
            {
                'name': [appName],
                'package': [packageName],
                'version': [versionName]
            },
            ...
        ]
    }
    """
    response = {
        'rc': 200,
        'message': 'ok',
    }
    if request.method != 'POST':
        response = {
            'rc': 405,
            'message': 'Method not allowed',
        }
        return HttpResponse(simplejson.dumps(response))
    if not request.POST.get('request'):
        response = {
            'rc': 404,
            'message': 'Parameter "request" is required',
        }
        return HttpResponse(simplejson.dumps(response))
    json = simplejson.loads(request.REQUEST['request'])
    
    # Custom code for save phone
    if not json.get('device_id'):
        response = {
            'rc': 404,
            'message': 'JSON field "device_id" is required',
        }
        
    phone, create = models.Phone.objects.get_or_create(device_id = json['device_id'])
    phone.vender = json['vender'].encode('utf-8')
    phone.model  = json['model'].encode('utf-8')
    phone.save()
    
    exist_apps = phone.app.all()
    installed_app_packages = []
    # Custom code for save apps m2m
    for app_json in json['apps']:
        app, create = models.App.objects.get_or_create(package = app_json['package'])
        app.name = app_json['name'].encode('utf-8')
        if not app.version:
            app.version = app_json['version']
        else:
            try:
                if __veresion_cmp(app_json['version'], app.version) > 0:
                    app.version = app_json['version']
            except ValueError, err:
                response = {
                    'rc': 500,
                    'message': 'Version compare error, ver in db is %s, post data is %s' % (
                        app.version,
                        app_json['version'],
                    ),
                }
                return HttpResponse(simplejson.dumps(response))

        if not app.download_url:
            app.is_active = False
        app.save()
        installed_app_packages.append(app.package)
        if not app in exist_apps:
            phone.app.add(app)

    # Remove the uninstalled apps
    remove_apps = phone.app.exclude(package__in = installed_app_packages)
    for app in remove_apps:
        phone.app.remove(app)
    return HttpResponse(simplejson.dumps(response))

@csrf_exempt
def get_category(request, categories = None, do_cache = True, returns_dict = False):
    hot = False
    if request.REQUEST.get('hot'):
        hot = True
    if not categories:
        # Get data from cache
        if request.user.is_authenticated():
            return_obj = cache.get('category_' + request.user.username)
        elif hot:
            return_obj = cache.get('hot_category')
        else:
            return_obj = cache.get('category')
        if return_obj:
            if returns_dict:
                return simplejson.loads(return_obj)
            return HttpResponse(return_obj)
        # Do the DB works
        categories = models.Category.objects.all()
    if request.user.is_authenticated():
        selected_categories = request.user.category_set.all()
        if len(selected_categories) == 0:
            selected_categories = categories
    else:
        selected_categories = categories

    return_obj = {
        'res': 0,
        'length': len(categories),
        'data': [],
    }

    for category in categories:
        # Skiped the fake cold categories
        if hot and category.pk % 3 == 1:
            continue
        # Skiped children categories
        if not category.parent_id is None:
            continue
        # Do the root categories work.
        data = {
            'id': category.pk,
            'selected': category in selected_categories,
            'name': category.name,
            'has_ads': category.ad_set.count(),
            'icon_url': category.icon and request.build_absolute_uri(category.icon.url) or "",
            'children': [],
            'children_length': 0,
        }
        # Do the children categories work.
        for child in categories:
            if child.parent_id == category.pk:
                data['children'].append({
                    'id': child.pk,
                    'selected': child in selected_categories,
                    'name': child.name,
                    'has_ads': child.ad_set.count(),
                    'icon_url': child.icon and request.build_absolute_uri(child.icon.url) or "",
                    'children': []
                })
        data['children_length'] = len(data['children'])
        return_obj['data'].append(data)
    json = simplejson.dumps(return_obj)

    # Save the json to cache
    if do_cache:
        if request.user.is_authenticated():
            cache.set(request.user.username + '_category', json)
        elif hot:
            cache.set('hot_category', json)
        else:
            cache.set('category', json)

    if returns_dict:
        return return_obj
    return HttpResponse(json)

@csrf_exempt
def get_supplier(request, suppliers = None, do_cache = True):
    # Get data from cache
    if not suppliers:
        if request.user.is_authenticated():
            return_obj = cache.get('supplier_' + request.user.username)
        else:
            return_obj = cache.get('supplier')
        if return_obj:
            return HttpResponse(return_obj)
        # Do the DB works
        suppliers = models.Supplier.objects.all()
    if request.user.is_authenticated():
        selected_suppliers = request.user.supplier_set.all()
        if len(selected_suppliers) == 0:
            selected_suppliers = suppliers
    else:
        selected_suppliers = suppliers

    return_obj = {
        'res': 0,
        'length': len(suppliers),
        'data': [],
    }

    for supplier in suppliers:
        return_obj['data'].append({
            'id': supplier.pk,
            'name': supplier.name,
            'icon_url': request.build_absolute_uri(supplier.icon.url),
            'selected': supplier in selected_suppliers,
        })
    json = simplejson.dumps(return_obj)
    # Save the json to cache
    if do_cache:
        if request.user.is_authenticated():
            cache.set(request.user.username + '_supplier', json)
        else:
            cache.set('supplier', json)
    return HttpResponse(json)

@csrf_exempt
def set_category(request):
    return_obj = {
        'res': 0,
        'msg': 'Succeed',
        'data': [],
    }
    if not request.user.is_authenticated():
        return_obj['res'] = 401
        return_obj['msg'] = 'Unauthorized'
        return HttpResponse(simplejson.dumps(return_obj))
    user = request.user

    # Clean up the old exist category list
    # FIXME: Reverse query broken here
    categories = models.Category.objects.filter(user = user)

    for category in categories:
        category.user.remove(user)

    # Add category to user
    category_ids = request.REQUEST.getlist('category_id')
    categories = models.Category.objects.filter(
        Q(pk__in = category_ids)
        | Q(parent__pk__in = category_ids)
    )
    for category in categories:
        category.user.add(user)
    return get_category(request = request, categories = categories, do_cache = False)

@csrf_exempt
def set_supplier(request, suppliers = None):
    return_obj = {
        'res': 0,
        'msg': 'Succeed',
        'data': [],
    }
    if not request.user.is_authenticated():
        return_obj['res'] = 401
        return_obj['msg'] = 'Unauthorized'
        return HttpResponse(simplejson.dumps(return_obj))
    user = request.user
    # Clean up the old exist supplier list
    # FIXME: Reverse query broken here
    suppliers = models.Supplier.objects.filter(user = user)
    for supplier in suppliers:
        supplier.user.remove(user)

    # Add supplier to user
    suppliers = models.Supplier.objects.filter(
        pk__in = request.REQUEST.getlist('supplier_id')
    )
    for supplier in suppliers:
        supplier.user.add(user)
    return get_supplier(request = request, suppliers = suppliers, do_cache = False)
