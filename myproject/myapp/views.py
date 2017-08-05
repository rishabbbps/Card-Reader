# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from google.cloud import vision
from google.cloud import language
import re
from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('myproject.myapp.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form
    # Load documents for the list page
    documents = Document.objects.all()

    doc=[]
    for i in xrange(0,len(documents)):
        img='/home/rishab/Desktop/goapp/visitCards/myproject/myproject/media/'
        img1 = str(documents[i].docfile)
        img = img+img1
        # print img
        ANY_URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
        Ph2 = r'\d{3}[-\.\s]??\d{4}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{6}[-\.\s]??\d{4}'
        Ph3 = r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'
        client = vision.Client()
        with open(img, 'rb') as image_file:
            image = client.image(content=image_file.read())
        texts = image.detect_text()
        client = language.Client()
        document = client.document_from_text(texts[0].description)
        ent_analysis = document.analyze_entities()
        dir(ent_analysis)
        entities = ent_analysis.entities
        location = ""
        person = ""
        company = ""
        for e in entities:
            if (e.entity_type == 'LOCATION'):
                location = location + " " + e.name
            if (e.entity_type == 'PERSON'):
                person = person + " " + e.name
            if (e.entity_type == 'ORGANIZATION'):
                company = company + " " + e.name
        email_ids = re.findall(ANY_URL_REGEX, texts[0].description)
        emails = filter(None, email_ids[0])
        Document.emails = [str(x) for x in emails]
        str5 = re.sub(r'\W+', '', texts[0].description)
        zipcode = re.findall(r'\D\d{6}\D', str5)
        Document.zipcode = zipcode[0][1:-1]

        phone_nos2 = re.findall(Ph2, texts[0].description)
        phone_nos3 = re.findall(Ph3, texts[0].description)

        phone_nos2 = [str(x) for x in phone_nos2]
        phone_nos3 = [str(x) for x in phone_nos3]
        phones = phone_nos2 + phone_nos3
        Document.phones = reduce(lambda l, x: l.append(x) or l if x not in l else l, phones, [])

        Document.location = str(location)
        Document.person = str(person)
        Document.company = str(company)

        x=[Document.location,Document.person,Document.company,Document.zipcode,Document.emails,Document.phones]
        doc.append(x)

    return render_to_response(
            'myapp/list.html',
            {'documents': zip(documents,doc), 'form': form},
            context_instance=RequestContext(request)
        )
