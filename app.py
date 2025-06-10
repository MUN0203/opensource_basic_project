from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash

# 데이터베이스 관련
from flask_tinydb import TinyDB
from tinydb import Query
from flask_bcrypt import Bcrypt     # 비밀번호 해싱을 위해 사용
from flask_session import Session   # 서버 측 세션 관리

# 리뷰기능 관련 
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import uuid

# API 키
import config

from searchKeyword1 import searchKeyword1
from searchTheme import searchTheme
from spcprd3 import localSpcprd3
import requests
from weather import get_kma_weather_multi
from dotenv import load_dotenv
import os

def weather_emoji(weather_desc):
    if not weather_desc:
        return "🌦"
    weather_desc = weather_desc.lower()
    if "맑음" in weather_desc or "clear" in weather_desc:
        return "☀️"
    elif "구름" in weather_desc or "cloud" in weather_desc:
        return "☁️"
    elif "비" in weather_desc or "rain" in weather_desc:
        return "🌧️"
    elif "눈" in weather_desc or "snow" in weather_desc:
        return "❄️"
    elif "안개" in weather_desc or "fog" in weather_desc or "흐림" in weather_desc:
        return "🌫️"
    elif "천둥" in weather_desc or "thunder" in weather_desc:
        return "⛈️"
    else:
        return "🌦"

load_dotenv() 
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
from detailCommon1 import detailCommon1

from keywordExtraction import keywordExtraction

from weather import get_kma_weather_multi

app = Flask(__name__)

app.jinja_env.filters['weather_emoji'] = weather_emoji

# Flask-Session 설정
app.config["SESSION_PERMANENT"] = False # 브라우저 종료 시 세션 만료
app.config["SESSION_TYPE"] = "filesystem" # 세션 데이터를 파일 시스템에 저장
app.secret_key = 'testSecretkey'

Session(app)
bcrypt = Bcrypt(app)

#리뷰기능 관련
# 업로드 기능
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# flask-tinydb 초기화
# 기본적으로 인스턴스 폴더에 'database.json' 파일을 생성/사용
db = TinyDB(app).get_db()

# 테이블 정의
usersTable = db.table("users")
reviewsTable = db.table("reviews")
favoritesTable = db.table("favorites") # 즐겨찾기

# Tour API 키 import
tour_api_key = config.Config.getTOUR_API_KEY()

# 지역 특산물 API 키 import
spcprd_api_key = config.Config.getSPCPRD_API_KEY()

# 리뷰 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

@app.route('/review')
def reviews():
    items = []
    for item in reviewsTable:
        review = item.copy()
        review['doc_id'] = item.doc_id
        items.append(review)

    current_user = None
    if session.get('user_id'):
        user = usersTable.get(doc_id=session['user_id'])
        current_user = user['username'] if user else None

    return render_template('review.html', reviews=items, current_user=current_user)

@app.route('/review/write', methods=['GET'])
@login_required
def write_review():
    keyword = request.args.get('keyword', '').strip()
    places = []
    if keyword:
        def_params = {
            "SERVICE_KEY": config.Config.getTOUR_API_KEY(),
            "MOBILE_OS": "ETC",
            "MOBILE_APP": "MyTravelApp",
            "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
        }
        places = searchKeyword1(def_params, keyword)

    contentid = request.args.get('contentid')
    item_addr1 = request.args.get('item_addr1')
    place_image = request.args.get('image')
    place_title = request.args.get('title')
    place_tel = request.args.get('tel')
    return render_template('write_review.html', keyword=keyword, places=places,
                           contentid=contentid, item_addr1=item_addr1, image=place_image,
                           title=place_title, tel=place_tel)

@app.route('/review/write', methods=['POST'])
@login_required
def submit_review():
    title = request.form['title']
    content = request.form['content']
    theme = request.form['theme']
    image = request.files.get('image')

    img_path = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(save_path)
        img_path = os.path.join('uploads', filename)

    # 장소 정보 가져오기
    contentid = request.form.get('contentid')
    item_addr1 = request.form.get('item_addr1')
    place_image = request.form.get('place_image')
    place_title = request.form.get('place_title')
    place_tel = request.form.get('place_tel')

    user = usersTable.get(doc_id=session['user_id'])

    reviewsTable.insert({
        'user': user['username'],
        'title': title,
        'content': content,
        'theme': theme,
        'image': img_path,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'likes': 0,
        'liked_users': [],
        'comments': [],
        'contentid': contentid,
        'place_addr1': item_addr1,
        'place_image': place_image,
        'place_title': place_title,
        'place_tel': place_tel
    })

    flash('리뷰가 등록되었습니다.')
    return redirect(url_for('detail',
                            item_addr1=item_addr1,
                            contentid=contentid,
                            image=place_image,
                            title=place_title,
                            tel=place_tel))

