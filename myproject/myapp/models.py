from django.db import models


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.phones = ''
        self.location = ''
        self.zipcode = ''
        self.person = ''
        self.company = ''
        self.emails = ''

