from django.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


# Create your models here.

class Activity(models.Model):
    title = models.CharField(max_length=512)
    content = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=8192, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u'activities'

    def get_url(self):
        if self.url:
            return self.url
        else:
            return reverse('ucam_get_activity_content', args=(self.pk, ))
