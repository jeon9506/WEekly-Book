from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.shareTodayBook

## HTML 화면 보여주기
@app.route('/')
def main():
    return render_template('index.html')

# 도서 상세페이지(Read)
@app.route('/viewDetail/<book_id>')
def view_detail(book_id):
    # book_id_receive = request.args.get("book_id_give")
    # print(book_id_receive)

    return render_template("detailBook.html", book_id=book_id)

# 도서 상세페이지(Read)
@app.route('/readComment', methods=['GET'])
def read_comment():
    comments = list(db.comments.find({}))
    return jsonify({'result': 'success', 'details': comments})

# 도서 댓글 등록(Create)
@app.route('/createComment', methods=['POST'])
def create_comment():
    user_id_receive = request.form['user_id_give']
    book_id_receive = request.form['book_id_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = request.get(book_id_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    doc = {
        'userId' : user_id_receive,
        'bookId' : book_id_receive,
        'comment': comment_receive
    }
    db.articles.insert_one(doc)

    return jsonify({'msg':'댓글이 등록되었습니다!'})

# 도서 댓글 삭제(delete)
@app.route('/delComment', methods=['POST'])
def delete_comment():
    user_id_receive = request.form['user_id_give']
    book_id_receive = request.form['book_id_give']

    # commentObject key값 받기

    doc = {
        'userId':user_id_receive,
        'bookId':book_id_receive
    }

    db.articles.delete_one(doc)

    return jsonify({'msg':'댓글이 삭제되었습니다!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)