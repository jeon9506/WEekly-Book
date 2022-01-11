from bson import ObjectId
from flask import Flask, render_template, jsonify, request, url_for, redirect

import jwt
import datetime
import hashlib
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

#DB경로 설정
client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.shareTodayBook

# 로그인 회원가입 관련 api

# 로그인시
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


#로그인 기능 버튼 클릭시 POST 받는 메서드
@app.route('/loginCheck', methods=['POST'])
def loginCheck():
    # 로그인
    userId_receive = request.form['userId_give']
    password_receive = request.form['password_give']

    #DB에 저장된 암호화된 비밀번호와 사용자가 입력한 비밀번호가 일치 하는지 확인
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    #사용자가 입력한 ID와 DB의 ID가 일치하는지 확인
    result = db.user.find_one({'userId': userId_receive, 'password': pw_hash})

    #is not None 조회결과가 있다면 = 로그인 성공
    if result is not None:
        payload = {
         'id': userId_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 1)  # 로그인 1시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})

    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원 가입 버튼 클릭시 POST 메서드
@app.route('/joinCheck', methods=['POST'])
def joinCheck():
    userId_receive = request.form['userId_give']
    password_receive = request.form['password_give']
    #전달 받은 비밀번호 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    nickname=request.form['nickname_give']
    doc = {
        "userId": userId_receive,           # 아이디
        "password": password_hash,          # 비밀번호
        "nickname": nickname                # 닉네임
    }
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})

#회원 가입시 ID 중복 확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userId_receive = request.form['userId_give']
    exists = bool(db.user.find_one({"userId": userId_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/main')
def main():
    # 로그인 정보 저장 (토큰)
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#mypage로 이동하기
@app.route('/mypage')
def mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})
        return render_template('mypage.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 회원가입 관련 api 끝

# 초기화면 로그인 화면으로 이동 함
@app.route('/')
def first():
    return render_template('login.html')

# 도서 상세페이지(Read)
@app.route('/viewDetail')
def view_detail():
    token_receive = request.cookies.get('mytoken')

    try:
        # 로그인 정보
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})

        # 책 크롤링 정보
        book_id = request.args.get("book_id")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(f'https://book.naver.com/bookdb/book_detail.naver?bid={book_id}', headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        book_name = soup.select_one('#container > div.spot > div.book_info > h2 > a').text.strip()
        book_img_url = soup.select_one('#container > div.spot > div.book_info > div.thumb.type_end > div > a > img')["src"]
        author = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(2) > a.N\=a\:bil\.publisher').text.strip()
        public_date = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(2)').previous_element.strip()
        page = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(3) > span:nth-child(2)').previous_element.strip()
        isbn = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(3) > span:nth-child(4)').previous_element.strip()
        plate_type = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(3) > em:nth-child(5)').next_element.next_element.strip()
        book_score = soup.select_one('#txt_desc_point > strong:nth-child(2) > span').previous_element.strip()
        book_contents = soup.select_one('#bookIntroContent')

        #print(book_name, book_img_url, author, public_date, page, isbn, plate_type, book_score, book_contents)

        book_info = {
            'book_name': book_name,
            'book_img_url': book_img_url,
            'author': author,
            'public_date': public_date,
            'page': page,
            'isbn': isbn,
            'plate_type': plate_type,
            'book_score': book_score,
            'book_content': book_contents
        }

        # 댓글 정보
        comments = list(db.comment.find({}))

        for comment in comments :
            comment['comment_id'] = str(comment["_id"])
            print(comment['comment_id'])

        # print(comments)

        return render_template("detailBook.html", book_id=book_id, book_info=book_info, user_info=user_info, comments= comments)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 도서 댓글 등록(Create)
@app.route('/createComment', methods=['POST'])
def create_comment():
    user_id_receive = request.form['user_id_give']
    nickname_receive = request.form['nickname_give']
    book_id_receive = request.form['book_id_give']
    comment_receive = request.form['comment_give']

    doc = {
        'userId' : user_id_receive,
        'nickname': nickname_receive,
        'bookId' : book_id_receive,
        'comment': comment_receive
    }
    db.comment.insert_one(doc)

    return jsonify({'msg':'댓글이 등록되었습니다!'})

# 도서 댓글 삭제(delete)
@app.route('/delComment', methods=['POST'])
def delete_comment():
    user_id_receive = request.form['user_id_give']
    comment_id_receive = request.form['comment_id_give']

    # commentObject key값 받기

    doc = {
        '_id': ObjectId(comment_id_receive),
        'userId':user_id_receive
    }

    db.comment.delete_one(doc)

    return jsonify({'msg':'댓글이 삭제되었습니다!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)