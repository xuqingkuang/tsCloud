from django.conf.urls.defaults import patterns, include, url
import views, api

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'photodemo.views.home', name='home'),
    # url(r'^photodemo/', include('photodemo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.all, name='all photos'),
    #url(r'^upload/$', views.upload, 'all),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/$', views.get),

    url(r'^api/check/$', api.check),
    url(r'^api/filter/$', api.filter),
    url(r'^api/post/$', api.post),
)
