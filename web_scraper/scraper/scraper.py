import sys
class Scraper():
    def __init__(self):
        self.data = {}
        self.info = {
            "id": None,
            "title": None,
            "company": None,
            "companyImg": None,
            "previewImg": None,
            "regions": [],
            "address": None,
            "date": None,
            "role": "intern",
            "types": [],
            "opening": None,
            "wage": None,
            "lowerWage": None,
            "upperWage": None,
            "currency": "TWD",
            "per": None,
            "jd": None,
            "requirements": None,
            "benefit": None,
            "contact": None,
            "labels": [],
            "source_url": None,
            "source_web": "",
        }
        self.PARENT_PAGE_URL = ""

    def scrape_job_from(self, beginning_page, ending_page):
        return 

    # scrape all pages
    def construct_db(self):
        self.scrape_job_from(1, 1)
        
    def update_db(self):
        self.scrape_job_from(1, 100)
    
