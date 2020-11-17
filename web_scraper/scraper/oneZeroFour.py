import requests
from requests import Session
from bs4 import BeautifulSoup
import copy, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import selenium
from . import scraper
import os
# https://www.104.com.tw/area/job/search.cfm?addr=0&jobcat=0&indus=0&keyword=%E9%97%9C%E9%8D%B5%E5%AD%97&page=3&jobsource=job&sortField=APPEAR_DATE&sortMode=DESC
class Scraper(scraper.Scraper):
	def __init__(self):
		super().__init__()
		self.info['source_web'] = 'OneZeroFour'
		self.PARENT_PAGE_URL = 'https://www.104.com.tw/area/intern/search.cfm?addr=0&jobcat=0&indus=0&keyword=%E9%97%9C%E9%8D%B5%E5%AD%97&page={page}&jobsource=intern&sortField=APPEAR_DATE&sortMode=DESC'
		self.chromedriver_path = os.getcwd() + '/web_scraper/scraper/chromedriver'
	
	def scrape_job_from(self, beginning_page=1, ending_page=1):	
		if beginning_page < 1 or ending_page < 1 or ending_page < beginning_page:
			beginning_page = 1
			ending_page = 1

		for page in range(beginning_page, ending_page + 1):
			try:
				options = Options()
				options.set_headless(headless=True)
				# can use firefox
				driver = webdriver.Chrome(executable_path=self.chromedriver_path, chrome_options=options)
				driver.get(self.PARENT_PAGE_URL.format(page=page))
				bs4 = BeautifulSoup(driver.page_source, "lxml")

				job_list = bs4.select("div.joblist_cont")
				for job in job_list:
					job_url = "https://www.104.com.tw" + job.find("div", class_="jobname").find("a")['href']
					job_id = job_url.split('/')[4].replace("?jobsource=intern", "")

					res = requests.get(
						url='https://www.104.com.tw/job/ajax/content/' + job_id,
						headers={
							'Referer': job_url,
						}
					)

					self.add_job_info(json.loads(res.text)['data'], job_id, job_url)
			except selenium.common.exceptions.UnexpectedAlertPresentException:
				break

	def add_job_info(self, job_data, job_id, job_url):
		job_info = copy.deepcopy((self.info))
		job_info['id'] = 'oneZeroFour_' + job_id
		job_info['source_url'] = job_url
		job_info['title'] = job_data['header']['jobName']
		job_info['company'] = job_data['header']['custName']
		job_info['companyImg'] = job_data['custLogo']
		if len(job_data['environmentPic']['environmentPic']) > 0:
			job_info['previewImg'] = job_data['environmentPic']['environmentPic'][0]['link']
		job_info['regions'].append(job_data['jobDetail']['addressRegion'])
		job_info['address'] = job_data['jobDetail']['addressRegion'] + job_data['jobDetail']['addressDetail']
		job_info['date'] = job_data['header']['appearDate'].replace('/', '-')
		job_info['types'] = [job_type['description'] for job_type in job_data['jobDetail']['jobCategory']]

		splited_opening = job_data['jobDetail']['needEmp'].replace('人', '').split('~')
		if len(splited_opening) == 1:
			opening = splited_opening[0].strip()
		elif len(splited_opening) == 2:
			opening = splited_opening[-1].strip()
		job_info['opening'] = opening

		job_info['wage'] = job_data['jobDetail']['salary']
		job_info['lowerWage'] = float(job_data['jobDetail']['salaryMin'])
		job_info['upperWage'] = float(job_data['jobDetail']['salaryMax'])
		salaryType = job_data['jobDetail']['salaryType']
		if salaryType == 30:
			per = '小時'
		elif salaryType == 40:
			per = '日'
		elif salaryType == 50:
			per = '月'
		elif salaryType == 60:
			per = '年'
		else:
			per = None
		job_info['per'] = per

		job_info['jd'] = job_data['jobDetail']['jobDescription']
		job_info['requirements'] = self.get_requirements_text(job_data['condition'])
		job_info['benefit'] = job_data['welfare']['welfare']

		job_info['labels'] += [workType for workType in job_data['jobDetail']['workType']]
		job_info['labels'].append(job_data['jobDetail']['workPeriod'])
		job_info['labels'] += [specialty['description'] for specialty in job_data['condition']['specialty']]

		self.data[job_info['id']] = job_info

	def get_requirements_text(self, condition):
		requirements = []
		delimiter = '、'
		new_line = '\n'
		requirements.append('接受身份:' + ' '*1 + delimiter.join([role['description'] for role in condition['acceptRole']['role']]))
		requirements.append('工作經歷:' + ' '*1 + condition['workExp'])
		requirements.append('學歷要求:' + ' '*1 + condition['edu'])
		requirements.append('科系要求:' + ' '*1 + delimiter.join([major for major in condition['major']]))

		language_text = '語文條件:'
		for index, language in enumerate(condition['language']):
			language_format = language['language'] + ' -- ' + language['ability']
			if index == 0:
				language_text += (' '*1 + language_format)
			else:
				language_text += ('\n' + ' '*6 + language_format)
		requirements.append(language_text)

		requirements.append('擅長工具:' + ' '*1 + delimiter.join([specialty['description'] for specialty in condition['specialty']]))
		requirements.append('工作技能:' + ' '*1 + delimiter.join([skill['description'] for skill in condition['skill']]))
		requirements.append('具備證照:' + ' '*1 + delimiter.join([certificate['description'] for certificate in condition['certificate']]))
		requirements.append('其他條件:' + new_line + condition['other'])

		requirements_text = new_line.join(requirements)
		return requirements_text

if __name__ == '__main__':
	spider = Scraper()
	spider.scrape_job_from(96,97)
	#spider.add_job_info("https://www.104.com.tw/job/71bdy?jobsource=job")
	#print(spider.data)
