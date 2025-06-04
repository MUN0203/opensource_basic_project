from flask import Flask, render_template, request
import config
from searchKeyword1 import searchKeyword1
from searchTheme import searchTheme
from spcprd3 import localSpcprd3
from dotenv import load_dotenv
import os

load_dotenv() 
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

app = Flask(__name__)

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
    item_addr1 = request.args.get('item_addr1')

    key_loaded2 = bool(spcprd_api_key)
    if key_loaded2:
        print(f"로드된 특산물 API 키: {spcprd_api_key[:4]}...")
    else:
        print("특산물 API 키를 로드하지 못했습니다.")

    item_addr1 = item_addr1.split()

    def_params2 = {
        "apiKey": spcprd_api_key,
        "BASE_URL": "http://api.nongsaro.go.kr/service/localSpcprd"
    }

    print(item_addr1)

    if item_addr1[0] in ["부산광역시", "대구광역시", "광주광역시", "인천광역시", "울산광역시", "세종특별자치시"]:
        if item_addr1[1] in ["기장군", "달성군", "강화군", "옹진군"]:
            items2 = localSpcprd3(def_params2, item_addr1[1])
        else:
            items1 = localSpcprd3(def_params2, item_addr1[0])
            excluded_keywords = ['달성군', '기장군', '강화군', '옹진군']
            items2 = [item for item in items1 if not any(keyword in item.get('areaNm', '') for keyword in excluded_keywords)]
    else:
        items2 = localSpcprd3(def_params2, item_addr1[1])

    print(items2)
    return render_template('detail.html', items2=items2)

if __name__ == '__main__':
    app.run(debug=True)
