from django.db import models
from django.conf import settings
from django.contrib import admin
from documentcloud.MultipartPostHandler import getsize
from doccloud.models import Document


class DocumentAdmin(admin.ModelAdmin):
    exclude = ('user', 'dc_properties', )

    def save_model(self, request, obj, form, change):
        if len(form.files) > 0 and obj.updated_at is None:
            #file, obj are new
            obj.user = request.user
            obj.connect_dc_doc()
            obj.save()
        elif len(form.files) > 0 and obj.updated_at is not None:
            #object has been updated, look for file changes
            n_file = form.files['file']
            n_file_sz = getsize(n_file)
            n_file_hdr = n_file.read(512) if n_file_sz >= 512\
                else n_file.read()
            o_file = obj.file
            o_file_sz = getsize(o_file)
            o_file_hdr = o_file.read(512) if o_file_sz >= 512\
                else o_file.read()

            if o_file_hdr != n_file_hdr:
                #our 512 byte comparison tells us the docs differ
                obj.dc_properties.delete()
                obj.connect_dc_doc()
                obj.save()
        else:
            obj.dc_properties.update_access(obj.access_level)
            obj.save()

admin.site.register(Document, DocumentAdmin)
