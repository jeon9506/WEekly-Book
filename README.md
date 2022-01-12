# shareTodayNews
항해 B반 2조

## 프로젝트 소개

- 제목 : We(ekly) ; Book ( 이번 주 베스트셀러 공유 )
- 설명 : 이번 주 종합 베스트 셀러들을 나열하고, 도서를 클릭하여 댓글을 달고 의견을 공유할 수 있으며 관심 도서를 등록할 수 있는 플랫폼이다.

### 프로젝트 시연영상

### 페이지별 기능

![로그인](https://user-images.githubusercontent.com/32161395/149155482-113eaacd-9d4b-4c99-ae08-71d57d4d08c6.png)

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

### Member


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
