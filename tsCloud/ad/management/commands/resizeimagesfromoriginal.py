import urllib
import os.path

from django.core.files import File
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from tsCloud.ad.models import Ad

try:
    from PIL import Image
except ImportError:
    import Image

from _private import ADBaseCommand

class Command(ADBaseCommand):
    def handle(self, *args, **options):
        super(Command, self).handle(args, options)
        image_attrs = [
            'banner_240x240', 'banner_240x480', 'banner_480x240',
            'banner_480x480', 'banner_480x762'
        ]
        for ad in Ad.objects.all():
            field = ad.banner_original
            url = ad.banner_original_url
            if not self.valid_url(url):
                continue
            if not options['overwrite'] and os.path.isfile(field.path):
                continue
            self.stdout.write(
                ' * PK %s - Downloading %s from banner_original for ad %s... ' % (
                     ad.pk, url, ad,
                )
            )
            field.download(url = ad.banner_original_url, overwrite = options['overwrite'])

            # Generate the common variable for each resized image.
            filename = '.'.join(field.name.split('.')[0:-1]) + '.jpg'
            original_image = Image.open(field.path)
            self.stdout.write('Done.\n')

            # Process the other resolutions
            for attr in image_attrs:
                image = original_image.copy()
                field = getattr(ad, attr)
                if not options['overwrite'] and os.path.isfile(field.path):
                    continue
                self.stdout.write(
                    ' * PK %s - Resizing %s from %s for ad %s... ' % (
                         ad.pk, filename, attr, ad,
                    )
                )
                size = [int(s) for s in attr.split('_')[1].split('x')]
                image = image.convert('RGB')
                image.thumbnail(size, Image.ANTIALIAS)
                # image_content = ImageOps.fit(image, size, Image.ANTIALIAS)
                tmp_path = '/tmp/temp.jpg'
                image.save(tmp_path, 'JPEG', quality=80)
                field.save(filename, File(open(tmp_path, 'ro')))
                self.stdout.write('Done.\n')
