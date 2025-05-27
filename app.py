from flask import Flask, render_template, request
import config
from searchKeyword1 import searchKeyword1

app = Flask(__name__)

# API 키 import
tour_api_key = config.Config.getTOUR_API_KEY()

@app.route('/')
def index():

    if tour_api_key:
        print(f"로드된 Tour API 키: {tour_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded = True
    else:
        print("Tour API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded = False

    return render_template('index.html', title='해당 타이틀 미정', tour_api_key_loaded=key_loaded)

# 여행지 검색 페이지
@app.route('/search', methods = ['GET', 'POST'])
def search():
    if tour_api_key:
        print(f"로드된 Tour API 키: {tour_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded = True
    else:
        print("Tour API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded = False

    def_params = {
    "SERVICE_KEY" : config.Config.getTOUR_API_KEY(),
    # 서비스 호출 시 필수 파라미터
    "MOBILE_OS" : "ETC", # 예: "IOS", "AND", "WIN", "ETC" (기타)
    "MOBILE_APP" : "MyTravelApp", # 개발 중인 서비스명 또는 앱 이름
    "BASE_URL" : "http://apis.data.go.kr/B551011/KorService1"
    }
    
    # 폼에서 입력하면 입력한 키워드로 API로부터 데이터 가져오기
    items = []
    if request.method == 'POST' :
        keyword = request.form.get('keyword', '').strip()
        items = searchKeyword1(def_params, keyword)
    
    return render_template('search.html', title='해당 타이틀 미정', items = items, tour_api_key_loaded=key_loaded)

# 여행지 추천 페이지
@app.route('/recommend')
def recommend():
    # 여기에 여행지 추천 관련 로직 추가 가능
    return render_template('recommend.html')

# 테마별 추천 페이지
@app.route('/recommend/<theme_name>')
def recommend_theme(theme_name):
    # 실제 서비스 분류 코드 또는 필터를 활용한 추천 로직 구현 가능
    # 예: 힐링 → spa, 산, 자연 등 / 액티비티 → 레저, 체험 등

    # 일단 더미 데이터를 예시로 보여주기
    dummy_items = [
        {"title": f"{theme_name.capitalize()} 명소 1", "addr1": "서울시 강남구", "tel": "010-1234-5678", "image": None},
        {"title": f"{theme_name.capitalize()} 명소 2", "addr1": "부산 해운대구", "tel": "010-9876-5432", "image": None},
    ]

    return render_template('theme_result.html', theme=theme_name, items=dummy_items)

# 날씨 확인 페이지
@app.route('/weather')
def weather():
    # 여기에 날씨 확인 관련 로직 추가 가능
    return render_template('weather.html')

@app.route('/detail')
def detail():
    # 여기에 날씨 확인 관련 로직 추가 가능
    return render_template('detail.html')

if __name__ == '__main__':
    # debug_mode = app.config.get('DEBUG', False) # 예: Config 클래스에 DEBUG = True/False 추가
    app.run(debug=True) # 개발 중에는 True 사용
