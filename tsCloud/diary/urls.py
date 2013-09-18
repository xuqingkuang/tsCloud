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
    url(r'^$', views.all, name='all_diaries'),

    url(r'^api/update_emotion/$', api.update_emotion),
    url(r'^api/post_message/$', api.post_message),
    url(r'^api/receive_messages/$', api.receive_messages),
)
