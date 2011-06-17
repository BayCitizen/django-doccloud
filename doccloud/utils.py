import os
import documents
import docs
from datetime import datetime
from documentcloud import DocumentCloud
from documentcloud_docs.models import parse_file_name
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings


def generate_document_path(instance, filename):
    return u"uploaded/documents/%s/%s/%s/%s" % (datetime.now().year,\
     datetime.now().month, instance.slug, filename)


def upload_docs_dc():
    docs = list(documents.models.Document.objects.all())
    user = User.objects.get(email='dev@baycitizen.org')
    t_client = DocumentCloud(settings.DOCUMENTCLOUD_USERNAME,\
     settings.DOCUMENTCLOUD_PASS)
    for doc in docs:
        print 'attempting title=%s' % doc.title
        this_doc = docs.models.Document(file=doc.file, user=user,\
         title=doc.title, created_at=datetime.now())
        this_doc.save()
        fn = parse_file_name(this_doc.file.name)
        extension = fn.split('.')
        #see  errors function
        dc_obj = t_client.documents.upload(pdf=this_doc.file, title=fn,\
         access='public', secure=True)
        this_doc.dc_id = dc_obj.id
        this_doc.dc_url = dc_obj.canonical_url
        this_doc.save()