# 리뷰 디테일페이지로
@app.route('/review/<int:review_id>')
def review_detail(review_id):
    review = reviewsTable.get(doc_id=review_id)
    if not review:
        flash('리뷰가 존재하지 않습니다.')
        return redirect(url_for('reviews'))

    current_user = None
    if session.get('user_id'):
        user = usersTable.get(doc_id=session['user_id'])
        current_user = user['username'] if user else None

    return render_template('review_detail.html', review=review, current_user=current_user)

# 댓글 기능
@app.route('/review/<int:review_id>/comment', methods=['POST'])
@login_required
def add_comment(review_id):
    comment_text = request.form['comment']
    user = usersTable.get(doc_id=session['user_id'])
    comment = {
        'user': user['username'],
        'text': comment_text,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'id': str(uuid.uuid4())
    }

    review = reviewsTable.get(doc_id=review_id)
    if review:
        comments = review.get('comments', [])
        comments.append(comment)
        reviewsTable.update({'comments': comments}, doc_ids=[review_id])
    return redirect(url_for('review_detail', review_id=review_id))

# 댓글 수정
@app.route('/review/<int:review_id>/comment/<comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(review_id, comment_id):
    review = reviewsTable.get(doc_id=review_id)
    if not review:
        flash('리뷰가 존재하지 않습니다.')
        return redirect(url_for('reviews'))

    comments = review.get('comments', [])
    comment = next((c for c in comments if c['id'] == comment_id), None)
    if not comment or comment['user'] != usersTable.get(doc_id=session['user_id'])['username']:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('review_detail', review_id=review_id))

    if request.method == 'POST':
        new_text = request.form['comment']
        comment['text'] = new_text
        reviewsTable.update({'comments': comments}, doc_ids=[review_id])
        flash('댓글이 수정되었습니다.')
        return redirect(url_for('review_detail', review_id=review_id))

    return render_template('edit_comment.html', comment=comment, review_id=review_id)

# 리뷰 좋아요 (1회원 1회)
@app.route('/review/<int:review_id>/like', methods=['POST'])
@login_required
def like_review(review_id):
    user_id = session['user_id']
    review = reviewsTable.get(doc_id=review_id)
    if review:
        liked_users = review.get('liked_users', [])
        if user_id not in liked_users:
            review['likes'] = review.get('likes', 0) + 1
            liked_users.append(user_id)
            reviewsTable.update({'likes': review['likes'], 'liked_users': liked_users}, doc_ids=[review_id])
    return redirect(url_for('review_detail', review_id=review_id))

