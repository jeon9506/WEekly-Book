from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.shareTodayNews

## HTML 화면 보여주기
@app.route('/')
def main():
    return render_template('index.html')

# 뉴스 상세페이지(Read) API
@app.route('/viewDetail', methods=['GET'])
def view_detail():
    details = list(db.orders.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'details': details})

## 댓글 등록
@app.route('/createComment', methods=['POST'])
def create_memo():
    user_id_receive = request.form['user_id_give']
    news_id_receive = request.form['news_id_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = request.get(news_id_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    doc = {
        'userId':user_id_receive,
        'newsId':news_id_receive,
        'comment': comment_receive,
    }
    db.articles.insert_one(doc)

    return jsonify({'msg':'저장이 완료되었습니다!'})

@app.route('/memo/delete', methods=['POST'])
def delete_memo():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    # print(url_receive)
    # print(comment_receive)

    doc = {
        'url':url_receive,
        'comment':comment_receive
    }

    db.articles.delete_one(doc)

    return jsonify({'msg': '삭제 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)