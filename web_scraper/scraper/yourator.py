import requests
from bs4 import BeautifulSoup
import copy, json 
from datetime import date
from . import scraper
#import scraper
#https://www.yourator.co/api/v2/jobs?position[]=intern&page=2
class Scraper(scraper.Scraper):
	def __init__(self):
		super().__init__()
		self.info['source_web']= 'Yourator'
		self.info['date'] = date.today()
		self.PARENT_PAGE_URL = "https://www.yourator.co/api/v2/jobs?position[]=intern&page={page}"
		self.job_count = 0

	def scrape_job_from(self, beginning_page=1, ending_page=1):
		if beginning_page < 1 or ending_page < 1 or ending_page < beginning_page:
			beginning_page = 1
			ending_page = 1

		for page in range(beginning_page, ending_page + 1):
			res = requests.get(self.PARENT_PAGE_URL.format(page=page))
			res_data = json.loads(res.text)

			for job_data in res_data['jobs']:
				self.add_job_info(job_data)

			self.job_count += len(res_data['jobs'])
			# automated stopping
			if self.job_count >= res_data['total']:
				break

	def add_job_info(self, job_data):
		# no date, opening
		BASE_URL = "https://www.yourator.co"
		job_info = copy.deepcopy((self.info))
		job_info['source_url'] = BASE_URL + job_data['path']
		job_info['id'] = "yourator_" + str(job_data['id'])
		job_info['title'] = job_data['name']
		job_info['company'] = job_data['company']['brand']
		job_info['previewImg'] = job_data['company']['banner']
		job_info['regions'].append(job_data['country_name'])
		job_info['regions'].append(job_data['city'])

		for category in job_data['category']['name'].split('/'):
			job_info['types'].append(category.strip())

		for tag in job_data['tags']:
			job_info['labels'].append(tag['name'])

		try:
			job_info["wage"] = wage = job_data['salary']
			wage_start = wage.index('$')
			wage_end = wage.index('(')
			per_end = wage.index(')')

			splited_wage = wage[wage_start+1:wage_end].split('-')
			job_info["lowerWage"] = float(splited_wage[0].replace(',', '').strip())
			if splited_wage[1].strip() == '':
				job_info["upperWage"] = job_data["lowerWage"]
			else:
				job_info["upperWage"] = float(splited_wage[1].replace(',', '').strip())

			extracted_per = wage[wage_end+1:per_end]
			if extracted_per == "時薪":
				per = "小時"
			elif extracted_per == "日薪":
				per = "日"
			elif extracted_per == "月薪":
				per = "月"
			elif extracted_per == "年薪":
				per = "年"
			else:
				per = None
			job_info["per"] = per
		except: 
			pass

		res = requests.get(job_info['source_url'])
		bs4 = BeautifulSoup(res.text, "lxml")

		locations = bs4.select("p.basic-info__address")
		if len(locations) == 2:
			job_info['address'] = locations[1].text.strip()
		job_info['companyImg'] = bs4.find("div", class_="basic-info__title--subtitle").find("img", class_="basic-info__logo")['src']

		content_h2 = bs4.select(".job__content h2")
		content_section = bs4.select(".job__content section")

		for h2, section in zip(content_h2, content_section):
			h2_text = h2.text.strip()
			if h2_text == "工作內容":
				job_info['jd'] = str(section)
			elif h2_text == "條件要求":
				job_info['requirements'] = str(section)
			elif h2_text == "公司福利":
				job_info["benefit"] = str(section)

		self.data[job_info['id']] = job_info

if __name__ == '__main__':
	spider = Scraper()
	spider.scrape_job_from(1,1)
	#spider.add_job_info("https://www.yourator.co/companies/flow/jobs/13068")
	print(spider.data)
