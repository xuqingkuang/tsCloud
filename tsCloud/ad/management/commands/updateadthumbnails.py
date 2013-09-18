import os.path
from django.conf import settings
from tsCloud.ad.models import Ad
from _private import ADBaseCommand

class Command(ADBaseCommand):
    def handle(self, *args, **options):
        super(Command, self).handle(args, options)
        image_attrs = [
            'banner_original', 'banner_240x240', 'banner_240x480',
            'banner_480x240', 'banner_480x480', 'banner_480x762'
        ]
        for ad in Ad.objects.all():
            for attr in image_attrs:
                field = getattr(ad, attr)
                if not field.name_is_url():
                    continue
                self.stdout.write(
                    ' * PK %s - Downloading %s from %s for ad %s... ' % (
                         ad.pk, field.name, attr, ad,
                    )
                )
                field.download(overwrite = options['overwrite'])
                self.stdout.write('Done.\n')
