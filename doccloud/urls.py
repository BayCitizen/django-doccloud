from django.conf.urls.defaults import patterns, include, url

#to use
#url(r'^docs/', include('doccloud.urls')),

urlpatterns = patterns('',
    url(r'^create/$', 'doccloud.views.index', name='docs_index'),
    url(r'^upload/$', 'doccloud.views.upload', name='docs_upload'),
)