from django.contrib import admin
import models

class AdContentInline(admin.TabularInline):
    model = models.AdContent
    extra = 0

class AdAdmin(admin.ModelAdmin):
    search_fields = (('title',))
    list_display = ('title', 'price_market', 'price_supplier', 'description_240x240', 'flag')
    inlines = [AdContentInline]

class AppAdmin(admin.ModelAdmin):
    search_field = (('name', ))
    list_display = ('name', 'package', 'version')

class PhoneAdmin(admin.ModelAdmin):
    search_field = (('vender', 'model', 'device_id'))
    list_display = ('vender', 'model', 'device_id')

class CategoryAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    ordering = ('id',)

class SupplierAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    list_display = ('name', 'icon')

admin.site.register(models.Ad, AdAdmin)
admin.site.register(models.App, AppAdmin)
admin.site.register(models.Phone, PhoneAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Supplier, SupplierAdmin)
