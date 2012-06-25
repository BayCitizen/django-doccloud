from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from doccloud.forms import DocCloudDocForm
from doccloud.models import DocumentCloudProperties
from doccloud.models import Document
from django.contrib.auth.decorators import login_required

#@login_required
def create(request, template_name='upload.html'):
    context = {}
    context['form'] = DocCloudDocForm()
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def list(request, template_name='list.html'):
    context = {}
    context['objects'] = Document.objects.all()
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def detail(request, slug, template_name='detail.html'):
    '''
    Documents where access_level==Private will not appear in the detail page
    unless the user is logged in.  Some JS logic will need to be added to the template
    to check if the url: 
    http://www.documentcloud.org/documents/{{document.dc_properties.dc_id}}.js exists
    else fall back on the locally stored documents or use the secure url:
    https://www.documentcloud.org/documents/{{document.dc_properties.dc_id}}.js
    '''
    context = {}
    context['document'] = get_object_or_404(Document, slug=slug)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

#user field can be null so login not necessarily required
#@login_required
def upload(request, template_name='upload.html'):
    context = {}
    try:
        if request.method == 'POST':
            dc_form = DocCloudDocForm(request.POST, request.FILES)
            dc_form.user = request.user
            if dc_form.is_valid():
                model = dc_form.save(commit=False)
                #model.user = request.user
                model.connect_dc_doc()#queue for background processing here
                model.save()
                return redirect('docs_list')
            else:
                context['form'] = dc_form
                return render_to_response('upload.html', context, context_instance=RequestContext(request))
        else:
            return render_to_response('upload.html', context, context_instance=RequestContext(request))
    except Exception as e:
        print e#need logger
    return render_to_response(template_name, context, context_instance=RequestContext(request))