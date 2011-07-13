from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from datetime import datetime
from documentcloud import DocumentCloud
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField


PRIVACY_LVLS = (
('private', 'Private (only viewable by those with permission to this doc)'),
('public', 'Public (viewable by anyone)'),
('organization', 'Organization (viewable by users in your organization)')
)

def get_client():
    return DocumentCloud(settings.DOCUMENTCLOUD_USERNAME,\
         settings.DOCUMENTCLOUD_PASS)

def put_file(file, title, access_level):
    t_client = get_client()
    dc_obj = t_client.documents.upload(pdf=file, title=title,\
     access=access_level, secure=True)
    return (dc_obj.id, dc_obj.canonical_url)

def rm_file(id):
    t_client = get_client()
    try:
        dc_obj = t_client.documents.get(id)
        dc_obj.delete()
        return True
    except Exception as e:
        print e
        return False

class DocumentCloudProperties(models.Model):
    dc_id = models.CharField(max_length=300, blank=False, null=False)
    dc_url = models.URLField(verify_exists=False, max_length=200, null=False, blank=False)

    def __init__(self, *args, **kwargs):
        vals = None
        if "file" in kwargs and "title" in kwargs and "access_level" in kwargs:
                file = kwargs.pop('file')
                title = kwargs.pop('title')
                access_level = kwargs.pop('access_level')
                vals = put_file(file, title, access_level)
                print vals
        super(DocumentCloudProperties, self).__init__(*args, **kwargs)
        #save l8r so values aren't overwritten !?!
        if vals != None:
            self.dc_id = vals[0]
            self.dc_url = vals[1]
        print 'after_super %s' % self.dc_id

    def delete(self, *args, **kwargs):
        if not rm_file(self.dc_id):
            return
        super(DocumentCloudProperties, self).delete(*args, **kwargs)

class Document(models.Model):
    """
    see documentcloud api https://www.documentcloud.org/help/api
    upload_to path is ...
    https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload_to
    """
    file = models.FileField(upload_to=settings.DOCUMENTS_PATH)
    slug = AutoSlugField(populate_from=('title',))
    user = models.ForeignKey(User, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = CreationDateTimeField(db_index=True)
    updated_at = models.DateTimeField(editable=False, blank=True, db_index=True)
    dc_properties = models.ForeignKey(DocumentCloudProperties, blank=True, null=True)
    access_level = models.CharField(max_length=32, choices=PRIVACY_LVLS)

    class Meta:
        verbose_name_plural = 'Documents'
        ordering = ['created_at']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.dc_properties.dc_url

    def connect_dc_doc(self):
        try:
            dc_props = DocumentCloudProperties(file=self.file, title=self.title,\
             access_level=self.access_level)
            print 'print id=%s' % dc_props.dc_id
            dc_props.save()
            self.dc_properties = dc_props
        except Exception as e:
            print e

    def delete(self, *args, **kwargs):
        self.dc_properties.delete()
        if self.dc_properties != None:
            return #document didn't delete
        super(Document, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Document, self).save(*args, **kwargs)

    def dc_link(self):
        return '<a href="%s" target="_blank">%s</a>' %\
         (self.dc_properties.dc_url, "document cloud link")

    def aws_link(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.get_absolute_url(), "local link")
