# TourAPI 4.0을 이용한 여행지 검색&추천 앱
본 프로젝트는 오픈소스SW기초 수업 팀 프로젝트로, 오픈 API와 오픈소스SW를 활용하여 국내 여행지를 추천하고 숙소, 특산품, 날씨 등의 정보를 제공하는 웹 페이지입니다.

## 구현 기능
- 여행지 검색 (해당 지역의 설명, 이미지, 지도 링크, 날씨 정보를 제공)
- 분위기 기반 여행지 추천 (사용자가 원하는 분위기를 선택시 국내 여행지 추천)
- 상세 페이지에서 특산품이나 관광정보를 제공

## 사용 기술 스택
- 프론트엔드 작성 언어: HTML, CSS, JavaScript
- 백엔드 작성 언어: Python
- 웹 프레임워크: Flask (백엔드 ,BSD-3-Clause license)


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

## License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

This project uses the following open-source libraries and APIs:

| Library/API      | License        | Notes |
|-------------------|----------------|-------|
| Flask             | BSD-3-Clause   | Web backend framework |
| Jinja2            | BSD-3-Clause   | HTML template engine |
| TinyDB            | MIT License    | NoSQL database |
| Werkzeug          | BSD-3-Clause   | Flask internal dependency |
| python-dotenv     | BSD-3-Clause   | Environment variable management |
| Flask-Bcrypt      | MIT License    | Password hashing |
| Python            | PSF License    | Programming language |
| TourAPI           | Public API     | Subject to TourAPI usage policy |
| Kakao Map API     | Public API     | Subject to Kakao usage policy |
| 농사로 API         | Public API     | Subject to 농사로 usage policy |
| Open-Meteo API    | Public API     | Subject to Open-Meteo usage policy |
| KR-WordRank       | LGPL License   | Keyword extraction for Korean |
| konlpy            | GPL License    | Stemming for Korean |

> 
> Third-party API services (TourAPI, Kakao Map API, 농사로 API, Open-Meteo API) are used in compliance with their respective terms of service. Please refer to their official documentation for details.