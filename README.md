# shareTodayNews
항해 B반 2조

## 프로젝트 소개

- 제목 : We(ekly) ; Book ( 이번 주 베스트셀러 공유 )
- 설명 : 이번 주 종합 베스트 셀러들을 나열하고, 도서를 클릭하여 댓글을 달고 의견을 공유할 수 있으며 관심 도서를 등록할 수 있는 플랫폼이다.

### 프로젝트 시연영상

### 페이지별 기능

![로그인](https://user-images.githubusercontent.com/32161395/149157418-5c8fc416-2478-40ac-88d3-88adce8aab29.png)
#### 로그인 페이지(최초 접속 시)

- 로그인, 회원가입 기능
- 회원 검사
- ID/PW 입력 성공 시 메인 페이지로 이동
- ID/PW 틀릴 시 빨간글씨 또는 alert으로 표시
- '회원가입'버튼 클릭 시 회원가입 페이지로 이동
<p></p>

![회원가입](https://user-images.githubusercontent.com/32161395/149157456-c9f3c844-fdd8-4bde-a3fa-9a56ba643c5c.png)
#### 회원가입 페이지(회원 가입 버튼 클릭 시)

- 회원가입 기능
- 회원가입 시 아이디 중복체크 (id로 체크)
- 이름, 아이디, 패스워드(패스워드 확인 검사)
- 회원 가입 성공 시 alert창 띄우고 로그인 페이지로 이동
<p></p>

![메인페이지](https://user-images.githubusercontent.com/32161395/149157504-dc64e8a0-47a9-4249-859f-068207c83e37.png)
#### 메인 페이지 - 크롤링(스크래핑)

- 상위 25위 도서정보 스크래핑 후 도서정보 저장(네이버 베스트셀러)
- 신규 도서 추가
- 리스트 형식으로 조회
- 이미지, 타이틀 클릭 시 상세 페이지로 이동
<p></p>

![상세페이지](https://user-images.githubusercontent.com/32161395/149157520-263a3cdb-dc6b-4bee-b3de-1bb616b10a88.png)
#### 상세페이지

- 도서상세 정보 스크래핑
- 선택한 도서 관심등록,취소 기능
- 댓글 리스트 + 삭제 버튼을 보여줌
- 본인이 등록한 댓글 정보만 삭제가능
<p></p>

![마이페이지](https://user-images.githubusercontent.com/32161395/149157546-f053425d-cdf7-4fa5-9aeb-7e65bccff5b8.png)
#### 마이 페이지

- 사용자가 관심등록한 도서목록을 카드 형식으로 표시
- 사용자가 이미지와 타이틀 클릭 시 관련도서의 상세정보 조회
- 사용자의 관심도서 삭제 버튼 클릭 시 관심도서 목록에서 삭제 후 reload
<p></p>

### API 테이블

| 기능  | Method | URL | request | response |
| --- | --- | --- | --- | --- |
| 로그인 | POST | /loginCheck | {'userId':userId,'password':password} | 로그인 성공 여부 |
| 회원가입 | POST | /joinCheck | {'userId':userId,'password':password,'nickname',nickname} | 회원가입 성공 여부 |
| 회원 가입시 ID<br> 중복 확인 | POST | /sign_up/check_dup | {'userId':userId} | ID 중복여부 |
| 메인페이지 | GET | /main |     | 메인페이지 도서목록 조회 |
| 상세페이지 | GET | /viewDetail | {'bid':bid} | 선택한 도서 상세,댓글정보 조회 |
| 마이페이지 | GET | /mypage |     | 마이페이지 관심도서목록 조회 |
| 도서 댓글 등록 | POST | /createComment | {'userId':userId,'nickname':nickname<br><br> 'bid':bid,'comment':comment} | 도서댓글등록 성공 여부 |
| 도서 댓글 삭제 | POST | /delComment | {'userId':userId,'_id':ObjectId(id)} | 도서댓글삭제 성공 여부 |
| 북마크 등록 | POST | /createBookmark | {'userId':userId,'bookId':bookId} | 관심도서등록 성공 여부 |
| 북마크<br> 삭제 | POST | /delBookmark | {'userId':userId,'bookId':bookId} | 관심도서삭제 성공 여부 |
<p></p>

## Trouble Shooting

1. 로컬에서 pull 받고 원격저장소로 push 하는 과정에서 merge시 충돌이 발생했는데
  git bash에서 git status 명령어를 입력해 both modified 상태된 파일을 확인하고 
  새롭게 수정후 commit 해서 충돌을 해결했다.
2. Jinja2를 통해 서버에서 html로 변수에 값을 담아 보내는 방법
  ->html {{변수이름}},app.py에서는 <변수이름>으로 받게된다.
  jwt을 이용한 로그인 정보 저장과 정보를 통한 로그인 유지 방법
  ->token을 이용해 저장하며
  token에 있는 정보를 통해 DB에서 회원정보를 읽어 온 뒤 
  변수에 담아서 다른 페이지로 이동 시 넘겨준다.
3. 크롤링 시 NoneType error 발생 -> try except AttributeError 후 해당 변수 공백처리
4. 도서목록 db크롤링 때 데이터가 한 번 더 중복으로 생성됐는데
  bid를 이용해서 db에 bid가 들어가있지 않으면 크롤링 데이터를 db에 생성하는 조건문을 
  써서 중복 문제를 해결하였다.
<p></p>
### Member