# 댓글 삭제
@app.route('/review/<int:review_id>/comment/<comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(review_id, comment_id):
    review = reviewsTable.get(doc_id=review_id)
    if not review:
        flash('리뷰가 존재하지 않습니다.')
        return redirect(url_for('reviews'))

    user = usersTable.get(doc_id=session['user_id'])
    comments = review.get('comments', [])
    new_comments = [c for c in comments if not (c['id'] == comment_id and c['user'] == user['username'])]

    if len(comments) != len(new_comments):
        reviewsTable.update({'comments': new_comments}, doc_ids=[review_id])
        flash('댓글이 삭제되었습니다.')
    else:
        flash('삭제 권한이 없습니다.')

    return redirect(url_for('review_detail', review_id=review_id))

# 리뷰 삭제
@app.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = reviewsTable.get(doc_id=review_id)
    if review and review['user'] == usersTable.get(doc_id=session['user_id'])['username']:
        reviewsTable.remove(doc_ids=[review_id])
    next_page = request.form.get('next') or url_for('reviews')
    return redirect(next_page)

# 리뷰 수정
@app.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = reviewsTable.get(doc_id=review_id)
    if not review or review['user'] != usersTable.get(doc_id=session['user_id'])['username']:
        flash('권한이 없습니다.')
        return redirect(url_for('reviews'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        theme = request.form['theme']
        reviewsTable.update({'title': title, 'content': content, 'theme': theme}, doc_ids=[review_id])
        flash('리뷰가 수정되었습니다.')
        return redirect(url_for('review_detail', review_id=review_id))

    return render_template('edit_review.html', review=review)

@app.route('/')
def index():
    if tour_api_key and spcprd_api_key:
        print(f"로드된 Tour API 키: {tour_api_key[:4]}...")
        print(f"로드된 지역 특산물 API 키: {spcprd_api_key[:4]}...")
        key_loaded = True
    else:
        print("API 키를 로드하지 못했습니다.")
        key_loaded = False

    user = None
    if session.get('user_id'):
        user = usersTable.get(doc_id=session['user_id'])

    return render_template('index.html', title='TripPick', tour_api_key_loaded=key_loaded, user=user)

# 회원가입 페이지
@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        # 1) 폼 데이터 받아오기
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 2) 입력값 유효성 검사
        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.')
            return redirect(url_for('register'))

        # 3) 이미 가입된 아이디인지 확인
        UserQuery = Query()
        existing_user = usersTable.get(UserQuery.username == username)
        if existing_user:
            flash('이미 사용 중인 아이디입니다.')
            return redirect(url_for('register'))

        # 4) 비밀번호 해싱 후 저장
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        usersTable.insert({
            'username': username,
            'hashed_password': hashed_password
        })

        flash('회원가입이 완료되었습니다.')
        return redirect(url_for('reviews'))

    # GET 요청일 때는 가입 폼 렌더링
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 1) 입력값 확인
        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.')
            return redirect(url_for('login'))

        # 2) DB에서 사용자 조회
        UserQuery = Query()
        user_doc = usersTable.get(UserQuery.username == username)
        if not user_doc:
            flash('존재하지 않는 아이디입니다.')
            return redirect(url_for('login'))

        # 3) 비밀번호 비교 (bcrypt)
        if not bcrypt.check_password_hash(user_doc['hashed_password'], password):
            flash('비밀번호가 틀렸습니다.')
            return redirect(url_for('login'))

        # 4) 로그인 성공 → 세션에 사용자 정보 저장
        session['user_id'] = user_doc.doc_id
        flash('로그인 되었습니다.')
        return redirect(url_for('reviews'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃 되었습니다.')
    return redirect(url_for('reviews'))


# 대시보드(로그인 후 접근) 페이지
@app.route('/dashboard')
def dashboard():
    # 보호된 페이지: 로그인된 사용자만 접근 가능
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))

    # 현재 로그인한 사용자의 정보를 가져옴
    user = usersTable.get(doc_id=session['user_id'])
    # 사용자가 작성한 리뷰 불러오기
    ReviewQuery = Query()
    user_reviews = reviewsTable.search(ReviewQuery.user == user['username'])
    return render_template('dashboard.html', user=user, reviews=user_reviews)


@app.route('/search', methods=['GET', 'POST'])
def search():
    keyword = ''
    items = []
    results = []

    key_loaded = bool(tour_api_key)
    if key_loaded:
        print(f"로드된 Tour API 키: {tour_api_key[:4]}...")
    else:
        print("Tour API 키를 로드하지 못했습니다.")

    def_params = {
        "SERVICE_KEY": tour_api_key,
        "MOBILE_OS": "ETC",
        "MOBILE_APP": "MyTravelApp",
        "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
    }

    if request.method == 'POST':
        # 키워드 검색하기
        keyword = request.form.get('keyword', '').strip()
        items = searchKeyword1(def_params, keyword)

        locs = []
        for item in items:
            try:
                lat = float(item.get('mapy', 0))
                lon = float(item.get('mapx', 0))
                locs.append((lat, lon))
            except Exception:
                locs.append((0, 0))

        # 위도, 경도 분리
        lats = [lat for lat, lon in locs]
        lons = [lon for lat, lon in locs]

        # 날씨 정보 가져오기
        weather_list = get_kma_weather_multi(lats, lons)

        for i, item in enumerate(items):
           weather = weather_list[i] if i < len(weather_list) else None

           if isinstance(weather, dict) and weather.get("current"):
              item['weather'] = weather
              item['weather_status'] = weather["current"].get("weather_kr", "날씨 정보 없음")
           else:
              item['weather'] = None
              item['weather_status'] = "날씨 정보 없음"

        # 검색 결과에 대한 날씨 리스트를 results에 저장
        results = weather_list

    return render_template(
        'search.html',
        title='여행지 검색',
        items=items,
        weatherItems = results,
        keyword=keyword,
        tour_api_key_loaded=key_loaded,
        kakao_api_key=KAKAO_API_KEY  # 카카오맵 키 전달
    )

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/recommend/<theme_name>')
def recommend_theme(theme_name):
    def_params = {
        "SERVICE_KEY": config.Config.getTOUR_API_KEY(),
        "MOBILE_OS": "ETC",
        "MOBILE_APP": "MyTravelApp",
        "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
    }

    theme_category_map = {
        "healing":  {"cat1": "A01", "cat2": ["A0101", "A0103", "A0208"], "contentTypeId": "12"},
        "activity": {"cat1": "A03", "cat2": ["A0301", "A0303", "A0305"], "contentTypeId": "28"},
        "photo":    {"cat1": "A02", "cat2": ["A0201", "A0202", "A0207"], "contentTypeId": "12"},
        "food":     {"cat1": "A05", "cat2": ["A0502", "A0503", "A0505"], "contentTypeId": "39"}
    }

    if theme_name in theme_category_map:
        theme_config = theme_category_map[theme_name]
        items = searchTheme(def_params, theme_config["cat1"], theme_config["cat2"], theme_config["contentTypeId"])
    else:
        items = []

    # 날씨 정보 가져오기
    locs = []
    for it in items:
        try:
            lat = float(it.get('mapy', 0))
            lon = float(it.get('mapx', 0))
            locs.append((lat, lon))
        except Exception:
            locs.append((0, 0))
    lats = [lat for lat, lon in locs]
    lons = [lon for lat, lon in locs]
    weather_list = get_kma_weather_multi(lats, lons)
    
    for idx, it in enumerate(items):
        w = weather_list[idx] if idx < len(weather_list) else None
        if isinstance(w, dict) and w.get("current"):
            it['weather'] = w
            it['weather_status'] = w["current"].get("weather_kr", "날씨 정보 없음")
        else:
            it['weather'] = None
            it['weather_status'] = "날씨 정보 없음"

    return render_template('theme_result.html',
                           theme=theme_name,
                           items=items,
                           weatherItems=weather_list)

# 리뷰 확인 페이지
@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/detail', methods=['GET', 'POST'])
def detail():
    contentid = request.args.get('contentid')
    image_url = request.args.get('image_url')

     # 1. 관광지 상세 정보 가져오기
    detail_url = "http://apis.data.go.kr/B551011/KorService1/detailCommon1"
    detail_params = {
        'serviceKey': tour_api_key,
        'MobileOS': "ETC",
        'MobileApp': "TripPick",
        'contentId': contentid,
        'defaultYN': 'Y',
        'overviewYN': 'Y',
        'mapinfoYN': 'Y',
        '_type': 'json'
    }

    item = {}
    try:
        response = requests.get(detail_url, params=detail_params)
        print("✅ TourAPI 응답 상태코드:", response.status_code)
        print("✅ TourAPI 응답 내용:", response.text[:500])  # 너무 길면 500자만
        items = response.json()['response']['body']['items']['item']

        if isinstance(items, list) and len(items) > 0:
          item = items[0]
        elif isinstance(items, dict):
          item = items

        addr_from_param = request.args.get('item_addr1', None)
        if item.get("addr1") is None and addr_from_param:
           item["addr1"] = addr_from_param
           
    except Exception as e:
      print("TourAPI 상세 호출 실패:", e)

    print("addr1:", item.get("addr1"))
    print("mapx:", item.get("mapx"))
    print("mapy:", item.get("mapy"))

    item_addr1 = item.get("addr1", "").split()
    print("item_addr1:", item_addr1)

    try:
        lat = float(item.get("mapy", 0))
        lon = float(item.get("mapx", 0))
    except Exception as e:
        lat, lon = 0, 0

    # 날씨 정보  
    weather = "정보 없음"
    if lat != 0 and lon != 0:
        try:
            weather_result = get_kma_weather_multi([lat], [lon])
            if (
                isinstance(weather_result, list) and len(weather_result) > 0
                and isinstance(weather_result[0], dict)
                and weather_result[0].get("current") is not None
                and not weather_result[0]["current"].get("error")
                and "temperature" in weather_result[0]["current"]
                and "weather_kr" in weather_result[0]["current"]
            ):
                weather = weather_result[0]
        except Exception as e:
            print("날씨 정보 조회 실패:", e)

    # 특산물 API 키 확인
    key_loaded2 = bool(spcprd_api_key)
    if key_loaded2:
        print(f"로드된 특산물 API 키: {spcprd_api_key[:4]}...")
    # 상세 페이지에서 리뷰 제출 처리
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))

        title = request.form['title']
        content = request.form['content']
        theme = request.form['theme']
        image_file = request.files.get('image')

        img_path = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(save_path)
            img_path = os.path.join('uploads', filename)

        item_addr1 = request.args.get('item_addr1')
        contentid = request.args.get('contentid')
        place_image = request.args.get('image')
        place_title = request.args.get('title')
        place_tel = request.args.get('tel')

        # 리뷰 입력
        user = usersTable.get(doc_id=session['user_id'])
        reviewsTable.insert({
            'user': user['username'],
            'title': title,
            'content': content,
            'theme': theme,
            'image': img_path,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'likes': 0,
            'liked_users': [],
            'comments': [],
            'contentid': contentid,
            'place_addr1': item_addr1,
            'place_image': place_image,
            'place_title': place_title,
            'place_tel': place_tel
        })
        flash('리뷰가 등록되었습니다.')

        return redirect(url_for('detail',
                                item_addr1=item_addr1,
                                contentid=contentid,
                                image=place_image,
                                title=place_title,
                                tel=place_tel))

    def_params = {
        "SERVICE_KEY": config.Config.getTOUR_API_KEY(),
        "MOBILE_OS": "ETC",
        "MOBILE_APP": "MyTravelApp",
        "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
    }

    # search.html로부터 정보 얻어오기
    item_addr1 = request.args.get('item_addr1')
    contentid = request.args.get('contentid')
    image = request.args.get('image')
    title = request.args.get('title')
    tel = request.args.get('tel')

    info = {
        "item_addr1" : item_addr1,
        "contentid" : contentid,
        "image" : image,
        "title" : title,
        "tel" : tel
    }

    if spcprd_api_key :
        print(f"로드된 Tour API 키: {spcprd_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded2 = True
    else:
        print("특산물 API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded2 = False

    if item_addr1 == "" :
        item_addr1 = "주소 없음"
    # print(items["addr1"])
    # 특산물 API
    item_addr1 = item_addr1.split() 
    # print(item_addr1[1])


    print(item_addr1)
    def_params2 = {
        "apiKey" : spcprd_api_key,
        "BASE_URL" : "http://api.nongsaro.go.kr/service/localSpcprd"
    } 

    print(item_addr1)

    # 부산광역시, 대구광역시, 광주광역시, 인천광역시, 울산광역시, 세종특별자치시는 별도 로직 적용
    if item_addr1[0] == "부산광역시" or item_addr1[0] == "대구광역시" or item_addr1[0] == "광주광역시" or item_addr1[0] == "인천광역시" or item_addr1[0] == "울산광역시" or item_addr1[0] == "세종특별자치시" :
        print(item_addr1[0])
        if item_addr1[1] == "기장군" or item_addr1[1] == "달성군" or item_addr1[1] == "강화군" or item_addr1[1] == "옹진군" :
            print(item_addr1[1])
            items2 = localSpcprd3(def_params2, item_addr1[1])
        else :
            print(item_addr1[0])
            items1 = localSpcprd3(def_params2, item_addr1[0])
            excluded_keywords = ['달성군', '기장군', '강화군', '옹진군']
            items2 = [item for item in items1 if not any(keyword in item.get('areaNm', '') for keyword in excluded_keywords)]
            print(items2)
    else :
        items2 = localSpcprd3(def_params2, item_addr1[1])
        
    print(items2)


    # 상세 정보 불러오기
    detailInfo = detailCommon1(def_params, info["contentid"])
    print(f'테스트{detailInfo}')


    # 키워드 추출
    if detailInfo['item'][0]['overview'] == "-" or detailInfo['item'][0]['overview'] == "":
        keywordResult = ""
    else :
        print(f'개요 테스트: {detailInfo["item"][0]["overview"]}')
        # 키워드 추출
        keywordResult = keywordExtraction(detailInfo['item'][0]['overview'])
        print()
        print(f'키워드 결과: {keywordResult}')

    # 리뷰 가져오기
    ReviewQuery = Query()
    place_reviews = reviewsTable.search(ReviewQuery.contentid == info['contentid'])

    return render_template('detail.html',
                           item=item,
                           items2=items2,
                           image_url=image_url,
                           info=info,
                           keywords=keywordResult,
                           reviews=place_reviews,
                           weather=weather,
                           kakao_api_key=KAKAO_API_KEY)

 
if __name__ == '__main__':
    app.run(debug=True)
