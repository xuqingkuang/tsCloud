from django.conf.urls.defaults import patterns, include, url
import apis

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'photodemo.views.home', name='home'),
    # url(r'^photodemo/', include('photodemo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^api/get_activities/$', apis.get_activities, name='ucam_get_activities'),
    url(r'^api/get_activity_content/(?P<pk>[\d]+)/$', apis.get_activity_content, name='ucam_get_activity_content'),
)
