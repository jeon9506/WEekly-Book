import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbbestseller

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://book.naver.com/bestsell/bestseller_list.naver?cp=kyobo',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

charts = soup.select('#section_bestseller > ol > li')

desc = []
for index in range(0, 25):
    desc_data = soup.find('dd', {'id': "book_intro_" + str(index)}).text
    desc_total = (desc_data[4:100] + "...")
    desc.append(desc_total)
    for i in range(len(desc)):
        desc[i] = desc[i].replace('\n', '')

for chart in charts:
    title = chart.select_one("dl > dt > a").text
    author = chart.select_one("dl > dd > a").text
    ha = ''

    if chart.select_one("#book_intro_1") is not None:
        ha = chart.select_one("#book_intro_1")



    print(ha)

    doc = {
        'title': title,
        'author': author,
    }

