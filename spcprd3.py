import json, requests, xmltodict

def localSpcprd3(def_params, region) :

    operation = "localSpcprdLst"
    base_params = {
        "apiKey" : def_params["apiKey"],
    }
    base_params["sAreaNm"] = region


    # base_params["sAreaCode"] = input("시군구 코드 입력: ")
    endpoint = f"{def_params["BASE_URL"]}/{operation}"

    # 전달받은 파라미터와 기본 파라미터 병합
    request_params = {**base_params}
    response = requests.get(endpoint, params=request_params, timeout=15)

    # 응답 상태 코드 확인
    # 서비스 키는 로그에 남기지 않도록 요청 URL 출력 시 제외
    print(f"\n요청 URL (서비스키 제외): {endpoint}?")
    print(f"응답 상태 코드: {response.status_code}")

    print(f"로드된 지역 특산물 API 키: {base_params['apiKey']}... (보안을 위해 일부만 출력)") # 서버 로그에 출력

    items = []
    data = xmltodict.parse(response.text)
    if 'response' in data and 'header' in data['response']:
        items = data['response']['body']['items'].get('item', [])

    return items
