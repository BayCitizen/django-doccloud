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

def get_dc_file(id):
    t_client = get_client()
    return t_client.documents.get(id)

def put_file(file, title, access_level):
    t_client = get_client()
    dc_obj = t_client.documents.upload(pdf=file, title=title,\
     access=access_level, secure=True)
    return (dc_obj.id, dc_obj.canonical_url)

def rm_file(id):
    try:
        get_dc_file(id).delete()
    except Exception as e: 
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
        super(DocumentCloudProperties, self).__init__(*args, **kwargs)
        #set values l8r so values aren't overwritten
        if vals != None:
            self.dc_id = vals[0]
            self.dc_url = vals[1]

    def update_access(self, access):
        if self.dc_id == None and self.dc_url == None:
            return False #obj not set yet
        try: 
            dc_obj = get_dc_file(self.dc_id)
            dc_obj.access = access
            dc_obj.save()
        except Exception as e:
            return False #taking suggestions on handling mgmt issues n admin

    def delete(self, *args, **kwargs):
        #no effective way of dealing with errors on DC cloud side
        #unless we create a custom template for managing documents 
        rm_file(self.dc_id)
        #so if rm_file don't complete we orphan the dc cloud doc
        super(DocumentCloudProperties, self).delete(*args, **kwargs)

class Document(models.Model):
    """
    see documentcloud api https://www.documentcloud.org/help/api
    upload_to path is ...
    https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload_to
    """
    file = models.FileField(upload_to=settings.DOCUMENTS_PATH, max_length=255)
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
        if self.dc_properties != None:
            return self.dc_properties.dc_url
        return self.file.url

    def connect_dc_doc(self):
        dc_props = DocumentCloudProperties(file=self.file, title=self.title,\
         access_level=self.access_level)
        dc_props.save()
        self.dc_properties = dc_props

    def delete(self, *args, **kwargs):
        self.dc_properties.delete()
        if self.dc_properties != None:
            return #document didn't delete, admin view error msgs?
        super(Document, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Document, self).save(*args, **kwargs)

    def link(self):
        return '<a href="%s" target="_blank">%s</a>' %\
         (self.get_absolute_url(), "link")
