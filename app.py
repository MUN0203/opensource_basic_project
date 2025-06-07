from flask import Flask, render_template, request
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

app = Flask(__name__)

app.jinja_env.filters['weather_emoji'] = weather_emoji

# Tour API 키 import
tour_api_key = config.Config.getTOUR_API_KEY()

# 지역 특산물 API 키 import
spcprd_api_key = config.Config.getSPCPRD_API_KEY()

@app.route('/')
def index():
    if tour_api_key and spcprd_api_key:
        print(f"로드된 Tour API 키: {tour_api_key[:4]}...")
        print(f"로드된 지역 특산물 API 키: {spcprd_api_key[:4]}...")
        key_loaded = True
    else:
        print("API 키를 로드하지 못했습니다.")
        key_loaded = False

    return render_template('index.html', title='해당 타이틀 미정', tour_api_key_loaded=key_loaded)

@app.route('/search', methods=['GET', 'POST'])
def search():
    keyword = ''
    items = []

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

    return render_template('theme_result.html', theme=theme_name, items=items)

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/detail')
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
    else:
        print("특산물 API 키를 로드하지 못했습니다.")

    def_params2 = {
        "apiKey": spcprd_api_key,
        "BASE_URL": "http://api.nongsaro.go.kr/service/localSpcprd"
    }


    if len(item_addr1) >= 2:
        if item_addr1[0] in ["부산광역시", "대구광역시", "광주광역시", "인천광역시", "울산광역시", "세종특별자치시"]:
            if item_addr1[1] in ["기장군", "달성군", "강화군", "옹진군"]:
                items2 = localSpcprd3(def_params2, item_addr1[1])
            else:
                items1 = localSpcprd3(def_params2, item_addr1[0])
                excluded_keywords = ['달성군', '기장군', '강화군', '옹진군']
                items2 = [item for item in items1 if not any(keyword in item.get('areaNm', '') for keyword in excluded_keywords)]
        else:
            items2 = localSpcprd3(def_params2, item_addr1[1])
    else:
        items2 = []
   
    print("특산물 items2:", items2)

    return render_template(
        'detail.html',
        item=item,
        items2=items2,
        image_url=image_url,
        weather=weather,
        kakao_api_key=KAKAO_API_KEY  
    )

 
if __name__ == '__main__':
    app.run(debug=True)
