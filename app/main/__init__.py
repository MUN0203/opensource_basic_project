# app/main/__init__.py, 블루프린트 구현
from flask import Blueprint

# 'main'은 블루프린트의 이름, __name__은 현재 모듈의 이름
bp = Blueprint('main', __name__)

# 블루프린트 생성 후 라우트 모듈 임포트 (순환 참조 방지)
from. import routes