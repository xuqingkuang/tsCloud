from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

import models, forms

class CategoryAdmin(DjangoMpttAdmin):
    tree_auto_open = 0
    list_display = ('name', 'need_count')
    form = forms.CategoryAdminForm
    search_fields = ('name', )


class OwnAppSpecInline(admin.StackedInline):
    model = models.OwnAppSpec
    extra = 1

class ExtraImageInline(admin.StackedInline):
    model = models.ExtraImage
    extra = 1

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'upload_at', 'is_active')
    list_filter = ('category',)
    search_fields = ('name', )
    readonly_fields = ('slug', )
    inlines = [
        OwnAppSpecInline, ExtraImageInline
    ]

admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Resource, ResourceAdmin)
