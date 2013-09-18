import time, random, os.path
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class RandomNameField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(RandomNameField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)

    def generate_filename(self, instance, filename):
        ext = os.path.splitext(filename)[1]
        d = os.path.dirname(filename)
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0, 1000)
        name = os.path.join(d, fn + ext)
        return os.path.join(self.get_directory_name(), name)

class CommonModelMixin(models.Model):
    slug = models.SlugField(
        _('url slug'), max_length=128, unique=True,
        help_text=_('Simple words for URL indentification, must be unique')
    )
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        return super(CommonModelMixin, self).save(*args, **kwargs)
