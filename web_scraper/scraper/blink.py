import requests
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import copy
from . import scraper

# https://www.blink.com.tw/jobs/list/?tab=new
class Scraper(scraper.Scraper):
	def __init__(self):
		super().__init__()
		self.info['source_web'] = 'Blink'
		self.PARENT_PAGE_URL = "https://www.blink.com.tw/jobs/list/?page={page}&tab=new"

	def scrape_job_from(self, beginning_page=1, ending_page=1):
		if beginning_page < 1 or ending_page < 1 or ending_page < beginning_page:
			beginning_page = 1
			ending_page = 1

		for page in range(beginning_page, ending_page + 1):
			res = requests.get(self.PARENT_PAGE_URL.format(page=page))
			bs4 = BeautifulSoup(res.text, "lxml")

			job_list = bs4.select(".to-job-intro")
			if len(job_list) > 0:
				for job in job_list:
					job_id = self.add_job_info("https://www.blink.com.tw" + job['href'])
					self.data[job_id]['labels'] = [tag.text.strip('#') for tag in job.select(".orange-tag")]

					previewImg_style = job.find("div", class_="img-inner")['style']
					start_index = previewImg_style.index('(') + 2
					end_index = previewImg_style.index(')') - 1
					if previewImg_style[start_index:end_index] != "https://www.blink.com.tw/static/images/new_blink_bear_na2.png":
						self.data[job_id]['previewImg'] = previewImg_style[start_index:end_index]
			else:
				break

	def add_job_info(self, url):
		res = requests.get(url)
		bs4 = BeautifulSoup(res.text, "lxml")

		job_info = copy.deepcopy(self.info)
		job_info['source_url'] = url
		splited_url = url.split('/')
		job_info['id'] = "blink_" + splited_url[-2]
		# no region, type
		detail_item_created_span = bs4.find('span', class_='detail-item created')
		if detail_item_created_span is not None:
			detail_item_span = detail_item_created_span.find_all('span')
		else:
			detail_item_span = bs4.select('.detail span')
		job_info['company'] = detail_item_span[0].text.strip()
		post_date = detail_item_span[1].text
		if "天之前" in post_date:
			post_date = datetime.now() - timedelta(days=int(post_date.replace('天之前', '').strip()))
			post_date = datetime.strptime(post_date.strftime("%Y-%m-%d"),"%Y-%m-%d")
		elif "小時之前":
			post_date = datetime.now() - timedelta(hours=int(post_date.replace('小時之前', '').strip()))
			post_date = datetime.strptime(post_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
		else: # 舊文章直接寫日期
			post_date = datetime.strptime(post_date[:10],'%Y-%m-%d')	
		job_info['date'] = post_date

		job_info['companyImg'] = bs4.find("div", class_="logo").find("img")['src']
		if bs4.find("div", class_="address") is not None:
			job_info["address"] = bs4.find("div", class_="address").text.strip()
		if bs4.find("div", class_="need") is not None:
			splited_opening = bs4.find("div", class_="need").text.split('~')
			if len(splited_opening) == 2:
				job_info['opening'] = splited_opening[1].replace('人', '').strip()
			else:
				job_info['opening'] = splited_opening[0].replace('人', '').strip()[-1]
		if bs4.find("div", class_="pay") is not None:
			job_info['wage'] = bs4.find("div", class_="pay").text.strip()
			splited_wage = job_info['wage'].split('/')
			job_info['lowerWage'] = job_info['upperWage'] = int(splited_wage[0].strip('$').strip())
			striped_per = splited_wage[1].strip()
			if striped_per == "時薪":
				per = "小時"
			elif striped_per == "日薪":
				per = "日"
			elif striped_per == "月薪":
				per = "月"
			elif striped_per == '年薪':
				per = '年'
			else:
				per = None
			job_info['per'] = per

		# content
		job_info['title'] = bs4.find("div", class_="title").find("h1").text.strip()	
		content_item_list = bs4.select(".content-item")
		for content_item in content_item_list:
			content_item_key = content_item.find("h2").text.strip()
			br_permition = True
			content_item_value = ''
			for tag in content_item.find_all():
				text = tag.text.replace("\xa0", "")
				if tag.name == 'p' and len(text) > 0:
					br_permition = True
					content_item_value += tag.text.strip()
				elif tag.name == 'br' and br_permition == True:
					br_permition = False
					content_item_value += '\n'

			if content_item_key == '工作資訊' or content_item_key == '工作內容':
				if job_info['jd'] == None:
					job_info['jd'] = content_item_value
				else:
					job_info['jd'] += ('/n' + content_item_value)
			elif content_item_key == '職缺需求':
				job_info['requirements'] = content_item_value
			elif content_item_key == '其他福利':
				job_info['benefit'] = content_item_value

		self.data[job_info['id']] = job_info
		return job_info['id']


if __name__ == '__main__':
	spider = Scraper()
	spider.scrape_job_from(1,1)
	#a = spider.add_job_info(url="https://www.blink.com.tw/jobs/list/94018/")
	#print(spider.data)

