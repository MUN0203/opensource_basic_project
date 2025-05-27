import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import config

from tests.areaCode import areaCode
from tests.categoryCode1 import categoryCode1
from tests.areaBasedList1 import areaBasedList1
from tests.locationBasedList1 import locationBasedList1
from tests.searchKeyword1 import searchKeyword1
from tests.searchFestival1 import searchFestival1
from tests.searchStay1 import searchStay1
from tests.detailCommmon1 import detailCommon1
from tests.detailIntro1 import detailIntro1
from tests.detailInfo1 import detailInfo11
from tests.detailImage1 import detailImage1
from tests.areaBasedSyncList1 import areaBasedSyncList1
from tests.detailPetTour1 import detailPetTour1
from tests.spcprd import localSpcprd
from tests.spcprd2 import localSpcprd2
from tests.spcprd3 import localSpcprd3


def_params = {
    "SERVICE_KEY" : config.Config.getTOUR_API_KEY(),
    # 서비스 호출 시 필수 파라미터
    "MOBILE_OS" : "ETC", # 예: "IOS", "AND", "WIN", "ETC" (기타)
    "MOBILE_APP" : "MyTravelApp", # 개발 중인 서비스명 또는 앱 이름
    "BASE_URL" : "http://apis.data.go.kr/B551011/KorService1"
}

def_params2 = {
    "SERVICE_KEY" : config.Config.getSPCPRD_API_KEY(),
    "BASE_URL" : "http://api.nongsaro.go.kr/service/localSpcprd"
}

print("1. 지역 코드 조회")
print("2. 서비스 분류 코드 조회")
print("3. 지역 기반 관광 정보 조회")
print("4. 위치 기반 관광 정보 조회")
print("5. 키워드 검색 조회")
print("6. 행사 정보 조회")
print("7. 숙박 정보 조회")
print("8. 공통 정보 조회")
print("9. 소개 정보 조회")
print("10. 반복 정보 조회")
print("11. 이미지 정보 조회")
print("12. 국문관광정보 동기화 목록 조회")
print("13. 국문관광정보 반려동물 여행 정보")

print("14. 지역 특산물 정보 / 시도 데이터 목록")
print("15. 지역 특산물 정보 / 시군구 데이터 목록")
print("16. 지역 특산물 정보")

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

elif select == 6 :
    # 행사 정보 조회
    searchFestival1(def_params)

elif select == 7 :
    # 숙박 정보 조회
    searchStay1(def_params)

elif select == 8 :
    # 공통 정보 조회
    detailCommon1(def_params)

elif select == 9 :
    # 소개 정보 조회
    detailIntro1(def_params)

elif select == 10 :
    # 반복 정보 조회
    detailInfo11(def_params)

elif select == 11 :
    # 반복 정보 조회
    detailImage1(def_params)

elif select == 12 :
    # 국문관광정보 동기화 목록 조회
    areaBasedSyncList1(def_params)

elif select == 13 :
    # 국문관광정보 반려동물 여행 정보
    detailPetTour1(def_params)

elif select == 14 :
    # 지역 특산물 정보 / 시도 데이터 목록
    localSpcprd(def_params2)

elif select == 15 :
    # 지역 특산물 정보 / 시군구 데이터 목록
    localSpcprd2(def_params2)

elif select == 16 :
    # 지역 특산물 정보 / 지역 특산물 목록
    localSpcprd3(def_params2)