from django.shortcuts import render
from web_scraper.models import Job, Company, Wage, Content, Source
from django.http import HttpResponse
import datetime
# Create your views here.

def test_db(request):
    company = Company(
        name = 'NCCU',
        address = 'Taipei road',
    )


    job = Job(
        code = '001',
        date = datetime.datetime.now(),
        title= 'TA',
        role = 'Intern',
        company = company,
    )

    job.save()
    return HttpResponse(request, '1')
    
