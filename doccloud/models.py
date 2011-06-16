from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from datetime import datetime
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField
from documents.utils import generate_document_path


def parse_file_name(file_path):
    items = file_path.split('/')
    return items[len(items) - 1]


class Document(models.Model):
    #see documentcloud api https://www.documentcloud.org/help/api
    PRIVACY_LVLS = (
    ('private', 'Private (only viewable by those with permission to this doc)'),
    ('public', 'Public (viewable by anyone)'),
    ('organization', 'Organization (viewable by users in your organization)')
    )
    file = models.FileField(upload_to=generate_document_path)
    slug = AutoSlugField(populate_from=('title',))
    user = models.ForeignKey(User, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = CreationDateTimeField(db_index=True)
    updated_at = models.DateTimeField(editable=False, blank=True, db_index=True)
    dc_id = models.CharField(max_length=300, blank=True, null=True)
    dc_url = models.URLField(verify_exists=False, max_length=200, null=True, blank=True)
    access_level = models.CharField(max_length=32, choices=PRIVACY_LVLS)

    class Meta:
        verbose_name_plural = 'Documents'
        ordering = ['created_at']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.dc_url

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Document, self).save(*args, **kwargs)

    def dc_link(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.dc_url, "document cloud link")

    def aws_link(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.get_absolute_url(), "local link")
