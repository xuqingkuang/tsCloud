import re, urllib, os.path
try:
    from PIL import Image, ImageOps
except ImportError, e:
    import Image, ImageOps

from unidecode import unidecode
from django.utils import simplejson
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

import EXIF

import string, random

def generate_random_string(length = 11):
    return ''.join(
        [random.choice(string.ascii_letters + string.digits) for n in xrange(length)]
    )

def exif_to_human(image):
    fields = (
        ('Image Make', _('Camera manifacture')),
        ('Image Model', _('Camera model')),
        ('EXIF DateTimeDigitized', _('Digitized time')),
        ('EXIF DateTimeOriginal', _('Taken time')),
        ('Image Software', _('Image software')),
        ('EXIF ColorSpace', _('Color space')),
        ('EXIF FocalLength', _('Focal length')),
        ('EXIF FocalLengthIn35mmFilm', _('Forcal length(in 35mm)')),
        ('EXIF ISOSpeedRatings', _('ISO speed')),
        ('EXIF MaxApertureValue', _('Max aperture')),
        ('EXIF ExposureMode', _('Exposure mode')),
        ('EXIF ExposureProgram', _('Exposure program')),
        ('EXIF ExposureTime', _('Exposure time')),
        ('EXIF Flash', _('Flash')),
        ('EXIF LightSource', _('Light source')),
        ('EXIF DigitalZoomRatio', _('Digital zoom ratio')),
        ('EXIF ExifImageLength', _('Image length')),
        ('EXIF ExifImageWidth', _('Image width')),
        ('EXIF WhiteBalance', _('White balance')),
        ('EXIF Sharpness', _('Sharpness')),
        ('EXIF Contrast', _('Contrast')),
    )
    exif = []
    tags = EXIF.process_file(image, strict=True, stop_tag='JPEGThumbnail')
    for f in fields:
        if tags.has_key(f[0]):
            exif.append((f[1], str(tags[f[0]])))
    image.close()
    return exif

def geocode_to_address(latitude, longitude):
    # In the tradition Chinese, we say longitude as first.
    params = urllib.urlencode({
        'coordinate': '%s,%s' % (longitude, latitude),
        'source': settings.SINA_APP_KEY
    })
    try:
        json_str = urllib.urlopen(
            "http://api.map.sina.com.cn/geocode/geo_to_address.json?%s" % params
        )
    except IOError, error:
        return None
    json = None
    try:
        json = simplejson.loads(json_str.read())
    except TypeError, error:
        raise
    return json

def get_address_name_from_geocode(latitude, longitude):
    json = geocode_to_address(latitude, longitude)
    if not json or not json.get('address'):
        return
    geo_dict = {
        'province': json['address']['prov_name'],
        'city': json['address']['city_name'],
        'district': json['address']['district_name'],
        'street': json['address']['street'],
    }
    geo_list = geo_dict.values()
    new_geo_list = []
    for s in geo_list:
        if s: new_geo_list.append(s)
    return ', '.join(new_geo_list).encode('utf-8')

def resize_image(image, write_to, size, keep_ratio, quality = None):
    """
    Resize image to specific size.
    """
    if not quality:
        if hasattr(settings, 'RESIZE_QUALITY'):
            quality = settings.RESIZE_QUALITY
        else:
            quality = 85

    x, y = [int(x) for x in size.split('x')]

    # if the image wasn't already resized, resize it
    if os.path.exists(write_to):
        return write_to
    image = Image.open(image)
    # ImageOps compatible mode
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")
    if keep_ratio:
        # image.thumbnail([x, y]) # generate a 128x128 thumbnail
        image.thumbnail(size=(x, y), resample=Image.ANTIALIAS)
    else:
        # Crop the image to fit size
        image = ImageOps.fit(image, (x, y), Image.ANTIALIAS)
    image.save(write_to, image.format, quality=quality)
    return write_to

def u_slugify(value):
    value = value.strip() # remove trailing whitespace
    if not isinstance(value, unicode):
        value = value.decode('utf-8')
    value = unidecode(value) # Convert to PinYin
    value = re.sub('_', '-', value)
    value = re.sub('\.', '-', value)
    value = slugify(value)
    return value
