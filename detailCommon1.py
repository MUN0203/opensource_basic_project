"""
관광지 상세 설명만 출력
"""
import json, requests

def detailCommon1(def_params, contentId) :
    # 원하는 정보 선택
    params1 = {
        "numOfRows" : 10,
        "pageNo" : 1,
        "defaultYN" : "Y",
        "firstImageYN" : "Y",
        "areacodeYN" : "Y",
        "catcodeYN" : "Y",
        "addrinfoYN": "Y",
        "mapinfoYN" : "Y",
        "overviewYN" : "Y"
    }

    # 필수 입력
    params1["contentId"] = contentId

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

    return data["response"]["body"]["items"]