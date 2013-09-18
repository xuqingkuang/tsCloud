import base64
from pprint import pprint
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import simplejson
from django.core.files.base import ContentFile
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from forms import RequestForm

from models import PhoneInfo, Data

default_rc = 0
default_msg = 'Succeed'
default_returnobj = {
    'rc': default_rc,
    'msg': default_msg,
}

data_extras = (
    'get_absolute_url', 'get_data_url', 'get_location', 'get_google_map_url',
    'get_square_url', 'get_mobile_size_url', 'get_large_size_url', 
)

def check(request):
    """
    Parameters:
        timestamp: Query the data in timestamp seconds.

    Response:
        rc: Return code
        msg: Message
        data: Serialized QuerySet
    """
    returnobj = default_returnobj.copy()
    now = datetime.now()
    timestamp = request.REQUEST.get('timestamp')
    if not timestamp:
        timestamp = 0

    try:
        timestamp = int(timestamp)
    except TypeError, error:
        returnobj['rc'] = 1
        returnobj['msg'] = error[0]

    fromdate = now - timedelta(0, timestamp)
    data = Data.objects.filter(create_time__gt = fromdate)
    data = data.order_by('pk')
    if not data.count() > 0:
        returnobj['rc'] = 2
        returnobj['msg'] = 'No new data uploaded.'
        return HttpResponse(simplejson.dumps(returnobj))

    data_json = serializers.serialize(
        'json', data, extras=data_extras, relations=('phone',)
    )
    returnobj['data'] = data_json
    return HttpResponse(simplejson.dumps(returnobj))

def filter(request):
    """
    Parameters:
        order_by: Reorder the sort of QuerySet
        device_id: Device ID for the photo uploading
        start_pk: To corporate with limit for get a range of of data.
        limit: Limitation of QuerySet

    Response:
        rc: Return code
        msg: Message
        data: Serialized QuerySet
    """
    returnobj = default_returnobj.copy()
    ds = Data.objects.select_related('phone').all()
    try:
        if request.REQUEST.get('order_by'):
            ds = ds.order_by(request.REQUEST['order_by'])
        if request.REQUEST.get('device_id'):
            ds = ds.filter(phone__device_id = request.REQUEST['device_id'])
        if request.REQUEST.get('start_pk'):
            d = ds.filter(pk = request.REQUEST['start_pk'])
            if not d:
                returnobj['rc'] = 1
                returnobj['msg'] = 'The pk of start is not exist in database'
                return HttpResponse(simplejson.dumps(returnobj))
            d = d[0]    
            index = list(ds).index(d)
            ds = ds[index:]
        if request.REQUEST.get('limit'):
            limit = int(request.REQUEST['limit'])
            ds = ds[:limit]
    except TypeError, error:
        returnobj['rc'] = 1
        returnobj['msg'] = error
        return HttpResponse(simplejson.dumps(returnobj))
    except:
        raise

    data_json = serializers.serialize(
        'json', ds, extras=data_extras, relations=('phone',)
    )
    returnobj['data'] = data_json
    return HttpResponse(simplejson.dumps(returnobj))

@csrf_exempt
def post(request):
    """
    Parameters:
        a: Action
        t: Type
        p: Parameters
        d: Data(Optional)

    Response:
        rc: Return code
        msg: message
    """
    # initial the responsor request
    returnobj = default_returnobj.copy()
    form = RequestForm(request.POST, request.FILES)

    # Error handler
    if not form.is_valid():
        returnobj['rc'] = 1
        returnobj['msg'] = form.errors
        return HttpResponse(simplejson.dumps(returnobj))

    p = form.cleaned_data['p']
    # Get the uploaded file contents
    if form.cleaned_data.get('d'):
        # If the file is loaded with generic POST method
        d = form.cleaned_data['d']
        mime_type = d.content_type
        file_name = p.get('file_name', 'untitiled.' + mime_type.split('/')[1])
    else:
        returnobj['rc'] = 1
        returnobj['msg'] = 'File(Parameter "d") is necessary by uploading'
        return HttpResponse(simplejson.dumps(returnobj))

    # Get the phone info
    phone = None
    pi = p.get('phone_info')
    if pi:
        phone, create = PhoneInfo.objects.get_or_create(device_id = pi['device_id'])
        phone.model = pi.get('model')
        phone.android_version = pi.get('android_version')
        phone.phone_number = pi.get('phone_number')
        phone.save()

    # Save the data
    desc = p.get('desc')
    latitude, longitude = p.get('latitude'), p.get('longitude')
    data = Data.objects.create(
        phone = phone,
        file_name = file_name,
        mime_type = mime_type,
        desc = desc,
        ip_address = request.META['REMOTE_ADDR'],
        latitude = latitude,
        longitude = longitude,
    )
    data.data.save(file_name, request.FILES['d'])
    data.save()
    data.generate_thumbnails()
    return HttpResponse(simplejson.dumps(returnobj))
