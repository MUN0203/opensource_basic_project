import os
from dotenv import load_dotenv # `pip install python-dotenv` 필요

basedir = os.path.abspath(os.path.dirname(__file__))
# .env 파일에서 환경 변수 로드
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 한국관광공사 TourAPI 일반 인증키 (Decoding 된 값)
    TOUR_API_KEY = os.environ.get('TOUR_API_KEY')
    