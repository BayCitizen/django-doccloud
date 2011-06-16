from django.contrib import admin
from django.db import models

from documentcloud import DocumentCloud
from documentcloud.MultipartPostHandler import getsize
from docs.models import Document

from django.conf import settings

class DocumentAdmin(admin.ModelAdmin):
    exclude = ('user', 'dc_id', 'dc_url')
    client = None

    def get_dc_client(self):
        if self.client == None:
            self.client = DocumentCloud(settings.DOCUMENTCLOUD_USERNAME,\
             settings.DOCUMENTCLOUD_PASS)
        return self.client
    
    def save_new(self, obj):    
        obj.save()
        t_client = self.get_dc_client()
        dc_obj = t_client.documents.upload(pdf=obj.file, title=obj.title,\
         access=obj.access_level, secure=True)
        obj.dc_id = dc_obj.id
        obj.dc_url = dc_obj.canonical_url
        obj.save()

    def save_model(self, request, obj, form, change):
        if len(form.files) > 0 and obj.updated_at == None:
            #file, obj are new
            obj.user = request.user
            self.save_new(obj)
        elif len(form.files) > 0 and obj.updated_at != None:
            #object has been updated, look for file changes
            n_file = form.files['file']
            n_file_sz = getsize(n_file)
            n_file_hdr = n_file.read(512) if n_file_sz >= 512 else n_file.read()
            o_file = obj.file
            o_file_sz = getsize(o_file)
            o_file_hdr = o_file.read(512) if o_file_sz >= 512 else o_file.read()
        
            if o_file_hdr != n_file_hdr:
                #looks like the file is different (not looknin for change)
                t_client = self.get_dc_client()
                dc_obj = t_client.documents.get(obj.dc_id)
                dc_obj.delete()
                self.save_new(obj)
            else:
                #just attributes changed
                obj.save()
        else:
            obj.save()
       
    def delete_model(self, request, obj):
        t_client = self.get_dc_client()
        dc_obj = t_client.documents.get(obj.dc_id)
        dc_obj.delete()

admin.site.register(Document, DocumentAdmin)
