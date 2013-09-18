from django.db import models
from django.db.models import Q

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey('auth.User')
    emotion_id = models.IntegerField(null=True)
    update_at = models.DateTimeField(auto_now = True)
