# 앱 팩토리를 호출하고 개발 서버를 실행
from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True는 개발 중에만 사용
    app.run(debug=True)