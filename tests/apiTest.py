import requests
import json

import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import config

BASE_URL = "http://apis.data.go.kr/B551011/KorService1"

# --- 사용자 설정 영역 ---
SERVICE_KEY = config.Config.getTOUR_API_KEY()
# 서비스 호출 시 필수 파라미터
MOBILE_OS = "ETC" # 예: "IOS", "AND", "WIN", "ETC" (기타)
MOBILE_APP = "MyTravelApp" # 개발 중인 서비스명 또는 앱 이름
# ---------------------

def call_tour_api(operation, params={}):
    """
    TourAPI를 호출하는 함수

    Args:
        operation (str): 호출할 오퍼레이션 명 (예: 'areaBasedList1', 'searchKeyword1')
        params (dict, optional): API 호출 시 필요한 파라미터 딕셔너리.
                                 기본 파라미터(serviceKey, MobileOS, MobileApp, _type)는 자동으로 추가됩니다.
                                 Defaults to {}.

    Returns:
        dict: API 응답 결과 (JSON 파싱된 딕셔너리)
        None: API 호출 실패 시
    """
    if SERVICE_KEY == "YOUR_SERVICE_KEY" or len(SERVICE_KEY) < 50: # 서비스키 유효성 간이 체크
        print("오류: SERVICE_KEY를 실제 발급받은 키로 변경해주세요.")
        return None

    endpoint = f"{BASE_URL}/{operation}"

    # 기본 파라미터 설정
    base_params = {
        "serviceKey": SERVICE_KEY,
        "MobileOS": MOBILE_OS,
        "MobileApp": MOBILE_APP,
        "_type": "json"  # 응답 형식을 JSON으로 요청
    }

    # 전달받은 파라미터와 기본 파라미터 병합
    request_params = {**base_params, **params}

    try:
        # 서비스 키가 URL에 노출되지 않도록 params 인자로 전달
        response = requests.get(endpoint, params=request_params, timeout=15)
        response.raise_for_status() # 오류 발생 시 예외 발생 (4xx, 5xx)

        # 응답 상태 코드 확인
        # 서비스 키는 로그에 남기지 않도록 요청 URL 출력 시 제외
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        print(f"\n요청 URL (서비스키 제외): {endpoint}?MobileOS={MOBILE_OS}&MobileApp={MOBILE_APP}&_type=json&{param_string}")
        print(f"응답 상태 코드: {response.status_code}")

        # JSON 응답 파싱 시도
        try:
            data = response.json()
            # API 자체 에러 코드 확인 
            if 'response' in data and 'header' in data['response']:
                result_code = data['response']['header'].get('resultCode')
                result_msg = data['response']['header'].get('resultMsg')
                print(f"API 결과: {result_code} / {result_msg}")
                if result_code != '0000': # 0000이 정상이 아닐 경우
                    print(f"API 오류 발생: {result_msg} (코드: {result_code})")
            return data
        except json.JSONDecodeError:
            print("오류: JSON 응답을 파싱할 수 없습니다.")
            print("응답 내용:", response.text)
            return None

    except requests.exceptions.Timeout:
        print("HTTP 요청 시간 초과")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return None

