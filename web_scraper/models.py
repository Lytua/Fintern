from django.db import models
from mongoengine import Document, EmbeddedDocument, fields

# Create your models here.
class Company(EmbeddedDocument):
    name = fields.StringField(required=True)
    address = fields.StringField(null=True)
    img = fields.StringField(null=True)

class Wage(EmbeddedDocument):
    wage = fields.StringField(null=True)
    lowerWage = fields.FloatField(null=True)
    upperWage = fields.FloatField(null=True)
    currency = fields.StringField(null=True)
    per = fields.StringField(null=True)

class Content(EmbeddedDocument):
    jd = fields.StringField(null=True)
    requirements = fields.StringField(null=True)
    benefit = fields.StringField(null=True)

class Source(EmbeddedDocument):
    url = fields.StringField(required=True)
    web = fields.StringField(required=True)

class Job(Document):
    code = fields.StringField(required=True)
    date = fields.DateTimeField(required=True)
    role = fields.StringField(required=True)
    title = fields.StringField(required=True)
    company = fields.EmbeddedDocumentField(Company)
    previewImg = fields.StringField(null=True)
    wage = fields.EmbeddedDocumentField(Wage)
    opening = fields.StringField(null=True)
    regions = fields.ListField(fields.StringField())
    types = fields.ListField(fields.StringField())
    labels = fields.ListField(fields.StringField())
    content = fields.EmbeddedDocumentField(Content)
    source = fields.EmbeddedDocumentField(Source)
    meta = {'alias':'default', 'collection':'job'}


