from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel, TreeForeignKey
from datetime import date

from tsCloud.core.utils import generate_random_string

# Create your models here.

class Category(MPTTModel):
    name            = models.CharField(max_length=255)
    slug            = models.SlugField(unique=True)
    form_class_name = models.CharField(max_length=32, default='ResourceBaseForm')
    need_count      = models.BooleanField(default=False)
    parent          = TreeForeignKey('self', null=True, blank=True, related_name='children')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('categories')

class Resource(models.Model):
    category        = models.ForeignKey(Category, verbose_name=_('Category'))
    slug            = models.CharField(max_length=11, db_index=True) # Random hash
    name            = models.CharField(verbose_name=_('Name'), max_length=255)
    version         = models.CharField(verbose_name=_('Version'), max_length=128, default='1.0')
    desc            = models.CharField(verbose_name=_('Short description'), max_length=8192)
    download_url    = models.URLField(verbose_name=_('Download URL'), max_length=8192)
    is_active       = models.BooleanField(default=True)
    upload_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')
        ordering = ('-pk', )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """
        Get detail url.
        """
        return reverse('resource_detail', args=(self.slug, ))

    def get_download_url(self):
        """
        Get download redirect url
        """
        return reverse('resource_download', args=(self.slug, ))

    def download(self, source = None):
        # TODO : Get the url for redirect to download_url
        today = date.today()
        if source:
            today_counter, create = self.counter_set.get_or_create(
                date = today,
                source = source,
            )
        else:
            today_counter, create = self.counter_set.get_or_create(
                date = today,
                source = None,
            )
        today_counter.download_num += 1
        today_counter.save()
        return self.download_url

    def save(self, *args, **kwargs):
        if not self.slug:
            random_string = generate_random_string()
            while Resource.objects.filter(slug = random_string).count() != 0:
                random_string = generate_random_string()
            self.slug = random_string
        return super(Resource, self).save(*args, **kwargs)

class ExtraImage(models.Model):
    resource        = models.ForeignKey(Resource)
    type            = models.CharField(max_length=11)
    image_url       = models.URLField()

class Counter(models.Model):
    resource        = models.ForeignKey(Resource)
    download_num    = models.IntegerField(default=0)
    source          = models.CharField(max_length=32, blank=True, null=True)
    date            = models.DateField()

    class Meta:
        ordering = ('source', 'pk')
