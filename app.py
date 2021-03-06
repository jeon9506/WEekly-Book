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
#client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@15.164.211.199', 27017)
db = client.shareTodayBook


# 초기화면 로그인 화면으로 이동 함
@app.route('/')
def first():
    # 기존 로그인 정보가 있는지 확인하기 위해 토큰에 있는 쿠키정보를 받아옴
    token_receive = request.cookies.get('mytoken')


    # 조건문을 통해 None이 아니면 main 으로 이동
    if(token_receive is not None):
        try:
            books = list(db.books.find({}, {'_id': False}))
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"userId": payload["id"]})
            return render_template("main.html",user_info=user_info, books=books)

        # 쿠키시간이 만료하거나 정보가 없을시 로그인 페이지로 이동하며 관련 메세지를 띄움
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    #로그인정보가 없으면 로그인 페이지로 이동
    else:
        return render_template('login.html')
# 로그인 회원가입 관련 api

# 로그인시 성공시,
# url/login로 강제로 이동시 토큰 검사 후에 토큰 보유시 다시 mainpage로 이동함
@app.route('/login')
def login():
    token_receive = request.cookies.get('mytoken')

    # 조건문을 통해 None이 아니면 main 으로 이동
    if (token_receive is not None):
        try:
            return redirect(url_for("main"))

        # 쿠키시간이 만료하거나 정보가 없을시 로그인 페이지로 이동하며 관련 메세지를 띄움
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        #login.html로 이동
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
    #입력으로 전달받은 아이디와 비밀번호 정보를 변수에 저장
    userId_receive = request.form['userId_give']
    password_receive = request.form['password_give']
    #전달 받은 비밀번호 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    nickname=request.form['nickname_give']

    #전달 받은 회원정보를 dictionary에 저장
    doc = {
        "userId": userId_receive,           # 아이디
        "password": password_hash,          # 비밀번호
        "nickname": nickname                # 닉네임
    }

    #insert문으로 db에 저장 시킴
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})

