import json, requests

def detailCommon1(def_params) :
    # 원하는 정보 선택
    params1 = {
        "numOfRows" : 1,
        "pageNo" : 1,
        # "contentTypeId" : "",
        "defaultYN" : "Y",
        "defaultYN" : "Y",
        "firstImageYN" : "Y",
        "areacodeYN" : "Y",
        "catcodeYN" : "Y",
        "addrinfoYN": "Y",
        "mapinfoYN" : "Y",
        "overviewYN" : "Y"
    }

    # 필수 입력
    params1["contentId"] = int(input("콘텐츠 ID를 입력하세요: "))

    operation = "detailCommon1"
    base_params = {
        "serviceKey" : def_params["SERVICE_KEY"],
        "_type" : "json",
        "MobileOS" : "ETC",
        "MobileApp" : "AppTest"
    }
    endpoint = f"{def_params["BASE_URL"]}/{operation}"

    # 전달받은 파라미터와 기본 파라미터 병합
    request_params = {**base_params, **params1}
    response = requests.get(endpoint, params=request_params, timeout=15)

    # 응답 상태 코드 확인
    # 서비스 키는 로그에 남기지 않도록 요청 URL 출력 시 제외
    param_string = "&".join([f"{k}={v}" for k, v in params1.items()])
    print(f"\n요청 URL (서비스키 제외): {endpoint}?MobileOS={def_params['MOBILE_OS']}&MobileApp={def_params['MOBILE_APP']}&_type=json&{param_string}")
    print(f"응답 상태 코드: {response.status_code}")

    data = response.json()

    if 'response' in data and 'header' in data['response']:
        result_code = data['response']['header'].get('resultCode')
        result_msg = data['response']['header'].get('resultMsg')
        print(f"API 결과: {result_code} / {result_msg}")
        if result_code != '0000': # 0000이 정상이 아닐 경우
            print(f"API 오류 발생: {result_msg} (코드: {result_code})")

    print(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False))