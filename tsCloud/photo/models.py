import time, random, threading, os.path

try:
	from PIL import Image
except ImportError, e:
    import Image

from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from tsCloud.core.models import RandomNameField, CommonModelMixin
from tsCloud.core.utils import exif_to_human, get_address_name_from_geocode, resize_image, u_slugify

from pprint import pprint

IMAGE_SIZES = (
    {'size': '240x240', 'keep_ratio': False, 'name': 'square'},
    {'size': '800x480', 'keep_ratio': True, 'name': 'medium'},
    {'size': '1024x768', 'keep_ratio': True, 'name': 'large'},
)

def get_thumb_url(data, size):
    dirname = data.get_data_dirname()
    basename = data.get_data_basename()
    path = dirname.replace('photo/original/', 'photo/thumbs/') + '/' + size + '/' + basename
    return path

def make_thumb_dirs(data = None):
    if data:
        for s in IMAGE_SIZES:
            path = os.path.join(settings.MEDIA_ROOT, os.path.dirname(get_thumb_url(data, s['size'])))
            if not os.path.exists(path): os.makedirs(path)
    else:
        date_str = datetime.utcnow().strftime('%Y/%m/%d')
        for s in IMAGE_SIZES:
            path = os.path.join(settings.UPLOAD_ROOT, 'thumbs', date_str, s['size'])
            if not os.path.exists(path): os.makedirs(path)
make_thumb_dirs()

# Create your models here.

class PhoneInfo(models.Model):
    device_id = models.CharField(_('device id'), max_length=64)
    model = models.CharField(_('model'), max_length=128, blank=True, null=True)
    android_version = models.CharField(_('android version'), max_length=64, blank=True, null=True)
    phone_number = models.CharField(_('phone_number'), max_length=24, blank=True, null=True)
    class Meta:
        ordering = ('-id', )

    def __unicode__(self):
        return '%s-%s' % (self.model, self.android_version)

class Data(CommonModelMixin, models.Model):
    phone = models.ForeignKey(PhoneInfo, blank=True, null=True)
    file_name = models.CharField(_('origenal file name'), max_length=255)
    data = RandomNameField(_('stored file name'), upload_to=os.path.join(settings.UPLOAD_DIR, 'original', '%Y/%m/%d/'), blank=True, null=True)
    mime_type = models.CharField(_('mime type'), max_length=64)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    desc = models.CharField(_('description'), max_length=2048, blank=True, null=True, default='')

    ip_address = models.IPAddressField(_('ip address'), max_length=128, blank=True, null=True)
    latitude = models.FloatField(_('latitude'), blank=True, null=True)
    longitude = models.FloatField(_('longitude'), blank=True, null=True)
    location = models.CharField(_('location'), max_length=64, null=True, blank=True)
    views = models.BigIntegerField(_('view counts'), max_length=256, default=0)

    class Meta:
        ordering = ('-id', )

    def __unicode__(self):
        if self.slug:
            return self.slug
        return '%s-%s' % (self.pk, self.file_name)

    def _generate_thumbnail(self, size, keep_ratio=True, **kwargs):
        write_to = self.get_data_path(size)
        return resize_image(self.data.path, write_to, size, keep_ratio)

    def _get_location_name_when_save(self):
        self.location = get_address_name_from_geocode(
            latitude = self.latitude,
            longitude = self.longitude,
        )

    def get_absolute_url(self):
        return reverse('tsCloud.photo.views.get', args=(self.slug, ))

    def get_data_basename(self):
        return os.path.basename(self.data.name)

    def get_data_dirname(self):
        return os.path.dirname(self.data.name)

    def get_data_url(self, size=None):
        if not size:
            return self.data.url
        return os.path.join(settings.MEDIA_URL, get_thumb_url(self, size))

    def get_data_path(self, size=None):
        if not size:
            return self.data.path
        return os.path.join(settings.MEDIA_ROOT, get_thumb_url(self, size))

    def get_exif_info(self):
        if not self.is_image() and not self.mime_type in ('image/jpeg', 'image/tiff'):
            return []
        return exif_to_human(self.data)


    def get_google_map_image_link(self, zoom=14, size="300x125"):
        width = size.split('x')[0]
        height = size.split('x')[1]

        if not self.have_geo():
            return mark_safe('<img src="%s" width="%s" height="%s" alt="No location found" />' % (
                os.path.join(settings.STATIC_URL, 'images/no_location_found.png'),
                width, height
            ))

        return mark_safe('<img src="http://maps.google.com/maps/api/staticmap?zoom=%s&size=%s&maptype=roadmap&markers=color:red|color:red|label:Here|%s,%s&sensor=false" width="%s" height="%s" alt="Google maps" />' % (
            zoom, size, self.latitude, self.longitude, width, height
        ))

    def get_google_map_url(self):
        if not self.have_geo():
            return None
        return mark_safe('http://maps.google.com/maps?geocode=&q=%s,%s' % (
            self.latitude, self.longitude
        ))

    def get_location(self):
        if self.location:
            return self.location
        if self.latitude and self.longitude:
            self._get_location_name_when_save()
            self.save()
        return '(Unknown location)'

    def get_square_url(self, size='240x240'):
        return self.get_data_url(size)

    def get_mobile_size_url(self, size='800x480'):
        return self.get_data_url(size)

    def get_large_size_url(self, size='1024x768'):
        return self.get_data_url(size)

    def generate_slug(self):
        title = ''
        if self.phone_id:
            title += unicode(self.phone) + '-'
        title += self.file_name + '-'
        title += str(random.randint(0, 10000))
        return u_slugify(title)

    def generate_thumbnails(self):
        make_thumb_dirs(self)
        if not self.is_image():
            return
        for s in IMAGE_SIZES:
            # Create a new thread for the image reiszing
            #resize_thread = threading.Thread(target=self._generate_thumbnail, args=s)
            #resize_thread.start()
            self._generate_thumbnail(**s)

    def have_geo(self):
        if self.latitude and self.longitude:
            return True
        return False

    def is_image(self):
        if self.mime_type.startswith('image/'):
            return True
        return False

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self._get_location_name_when_save()
        return super(Data, self).save(*args, **kwargs)

