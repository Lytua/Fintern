import requests
from bs4 import BeautifulSoup
import copy
from . import scraper
# https://www.cakeresume.com/jobs?q=%E5%AF%A6%E7%BF%92%E7%94%9F&locale=zh-TW&page=1
class Scraper(scraper.Scraper):
	def __init__(self):
		super().__init__()
		self.info['source_web'] = 'CakeResume'
		self.PARENT_PAGE_URL = "https://www.cakeresume.com/jobs?q=%E5%AF%A6%E7%BF%92%E7%94%9F&locale=zh-TW&page={page}"

	def scrape_job_from(self, beginning_page=1, ending_page=1):	
		if beginning_page < 1 or ending_page < 1 or ending_page < beginning_page:
			beginning_page = 1
			ending_page = 1

		for page in range(beginning_page, ending_page + 1):
			res = requests.get(self.PARENT_PAGE_URL.format(page=page))
			bs4 = BeautifulSoup(res.text, "lxml")
			
			job_list = bs4.select("a.job-link")
			if len(job_list) > 0:
				for job in job_list:
					self.add_job_info(job['href'])
			else:
				break

	def add_job_info(self, url):
		res = requests.get(url)
		bs4 = BeautifulSoup(res.text, "lxml")
		# no address
		job_info = copy.deepcopy((self.info))
		job_info['source_url'] = url
		job_info['id'] = "cakeResume_" + url.replace("https://www.cakeresume.com/companies/",'')
		job_info['title'] = bs4.find("div", class_="heading").find("h1").text.strip()
		job_info['company'] = bs4.find("div", class_="heading").find("h2").text.strip()
		job_info['companyImg'] = bs4.find("div", class_="job").find("img", class_="logo")['src']
		if bs4.find("div", class_='page-work-env-imgs-container') is not None:
			job_info['previewImg'] = bs4.find("div", class_='page-work-env-imgs-container').find("a")['href']
		job_info['date'] = bs4.find("div", class_="meta-info").find("span").text.strip()
		job_info['types'] = bs4.find("div", class_="meta-info").find("a").text.strip().split(" » ")
		job_info['opening'] = bs4.find("span", class_="number-of-openings").text.strip()

		for location in bs4.select("#locations a"):
			job_info['regions'].append(location.text.strip())

		if bs4.find("div", id="salary") is not None:
			job_info['currency'] = bs4.find("div", id="salary").find("span", class_="currency").text.strip()
			per = bs4.find("div", id="salary").find("span", class_="per").text.strip()
			wage = bs4.find("div", id="salary").find("span", class_="job-salary").text.strip()
			job_info['wage'] = wage

			for replaced_char in ['~', job_info['currency']]:
				wage = wage.replace(replaced_char, per)
			splited_wage = wage.split(per)

			if splited_wage[0].strip()[-1] == 'K':
				lowerWage = 1000 * float(splited_wage[0].strip().strip('K'))
			else:
				lowerWage = float(splited_wage[0].strip())
			job_info['lowerWage'] = lowerWage

			if splited_wage[1].strip()[-1] == 'K':
				upperWage = 1000 * float(splited_wage[0].strip().strip('K'))
			else:
				upperWage = float(splited_wage[0].strip())
			job_info['upperWage'] = upperWage
			job_info['per'] = splited_wage[3].strip()
		else:
			pass

		job_info['jd'] = str(bs4.find("div", id="job-description"))
		job_info['requirements'] = str(bs4.find("div", id="requirements"))

		for label in bs4.select("a.label"):
			job_info['labels'].append(label.text.strip())

		self.data[job_info['id']] = job_info

if __name__ == '__main__':
	spider = Scraper()
	spider.scrape_job_from(25,30)
	#spider.add_job_info("https://www.cakeresume.com/companies/funnow/jobs/2ef708")
	#print(spider.data)