# --- API 호출 예시 ---
if __name__ == "__main__":

    # 예시 1: 키워드 검색
    # '힐링' 키워드로 관광지(contentTypeId=12) 검색
    print("\n--- 예시 1: 키워드 검색 ('힐링' 관광지) ---")
    keyword_params = {
        "numOfRows": 3,     # 3개 결과만 가져오기 (옵션)
        "pageNo": 1,        # 1페이지 (옵션)
        "arrange": "A",     # 제목순 정렬 (옵션)
        "contentTypeId": 12, # 관광지 타입 (옵션, 없으면 전체 타입 검색)
        "keyword": "힐링"    # 필수 검색 키워드
    }
    keyword_result = call_tour_api("searchKeyword1", keyword_params)
    if keyword_result and 'response' in keyword_result and 'body' in keyword_result['response'] and 'items' in keyword_result['response']['body']:
        items_container = keyword_result['response']['body']['items']
        items = []

        if isinstance(items_container, dict) and 'item' in items_container:
            item_data = items_container.get('item')
            if isinstance(item_data, list):
                items = item_data
            elif isinstance(item_data, dict):
                items = [item_data]
        elif isinstance(items_container, str) and items_container == '':
            print("키워드 검색 결과 'items'가 비어 있습니다.")

        if items:
            print(f"검색된 '힐링' 관광지 수: {len(items)}")
            for item in items:
                print(f" - 제목: {item.get('title')}, 주소: {item.get('addr1')}")
        else:
            print("검색 결과가 없습니다.")

    # 예시 2: 지역 기반 검색
    # 서울(areaCode=1) 강남구(sigunguCode=1)의 레포츠(contentTypeId=28) 시설 검색
    print("\n--- 예시 2: 지역 기반 검색 (서울 강남구 레포츠) ---")
    area_params = {
        "numOfRows": 3,
        "pageNo": 1,
        "arrange": "A",
        "contentTypeId": 28, # 레포츠 타입
        "areaCode": 1,      # 지역코드 (서울)
        "sigunguCode": 1    # 시군구코드 (강남구)
    }
    area_result = call_tour_api("areaBasedList1", area_params)
    if area_result and 'response' in area_result and 'body' in area_result['response'] and 'items' in area_result['response']['body']:
        items_container = area_result['response']['body']['items']
        items = []

        if isinstance(items_container, dict) and 'item' in items_container:
            item_data = items_container.get('item')
            if isinstance(item_data, list):
                items = item_data
            elif isinstance(item_data, dict):
                items = [item_data]
        elif isinstance(items_container, str) and items_container == '':
             print("지역 기반 검색 결과 'items'가 비어 있습니다.")

        if items:
            print(f"검색된 레포츠 시설 수: {len(items)}")
            for item in items:
                print(f" - 제목: {item.get('title')}, 주소: {item.get('addr1')}")
        else:
            print("검색 결과가 없습니다.")


    # 예시 3: 음식점 상세 정보 조회
    # 특정 콘텐츠 ID(예: 134546 - 매뉴얼 예시)의 소개 정보 조회
    print("\n--- 예시 3: 상세 정보 조회 (음식점 소개) ---")
    # contentId는 예시이며, 실제 존재하는 ID로 테스트해야 합니다.
    # 목록 조회(areaBasedList1 등)를 통해 얻은 contentId를 사용하세요.
    detail_intro_params = {
        "contentId": 134546,   # 필수 콘텐츠 ID
        "contentTypeId": 39   # 필수 콘텐츠 타입 (음식점)
    }
    detail_intro_result = call_tour_api("detailIntro1", detail_intro_params)
    # 응답 구조 확인 및 items 추출
    items_data = None
    if detail_intro_result and 'response' in detail_intro_result and 'body' in detail_intro_result['response']:
        body = detail_intro_result['response']['body']
        if 'items' in body:
            items_container = body['items']
            # items_container가 dict이고 내부에 item이 있는 경우 추출
            if isinstance(items_container, dict) and 'item' in items_container:
                items_data = items_container.get('item')
            # items_container가 비어있는 문자열인 경우 처리
            elif isinstance(items_container, str) and items_container == '':
                print(f"ID {detail_intro_params['contentId']}에 대한 'items' 정보가 비어 있습니다 (문자열).")
            # items_container가 아예 없는 경우 등은 items_data가 None으로 유지됨
            elif not items_container:
                 print(f"ID {detail_intro_params['contentId']}에 대한 'items' 정보가 없습니다.")

    # items_data가 성공적으로 추출되었고, 딕셔너리 형태인지 확인 후 처리
    if isinstance(items_data, dict) and items_data:
        print(f"음식점 정보 조회 (ID: {items_data.get('contentid')})")
        print(f" - 대표메뉴: {items_data.get('firstmenu')}")
        print(f" - 취급메뉴: {items_data.get('treatmenu')}")
        print(f" - 영업시간: {items_data.get('opentimefood')}")
        print(f" - 쉬는날: {items_data.get('restdatefood')}")
    else:
        # items_data가 None이거나 비어있는 dict인 경우
        print(f"ID {detail_intro_params['contentId']}에 대한 상세 정보 조회 결과가 없거나 처리할 수 없는 형식입니다.")


    # 예시 4: 이미지 정보 조회
    # 특정 콘텐츠 ID(예: 1095732 - 매뉴얼 예시)의 이미지 조회
    print("\n--- 예시 4: 이미지 정보 조회 ---")
    # contentId는 예시이며, 실제 존재하는 ID로 테스트해야 합니다.
    image_params = {
        "contentId": 1095732, # 필수 콘텐츠 ID
        "imageYN": "Y",       # 콘텐츠 이미지 조회 (Y)
        "subImageYN": "Y"     # 원본, 썸네일 이미지 모두 조회 (Y)
    }
    image_result = call_tour_api("detailImage1", image_params)
    if image_result and 'response' in image_result and 'body' in image_result['response'] and 'items' in image_result['response']['body']:
        items_container = image_result['response']['body']['items']
        items = []

        if isinstance(items_container, dict) and 'item' in items_container:
            item_data = items_container.get('item')
            if isinstance(item_data, list):
                items = item_data
            elif isinstance(item_data, dict):
                items = [item_data]
        elif isinstance(items_container, str) and items_container == '':
             print("이미지 정보 조회 결과 'items'가 비어 있습니다.")

        if items:
            print(f"이미지 정보 수: {len(items)}")
            for item in items:
                print(f" - 원본 이미지 URL: {item.get('originimgurl')}")
        else:
            print("이미지 정보가 없습니다.")

    # 예시 5: 반려동물 동반 정보 조회
    # 특정 콘텐츠 ID(예: 125534 - 매뉴얼 예시)의 반려동물 정보 조회
    print("\n--- 예시 5: 반려동물 동반 정보 조회 ---")
    # contentId는 예시이며, 실제 존재하는 ID로 테스트해야 합니다.
    pet_params = {
        "contentId": 125534 # 필수 콘텐츠 ID (없으면 전체 반려동물 정보 출력 시도)
    }
    pet_result = call_tour_api("detailPetTour1", pet_params)
    # 응답 구조 확인 및 items 추출 (상세 정보이므로 item 1개 예상)
    items_data = None
    if pet_result and 'response' in pet_result and 'body' in pet_result['response']:
        body = pet_result['response']['body']
        if 'items' in body:
            items_container = body['items']
            if isinstance(items_container, dict) and 'item' in items_container:
                items_data = items_container.get('item')
            elif isinstance(items_container, str) and items_container == '':
                 print(f"ID {pet_params['contentId']}에 대한 반려동물 'items' 정보가 비어 있습니다 (문자열).")
            elif not items_container:
                 print(f"ID {pet_params['contentId']}에 대한 반려동물 'items' 정보가 없습니다.")

    # items_data가 성공적으로 추출되었고, 딕셔너리 형태인지 확인 후 처리
    if isinstance(items_data, dict) and items_data:
        print(f"반려동물 정보 조회 (ID: {items_data.get('contentid')})")
        print(f" - 동반 가능 동물: {items_data.get('acmpyPsblCpam')}")
        print(f" - 동반 시 필요사항: {items_data.get('acmpyNeedMtr')}")
        print(f" - 기타 동반 정보: {items_data.get('etcAcmpyInfo')}")
    else:
        # items_data가 None이거나 비어있는 dict인 경우
        print(f"ID {pet_params['contentId']}에 대한 반려동물 정보 조회 결과가 없거나 처리할 수 없는 형식입니다.")


    print("\n--- 모든 예시 실행 완료 ---")