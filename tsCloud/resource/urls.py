from django.conf.urls.defaults import patterns, include, url
import views, apis

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'photodemo.views.home', name='home'),
    # url(r'^photodemo/', include('photodemo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.HomeView.as_view(), name='resource_home'),
    url(r'^list/$', views.ResourceListView.as_view(), name='resource_list'),
    url(r'^download/(?P<slug>[-\w]+)/$', views.download, name='resource_download'),
    url(r'^submit/(?P<category_slug>[-\w]+)/$', views.submit, name='resource_submit'),
    url(r'^(?P<slug>[-\w]+)/$', views.ResourceDetailView.as_view(), name='resource_detail'),

    url(r'^api/help.html$', apis.help),
    url(r'^api/(?P<slug>[-\w]+)/generate_short_url.json$', apis.generate_short_url),
    url(r'^api/get_categories.(?P<format>[-\w]+)$', apis.get_categories),
    url(r'^api/(?P<bucket_name>[-\w]+)/get_storage_token.json$', apis.get_storage_token),
    url(r'^api/(?P<slug>[-\w]+)/get_categories.(?P<format>[-\w]+)$', apis.get_categories),
    url(r'^api/(?P<slug>[-\w]+)/get_resources.(?P<format>[-\w]+)$', apis.get_resources),
)
