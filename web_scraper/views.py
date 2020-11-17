from django.shortcuts import render
from web_scraper.models import Job, Company, Wage, Content, Source
from django.http import HttpResponse
import datetime
from .scraper import blink, cakeResume, oneZeroFour, yourator
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
     
def construct_db(request):
    #spider_list = [blink.Scraper(), yourator.Scraper(), cakeResume.Scraper(), oneZeroFour.Scraper()]
    spider = oneZeroFour.Scraper()
    spider.construct_db()
    for value in spider.data.values():
        save_to_db(value)

    return (HttpResponse(request, 1))


def update_db():
    return

def save_to_db(data):
    company = Company(
        name = data['company'],
        address = data['address'],
        img = data['companyImg'],
    )
    wage = Wage(
        wage = data['wage'],
        lowerWage = data['lowerWage'],
        upperWage = data['upperWage'],
        currency = data['currency'],
        per = data['per'],
    )
    content = Content(
        jd = data['jd'],
        requirements = data['requirements'],
        benefit = data['benefit'],
    )
    source = Source(
        url = data['source_url'],
        web = data['source_web'],
    )
    job = Job(
        code = data['id'],
        date = data['date'],
        title= data['title'],
        role = data['role'],
        company = company,
        previewImg = data['previewImg'],
        wage = wage,
        opening = data['opening'],
        regions = data['regions'],
        types = data['types'],
        labels = data['labels'],
        content = content,
        source = source,
    )
    job.save()
    


    
