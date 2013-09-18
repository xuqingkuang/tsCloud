from django.conf.urls import patterns, url
import views, api

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^(?P<slug>[-\w\d]+)/$', views.get),
    url(r'^api/list/$', api.get_ad),
    url(r'^api/apps/$', api.get_apps),
    url(r'^api/apps/post/$', api.post_apps),
    url(r'^api/category/$', api.get_category),
    url(r'^api/category/set/$', api.set_category),
    url(r'^api/supplier/$', api.get_supplier),
    url(r'^api/supplier/set/$', api.set_supplier),
)
