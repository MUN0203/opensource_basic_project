# TourAPI 4.0을 이용한 여행지 검색&추천 앱
본 프로젝트는 오픈소스SW기초 수업 팀 프로젝트로, 오픈 API와 오픈소스SW를 활용하여 국내 여행지를 추천하고 숙소, 특산품, 날씨 등의 정보를 제공하는 웹 페이지입니다.

## 구현 기능
- 분위기 기반 여행지 추천 (사용자가 원하는 분위기, 지역 등을 선택시 검색이나 랜덤으로 국내 여행지 추천)
- 해당 지역의 날씨정보를 제공
- 해당 지역의 특산품이나 관광정보를 제공

## 사용 기술 스택
- 프론트엔드 작성 언어: HTML, CSS, JavaScript
- 백엔드 작성 언어: Python
- 웹 프레임워크: Flask (백엔드 ,BSD-3-Clause license), Bootstrap (프론트엔드, MIT License)


## 개발 환경 설정 방법

### Github 저장소
https://github.com/MUN0203/opensource_basic_project

### 가상환경 생성 및 활성화
#### 1. 가상환경 설정
    python3 -m venv .venv

#### 2. 가상환경 활성화 / 비활성화
- **macOS / Linux (bash/zsh)**: `source .venv/bin/activate`
- **Windows (Command Prompt)**: `.venv\Scripts\activate.bat`
- **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
- 비활성화: `deactivate`

#### 3. 라이브러리 설치
    pip3 install -r requirements.txt