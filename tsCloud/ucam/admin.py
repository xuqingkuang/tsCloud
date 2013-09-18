from django.contrib import admin

import models

class ActivityAdmin(admin.ModelAdmin):
    search_fields = (('content', ))
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    exclude = ('url', )

admin.site.register(models.Activity, ActivityAdmin)
