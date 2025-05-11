# app/__init__.py
# Flask의 애플리케이션 팩토리
from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    # 블루프린트 임포트 및 등록
    from.main import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    # 다른 블루프린트가 추가되면 여기서 등록 (예: app.register_blueprint(auth_bp, url_prefix='/auth'))

    # 간단한 테스트 라우트
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    return app