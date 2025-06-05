import requests
import config

def get_tour_detail(content_id):
    base_url = "http://apis.data.go.kr/B551011/KorService1/detailCommon1"
    params = {
        "serviceKey": config.Config.getTOUR_API_KEY(),
        "MobileOS": "ETC",
        "MobileApp": "MyTravelApp",
        "contentId": content_id,
        "defaultYN": "Y",
        "overviewYN": "Y",
        "firstImageYN": "Y",
        "_type": "json"
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        try:
            item = response.json()['response']['body']['items']['item'][0]
            return {
                "title": item.get("title"),
                "overview": item.get("overview"),
                "image": item.get("firstimage"),
                "mapx": item.get("mapx"),
                "mapy": item.get("mapy"),
                "areacode": item.get("areacode")
            }
        except Exception as e:
            print("파싱 오류:", e)
    return None
