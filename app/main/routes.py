from flask import render_template, request
from. import bp # 현재 패키지(main)의 __init__.py 에서 bp 임포트

@bp.route('/')
def index():
    """메인 페이지 라우트. 분위기 선택 옵션을 제공합니다."""
    moods = ["힐링", "사진 명소", "먹거리", "액티비티"]
    return render_template('main/index.html', title='여행지 추천', moods=moods)