BayCitizen / django-doccloud
===========================

This package provides a reusable Django app to facilitate uploads
and display of documents hosted on the DocumentCloud service

Install with PIP:
	pip install django-doccloud

Examples of how to use this package can be found in
	doccloud/views.py and doccloud/templates/*

Getting Started
===========================
Your settings.py file needs three variables.

Provide credentials and a path to save the document locally

	DOCUMENTS_PATH = os.path.join(MEDIA_ROOT, 'documents')

	DOCUMENTCLOUD_USERNAME='****'

	DOCUMENTCLOUD_PASS='****'


Add the urls to your project's urls.py file:

    (r'^docs/', include('doccloud.urls')),

The example templates assume you have the following template loader

    'django.template.loaders.app_directories.Loader',

Add 'doccloud' to your installed apps list in settings.py

Start your server and navigate to host:port/docs/

A few notes
===========================
Documents deleted using the admin interface will attempt to remove themselves
from DocumentCloud but in the case of a failure, the DocumentCloud doc
will be orphaned

doccloud/admin.py contains the admin form

doccloud/forms.py has a model form you can use on any page

doccloud/views.py contains an example using the model form

doccloud.models.Document.connect_dc_doc() uploads the doc to 
DocumentCloud.  For larger documents that can take some time
upload, this function should be run async with celery/rabbitmq
or the like

Private documents and large documents that have not finished processing 
in DocumentCloud will not appear on the templates/detail.html page
unless the user is logged in to DocumentCloud.  Some JS code could 
test to see if the document's doccloud url exist otherwise fall
back on the locally stored document.

More on this package at: http://www.baycitizen.org/blogs/sandbox/djangodocumentcloud-integration-theres/
