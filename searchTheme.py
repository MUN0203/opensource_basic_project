import requests
from urllib.parse import urlencode

def searchTheme(def_params, cat1, cat2_list, contentTypeId="12"):
    items = []
    for cat2 in cat2_list:
        params = {
            "serviceKey": def_params["SERVICE_KEY"],
            "MobileOS": def_params["MOBILE_OS"],
            "MobileApp": def_params["MOBILE_APP"],
            "numOfRows": 10,
            "pageNo": 1,
            "arrange": "P",  # 인기순
            "contentTypeId": contentTypeId,  
            "cat1": cat1,
            "cat2": cat2,
            "_type": "json"
        }

        url = f'{def_params["BASE_URL"]}/areaBasedList1?' + urlencode(params)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            items_data = data.get('response', {}).get('body', {}).get('items', None)
            if isinstance(items_data, dict):
                raw_items = items_data.get('item', [])
                # 단일 객체일 수도 있으므로 리스트로 맞춤
                if isinstance(raw_items, dict):
                    raw_items = [raw_items]
                for item in raw_items:
                    item['image'] = item.get('firstimage') or item.get('firstimage2') or None
                    items.append(item)
            else:
                print(f"▶ items가 비어있거나 문자열입니다: {items_data}")
        else:
            print(f"❌ 요청 실패: status {response.status_code}")
    return items
