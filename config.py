import os
from dotenv import load_dotenv # `pip install python-dotenv` 필요

basedir = os.path.abspath(os.path.dirname(__file__))
# .env 파일에서 환경 변수 로드
# .env 파일 내용: TOUR_API_KEY='API키'
load_dotenv(os.path.join(basedir, '.env'))

dotenv_path = os.path.join(basedir, '.env')

# 디버깅
print(f"Attempting to load .env file from: {dotenv_path}") # .env 파일 경로 출력
print(f".env file exists: {os.path.exists(dotenv_path)}") # .env 파일 존재 여부 출력

class Config:
    # 한국관광공사 TourAPI 일반 인증키 (Decoding 된 값)
    __TOUR_API_KEY = os.environ.get('TOUR_API_KEY')
    
    # 지역 특산물 API 키
    __SPCPRD_API_KEY = os.environ.get('SPCPRD_API_KEY')
    @classmethod
    def getTOUR_API_KEY(self) :
        return self.__TOUR_API_KEY  
    
    @classmethod
    def getSPCPRD_API_KEY(self) :
        return self.__SPCPRD_API_KEY