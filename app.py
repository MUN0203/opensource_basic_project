from flask import Flask, render_template, request
import config
from searchKeyword1 import searchKeyword1
from searchTheme import searchTheme
from spcprd3 import localSpcprd3

app = Flask(__name__)

# Tour API 키 import
tour_api_key = config.Config.getTOUR_API_KEY()

# 지역 특산물 API 키 import
spcprd_api_key = config.Config.getSPCPRD_API_KEY()

items = []

@app.route('/')
def index():
    # API 키 로딩 확인
    if tour_api_key and spcprd_api_key:
        print(f"로드된 Tour API 키: { tour_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        print(f"로드된 지역 특산물 API 키: {spcprd_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded = True
    else:
        print("Tour API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded = False

    return render_template('index.html', title='해당 타이틀 미정', tour_api_key_loaded=key_loaded)

# 여행지 검색 페이지
@app.route('/search', methods = ['GET', 'POST'])
def search():
    if tour_api_key :
        print(f"로드된 Tour API 키: {tour_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded = True
    else:
        print("Tour API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded = False

    # Tour API
    def_params = {
        "SERVICE_KEY" : tour_api_key,
        # 서비스 호출 시 필수 파라미터
        "MOBILE_OS" : "ETC", # 예: "IOS", "AND", "WIN", "ETC" (기타)
        "MOBILE_APP" : "MyTravelApp", # 개발 중인 서비스명 또는 앱 이름
        "BASE_URL" : "http://apis.data.go.kr/B551011/KorService1"
    }   
    
    # 폼에서 입력하면 입력한 키워드로 Tour API, 특산물 API로부터 데이터 가져오기
    items = []
    if request.method == 'POST' :
        keyword = request.form.get('keyword', '').strip()
        items = searchKeyword1(def_params, keyword)
    # print(items)
    return render_template('search.html', title='해당 타이틀 미정', items = items, tour_api_key_loaded=key_loaded)

# 여행지 추천 페이지
@app.route('/recommend')
def recommend():
    # 여기에 여행지 추천 관련 로직 추가 가능
    return render_template('recommend.html')

# 테마별 추천 페이지
@app.route('/recommend/<theme_name>')
def recommend_theme(theme_name):
    def_params = {
        "SERVICE_KEY": config.Config.getTOUR_API_KEY(),
        "MOBILE_OS": "ETC",
        "MOBILE_APP": "MyTravelApp",
        "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
    }
    
    # 테마별 카테고리 매핑
    theme_category_map = {
        "healing":  {"cat1": "A01", "cat2": ["A0101", "A0103", "A0208"], "contentTypeId": "12"},  # 자연/관광지
        "activity": {"cat1": "A03", "cat2": ["A0301", "A0303", "A0305"], "contentTypeId": "28"},  # 체험
        "photo":    {"cat1": "A02", "cat2": ["A0201", "A0202", "A0207"], "contentTypeId": "12"},  # 관광지
        "food":     {"cat1": "A05", "cat2": ["A0502", "A0503", "A0505"], "contentTypeId": "39"}   # 음식
    }

    if theme_name in theme_category_map:
       theme_config = theme_category_map[theme_name]
       cat1 = theme_config["cat1"]
       cat2_list = theme_config["cat2"]
       contentTypeId = theme_config["contentTypeId"]
       items = searchTheme(def_params, cat1, cat2_list, contentTypeId) 
    else:
       items = []
    return render_template('theme_result.html', theme=theme_name, items=items)

# 날씨 확인 페이지
@app.route('/weather')
def weather():
    # 여기에 날씨 확인 관련 로직 추가 가능
    return render_template('weather.html')

@app.route('/detail')
def detail():
    item_addr1 = request.args.get('item_addr1')
    if spcprd_api_key :
        print(f"로드된 Tour API 키: {spcprd_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded2 = True
    else:
        print("특산물 API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded2 = False

    # print(items["addr1"])
    # 특산물 API
    item_addr1 = item_addr1.split()
    print(item_addr1[1])


    def_params2 = {
        "apiKey" : spcprd_api_key,
        "BASE_URL" : "http://api.nongsaro.go.kr/service/localSpcprd"
    } 

    # 부산광역시, 대구광역시, 광주광역시, 인천광역시, 울산광역시, 세종특별자치시는 별도 로직 적용
    if item_addr1[0] == "부산광역시" or "대구광역시" or "광주광역시" or "인천광역시" or "울산광역시" or "세종특별자치시" :
        if item_addr1[1] == "기장군" or "달성군" or "강화군" or "웅진군" or "강화군" :
            items2 = localSpcprd3(def_params2, item_addr1[1])
        else :
            print(item_addr1[0])
            items2 = localSpcprd3(def_params2, item_addr1[0])
    else :
        items2 = localSpcprd3(def_params2, item_addr1[1])
        
    print(items2)
    

    return render_template('detail.html', items2 = items2)

if __name__ == '__main__':
    # debug_mode = app.config.get('DEBUG', False) # 예: Config 클래스에 DEBUG = True/False 추가
    app.run(debug=True) # 개발 중에는 True 사용
