from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import include
from django.conf.urls.defaults import url

urlpatterns = patterns('',
    url(r'^$', 'doccloud.views.list', name='docs_list'),
    url(r'^list/$', 'doccloud.views.list', name='docs_list'),
    url(r'^detail/(?P<slug>[\w-]+)/$', 'doccloud.views.detail',
        name='docs_detail'),
    url(r'^create/$', 'doccloud.views.create', name='docs_create'),
    url(r'^upload/$', 'doccloud.views.upload', name='docs_upload'),
)
