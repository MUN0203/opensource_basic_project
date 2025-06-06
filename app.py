from flask import Flask, render_template, request
import config
from searchKeyword1 import searchKeyword1
from searchTheme import searchTheme
from spcprd3 import localSpcprd3
import requests
from weather import get_kma_weather_multi

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

app = Flask(__name__)

app.jinja_env.filters['weather_emoji'] = weather_emoji

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
    keyword = ''
    items = []

    if tour_api_key :
        print(f"로드된 Tour API 키: {tour_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded = True
    else:
        print("Tour API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded = False
        
    def_params = {
        "SERVICE_KEY": tour_api_key,
        "MOBILE_OS": "ETC",
        "MOBILE_APP": "MyTravelApp",
        "BASE_URL": "http://apis.data.go.kr/B551011/KorService1"
    }

    if request.method == 'POST':
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

    return render_template(
        'search.html',
        title='여행지 검색',
        items=items,
        keyword=keyword,
        tour_api_key_loaded=key_loaded
    )   

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
@app.route('/review')
def review():
    # 여기에 날씨 확인 관련 로직 추가 가능
    return render_template('review.html')

@app.route('/detail')
def detail():
    contentid = request.args.get('contentid')
    item_addr1 = request.args.get('item_addr1')
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
        items = response.json()['response']['body']['items']['item']

        if isinstance(items, list) and len(items) > 0:
          item = items[0]
        elif isinstance(items, dict):
          item = items
    except Exception as e:
      print("TourAPI 상세 호출 실패:", e)

    try:
        lat = float(item.get("mapy", 0))
        lon = float(item.get("mapx", 0))
    except Exception as e:
        lat, lon = 0, 0

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

    # 특산물 API
    if spcprd_api_key :
        print(f"로드된 Tour API 키: {spcprd_api_key[:4]}... (보안을 위해 일부만 출력)") # 서버 로그에 출력
        key_loaded2 = True
    else:
        print("특산물 API 키를 로드하지 못했습니다. .env 파일을 확인하세요.")
        key_loaded2 = False

    item_addr1 = item_addr1.split()

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

    return render_template('detail.html', item=item, items2 = items2, image_url=image_url, weather=weather)
 
if __name__ == '__main__':
    # debug_mode = app.config.get('DEBUG', False) # 예: Config 클래스에 DEBUG = True/False 추가
    app.run(debug=True) # 개발 중에는 True 사용
