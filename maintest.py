import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.todayBook2


@app.route("/")
def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://book.naver.com/bestsell/bestseller_list.naver?cp=kyobo', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    charts = soup.select('#section_bestseller > ol > li')
    count = 0
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
        book_img = chart.select_one("div > div > a > img")['src']
        book_detail = chart.select_one("dl > dt > a")['href']
        bid = chart.select_one('a')['href'].split('?')[1].split('=')[1]

        doc = {
            'book_img': book_img,
            'book_detail': book_detail,
            'title': title,
            'author': author,
            'desc': desc[count],
            'bid': bid
        }
        count += 1

        bid_dup = db.todayBook2.find_one({'bid': bid})
        if bid_dup is None:
            print('~~ 같지않음 : ', bid)
            db.todayBook2.insert_one(doc)

    books = list(db.todayBook2.find({}, {'_id': False}))
    return render_template("index.html", books=books)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
