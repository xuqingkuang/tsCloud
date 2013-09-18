from django.db import models
from django.db.models import Q, signals
from django.core.files import File
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings

from tsCloud.core.models.fields.files import URLImageField

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='category', blank=True)
    parent = models.ForeignKey('self', blank=True, null=True) 
    user = models.ManyToManyField('auth.User', blank=True)

    class Meta:
        verbose_name_plural = u'categories'

    def __unicode__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='supplier')    # Small size
    user = models.ManyToManyField('auth.User', blank=True)

    def __unicode__(self):
        return self.name

class Ad(models.Model):
    slug = models.SlugField()
    flag = models.BooleanField()                                # Fixed on top.
    category = models.ForeignKey(Category)
    supplier = models.ForeignKey(Supplier)
    user = models.ManyToManyField('auth.User', blank=True)
    title = models.CharField(max_length=255)
    description_240x240 = models.CharField(max_length=8192)
    description_240x480 = models.CharField(max_length=8192)
    description_480x240 = models.CharField(max_length=8192)
    description_480x480 = models.CharField(max_length=8192)
    description_480x762 = models.CharField(max_length=8192)
    price_market = models.IntegerField()
    price_supplier = models.IntegerField()
    banner_original_url = models.URLField()
    banner_original = URLImageField(upload_to='ad/original/')
    banner_240x240 = URLImageField(upload_to='ad/240x240/')
    banner_240x480 = URLImageField(upload_to='ad/240x480/')
    banner_480x240 = URLImageField(upload_to='ad/480x240/')
    banner_480x480 = URLImageField(upload_to='ad/480x480/')
    banner_480x762 = URLImageField(upload_to='ad/480x762/')
    banner_text = models.CharField(max_length=256)
    banner_color = models.CharField(max_length=7)
    ad_link = models.CharField(max_length=8192, blank=True)      # Buy link

    def __unicode__(self):
        return self.title

    @classmethod
    def filterByRequest(cls, request):
        ads = cls.objects.select_related('category__name', 'supplier__name').order_by('-flag')

        # Process the selected categories and suppliers by user
        if request.user.is_authenticated():
            selected_categories = Category.objects.filter(user = request.user)
            selected_suppliers = Supplier.objects.filter(user = request.user)

            if len(selected_categories) != 0:
                ads = ads.filter(category__in = selected_categories)
            if len(selected_suppliers) != 0:
                ads = ads.filter(supplier__in = selected_suppliers)

        # Process query
        request.query = False
        if request.REQUEST.get('search_key'):
            request.query = True
            key = request.REQUEST['search_key']
            ads = ads.filter(
                Q(title__startswith = key)
                | Q(category__name__startswith = key)
                | Q(supplier__name__startswith = key)
            )

        if request.REQUEST.get('category_id'):
            request.query = True
            categories = Category.objects.filter(
                pk__in = request.REQUEST.getlist('category_id')
            )
            ads = ads.filter(category__in = categories)

        if request.REQUEST.get('supplier_id'):
            request.query = True
            suppliers = Supplier.objects.filter(
                pk__in = request.REQUEST.getlist('supplier_id')
            )
            ads = ads.filter(supplier__in = suppliers)
        return ads

    def get_source_link(self):
        return self.ad_link or self.get_internal_related_ad_link()

    def get_internal_related_ad_link(self):
        return reverse('tsCloud.ad.views.get', args=(self.slug, ))

    def get_text(self):
        return self.adcontent_set.all()[0].text

class AdContent(models.Model):
    ad = models.ForeignKey(Ad)
    text = models.TextField()

    def formattext(self):
        if (len(self.text) > 30):
            return '%s ... ...' % self.text[:30]
        return self.text

    def __unicode__(self):
        return self.ad.title

class App(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    package = models.CharField(max_length=128, unique=True)
    author = models.CharField(max_length=128, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=64, blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    download_url = models.URLField(blank=True, null=True)
    screen_shot1 = models.URLField(blank=True, null=True)
    screen_shot2 = models.URLField(blank=True, null=True)
    screen_shot3 = models.URLField(blank=True, null=True)
    screen_shot4 = models.URLField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    download_count = models.IntegerField(default=0, blank=True)
    score = models.IntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class Phone(models.Model):
    device_id = models.CharField(max_length=56)
    vender = models.CharField(max_length=128, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    app = models.ManyToManyField(App)

    def __unicode__(self):
        return '%s %s' % (self.vender, self.model)

def update_cache(sender, **kwargs):
    # Generate the instance keys belong to the user.
    class_name = sender.__name__.lower();
    instance = kwargs.get('instance')
    if not class_name or not instance:
        return
    usernames = instance.user.values_list('username', flat=True)
    keys = [ '%s_%s' % (username, class_name) for username in usernames]

    # Clean up the old cache.
    cache.delete(class_name)
    cache.delete_many(keys)

signals.post_save.connect(update_cache, Category)
signals.post_delete.connect(update_cache, Category)
signals.post_save.connect(update_cache, Supplier)
signals.post_delete.connect(update_cache, Supplier)
