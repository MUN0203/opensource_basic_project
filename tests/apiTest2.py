import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import config

from areaCode import areaCode
from categoryCode1 import categoryCode1
from areaBasedList1 import areaBasedList1
from locationBasedList1 import locationBasedList1
from searchKeyword1 import searchKeyword1


def_params = {
    "SERVICE_KEY" : config.Config.getTOUR_API_KEY(),
    # 서비스 호출 시 필수 파라미터
    "MOBILE_OS" : "ETC", # 예: "IOS", "AND", "WIN", "ETC" (기타)
    "MOBILE_APP" : "MyTravelApp", # 개발 중인 서비스명 또는 앱 이름
    "BASE_URL" : "http://apis.data.go.kr/B551011/KorService1"
}

print("1. 지역 코드 조회")
print("2. 서비스 분류 코드 조회")
print("3. 지역 기반 관광 정보 조회")
print("4. 위치 기반 관광 정보 조회")
print("5. 키워드 검색 조회")

select = int(input("번호 입력: "))

if select == 1 :
   # 지역코드 조회
   areaCode(def_params)

elif select == 2 :
    # 서비스분류코드 조회
    categoryCode1(def_params)

elif select == 3 :
    # 지역 기반 관광 정보 조회
    areaBasedList1(def_params)

elif select == 4 :
    # 위치 기반 관광 정보 조회
    locationBasedList1(def_params)

elif select == 5 :
    # 키워드 검색 조회
    searchKeyword1(def_params)