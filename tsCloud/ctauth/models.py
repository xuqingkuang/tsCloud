from django.db import models

# Create your models here.

class CTAuthMap(models.Model):
    user = models.ForeignKey('auth.User')
    token = models.CharField(max_length=100)