#회원 가입시 ID 중복 확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    #전달받은 ID를 변수에 저장
    userId_receive = request.form['userId_give']

    #전달받은 아이디를 조회후 결과를 전달함
    exists = bool(db.user.find_one({"userId": userId_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 메인 페이지
@app.route('/main')
def main():
    # 로그인 정보 저장 (토큰)
    token_receive = request.cookies.get('mytoken')

    #네이버 베스트셀러 사이트 스크래핑
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://book.naver.com/bestsell/bestseller_list.naver?cp=kyobo', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    charts = soup.select('#section_bestseller > ol > li')

    #책 소개(description) 데이터 리스트화
    #Description 리스트가 중복으로 Insert 되어 count 처리
    count = 0
    desc = []
    for index in range(0, 25):
        desc_data = soup.find('dd', {'id': "book_intro_" + str(index)}).text
        desc_total = (desc_data[4:100] + "...")
        desc.append(desc_total)
        #개행 제거
        for i in range(len(desc)):
            desc[i] = desc[i].replace('\n', '')

    #책 제목, 저자, 이미지, bid, 출판사 스크래핑
    for chart in charts:
        title = chart.select_one("dl > dt > a").text
        author = chart.select_one("dl > dd > a").text
        book_img = chart.select_one("div > div > a > img")['src']
        #book_detail = chart.select_one("dl > dt > a")['href']
        bid = chart.select_one('a')['href'].split('?')[1].split('=')[1]
        publisher = chart.select_one("dl > dd").text.split('|')[1].strip()

        doc = {
            'book_img': book_img,
            #'book_detail': book_detail,
            'title': title,
            'author': author,
            'desc': desc[count],
            'bid': bid,
            'publisher' : publisher
        }
        count += 1


        #데이터가 중복으로 db에 담겨 bid를 지표로 잡아 db에 bid가 존재하지 않을 때만 db에 저장
        bid_dup = db.books.find_one({'bid': bid})
        if bid_dup is None:
            print('~~ 같지않음 : ', bid)
            db.books.insert_one(doc)

    books = list(db.books.find({}, {'_id': False}))


    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})
        return render_template('main.html', user_info=user_info, books=books)
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

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get('https://book.naver.com/bestsell/bestseller_list.naver?cp=kyobo', headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        # description을 스크래핑 하기위한 작업을 해준다
        count = 0
        desc = []
        for index in range(0, 25):
            desc_data = soup.find('dd', {'id': "book_intro_" + str(index)}).text
            desc_total = (desc_data[4:100] + "...")
            desc.append(desc_total)
            for i in range(len(desc)):
                desc[i] = desc[i].replace('\n', '')

        # 도서 정보를 스크래핑 해서 scrappingBookList 리스트에 담는다
        booklist = soup.select('#section_bestseller > ol > li')
        scrappingBookList = [];

        for book in booklist:
            booklink = book.select_one('a')['href']
            bid = book.select_one('a')['href'].split('?')[1].split('=')[1]
            title = book.select_one("dl > dt > a").text
            author = book.select_one("dl > dd > a").text
            publisher = book.select_one("dl > dd").text.split('|')[1].strip()
            imgsrc = book.select_one('div> div > a > img')['src']
            doc = {
                'title': title,
                'author': author,
                'desc': desc[count],
                'imgsrc': imgsrc,
                'booklink': booklink,
                'bid': bid,
                'publisher':publisher
            }
            count += 1
            scrappingBookList.append(doc)


        # db에 bookmarks, books 테이블 정보를 가져옴
        bookmarks = list(db.bookmarks.find({}))
        books = list(db.books.find({}))

        # 접속한 사용자가 북마크한 도서를 uBookmarkList에 넣어준다
        uBookmarkList = []
        for book in books:
            for mark in bookmarks:
                if str(book['_id']) == mark['bookId'] and mark['userId'] == user_info['userId']:
                    uBookmarkList.append(book)

        # 도서 순위에 있는 도서와 bookmarks 테이블에 있는 도서의 title이 같은지 
        # 비교해서 에 담아준다
        userBookmarkList = []
        for sblist in scrappingBookList:
            for blist in uBookmarkList:
                if sblist['title'] == blist['title']:
                    sblist['id'] = str(blist['_id'])
                    userBookmarkList.append(sblist)


        # jinja2 템플릿을 활용하여 user_info에는 유저정보를 userBookmarkList에는 해당 사용자가 북마크한 도서정보를 담았다.
        return render_template('mypage.html', user_info=user_info, userBookmarkList=userBookmarkList)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 회원가입 관련 api 끝



# 도서 상세페이지(Read)
@app.route('/viewDetail')
def view_detail():
    token_receive = request.cookies.get('mytoken')

    try:
        # 로그인 정보
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})

        # 책 크롤링
        bid = request.args.get("bid")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(f'https://book.naver.com/bookdb/book_detail.naver?bid={bid}', headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        book_name = ''
        try:
            book_name = soup.select_one('#container > div.spot > div.book_info > h2 > a').text.strip()
        except AttributeError as e:
            if book_name == None:
                book_name = ''

        book_img_url = ''
        try:
            book_img_url = soup.select_one('#container > div.spot > div.book_info > div.thumb.type_end > div > a > img')["src"]
        except AttributeError as e:
            if book_img_url == None:
                book_img_url = ''

        author = ''
        try:
            author = soup.select_one('#container > div.spot > div.book_info > div.book_info_inner > div:nth-child(2)').text.strip()
        except AttributeError as e:
            if author == None:
                author = ''
        print('author : ' + author)

        book_score = ''
        try:
            book_score = soup.select_one('#txt_desc_point > strong:nth-child(2) > span').previous_element.strip()
        except AttributeError as e:
            if book_score == None:
                book_score = ''

        book_contents = ''
        try:
            book_contents = soup.select_one('#bookIntroContent')
        except AttributeError as e:
            if book_contents == None:
                book_contents = ''

        #print(book_name, book_img_url, author, public_date, book_score, book_contents)

        # 댓글 정보(book_info)
        book_info = {
            'book_name': book_name,
            'book_img_url': book_img_url,
            'author': author,
            'book_score': book_score,
            'book_content': book_contents
        }
        # print(book_info)

        # 댓글 정보(comments)
        comments = list(db.comments.find({'bid': bid}))

        for comment in comments :
            comment['comment_id'] = str(comment["_id"])

        # 도서 정보(books)
        books = db.books.find_one({'bid': bid})
        books["bookId"] = str(books["_id"])
        # print(books)

        # 즐겨찾기 정보(bookmarks)
        # 즐겨찾기 테이블에서 userId, bookId를 조건으로 조회
        bookmarks = db.bookmarks.find_one({'userId': user_info['userId'], 'bookId': books["bookId"]})
        # if books is not None :
        # print(bookmarks)

        return render_template("detailBook.html", bid=bid, user_info=user_info, book_info=book_info, books= books, comments=comments, bookmarks=bookmarks)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 도서 댓글 등록(Create)
@app.route('/createComment', methods=['POST'])
def create_comment():
    user_id_receive = request.form['user_id_give']
    nickname_receive = request.form['nickname_give']
    bid_receive = request.form['bid_give']
    comment_receive = request.form['comment_give']

    doc = {
        'userId' : user_id_receive,
        'nickname': nickname_receive,
        'bid' : bid_receive,
        'comment': comment_receive
    }
    db.comments.insert_one(doc)

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

    db.comments.delete_one(doc)

    return jsonify({'msg':'댓글이 삭제되었습니다!'})

# 북마크 등록(Create)
@app.route('/createBookmark', methods=['POST'])
def save_word():
    user_id_receive = request.form["user_id_give"]
    book_id_receive = request.form["book_id_give"]

    doc = {
        "userId": user_id_receive,
        "bookId": book_id_receive
    }
    db.bookmarks.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '관심등록되었습니다!'})

# 북마크 삭제(Delete)
@app.route('/delBookmark', methods=['POST'])
def delBookmark():
    user_id_receive = request.form['user_id_give']
    book_id_receive = request.form['book_id_give']

    print(user_id_receive, book_id_receive)
    doc = {
        "userId": user_id_receive,
        "bookId": book_id_receive
    }

    db.bookmarks.delete_one(doc)

    return jsonify({'msg': '관심취소되었습니다!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)