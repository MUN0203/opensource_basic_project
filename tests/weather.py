import openmeteo_requests
from datetime import datetime, timedelta, timezone, date
import requests_cache
from retry_requests import retry # retry-requests 임포트

# ── WMO 날씨코드 → 한국어 ───────────────────────────
WMO_KR = {
    0: "맑음", 1: "대체로 맑음", 2: "부분적 흐림",
    3: "흐림",
    45: "안개", 48: "상승하는 안개",
    51: "약한 안개비", 53: "안개비", 55: "강한 안개비",
    56: "약한 빗방울(얼음)", 57: "강한 빗방울(얼음)",
    61: "약한 비", 63: "비", 65: "강한 비",
    66: "약한 어는비", 67: "강한 어는비",
    71: "약한 눈", 73: "눈", 75: "강한 눈",
    77: "눈알/빙정", 80: "소나기", 81: "강한 소나기", 82: "매우 강한 소나기",
    85: "약한 눈소나기", 86: "강한 눈소나기",
    95: "뇌우", 96: "뇌우(약한 우박)", 99: "뇌우(강한 우박)",
}

def wmo2kr(code: int) -> str:
    """WMO 코드를 한국어로 변환(사전에 없으면 '알 수 없음')."""
    return WMO_KR.get(code, "알 수 없음")

# ── 버전 호환 유틸 ─────────────────────────────────
def _attr(obj, *names):
    """첫 번째로 존재하는 메서드/속성 호출 결과 반환"""
    for n in names:
        if hasattr(obj, n):
            m = getattr(obj, n)
            return m() if callable(m) else m
    raise AttributeError(f"{obj} – {names} 모두 없음")

def _series(obj, idx):
    return obj.Series(idx) if hasattr(obj, "Series") else obj.Variables(idx)

def _value(s):
    return _attr(s, "value", "Value")

def _values_np(s):
    return _attr(s, "values_as_numpy", "ValuesAsNumpy")

# ── 메인 함수 (여러 위치 지원) ─────────────────────────
def get_kma_weather_multi(
    lats: list[float],
    lons: list[float],
    expire_after: int = 3600,
    retries: int = 5,
    backoff_factor: float = 0.2
):
    """
    지정된 여러 위도와 경도에 대한 현재 날씨 및 8일 예보를 반환
    API 응답은 캐시되며, 요청 실패 시 재시도

    Parameters
    ----------
    lats : list[float]
        위도 리스트
    lons : list[float]
        경도 리스트 (lats와 동일한 순서 및 길이여야 함)
    expire_after : int, optional
        캐시 만료 시간(초), 기본값 3600 (1시간)
    retries : int, optional
        API 요청 실패 시 재시도 횟수, 기본값 5
    backoff_factor : float, optional
        재시도 간격 계수, 기본값 0.2

    Returns
    -------
    list[dict]
        각 위치별 날씨 정보를 담은 딕셔너리의 리스트.
        각 딕셔너리는 'latitude', 'longitude', 'elevation', 'timezone_info',
        'current', 'forecast' 키를 포함
        오류 발생 시 해당 위치에 대한 정보는 None 또는 오류 메시지를 포함할 수 있음
    """
    if len(lats) != len(lons):
        raise ValueError("위도와 경도 리스트의 길이가 동일해야 합니다.")
    if not lats: # 빈 리스트 입력 방지
        return []

    cache_session = requests_cache.CachedSession(
        '.weather_cache_multi', # 캐시 파일명 변경
        backend='sqlite',
        expire_after=expire_after
    )
    # 캐시 세션에 재시도 로직 적용
    retry_session = retry(cache_session, retries=retries, backoff_factor=backoff_factor)
    openmeteo_client = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude":  lats,
        "longitude": lons,
        "models":   ["kma_seamless"], # 모든 위치에 동일 모델 적용
        "timezone": "Asia/Seoul",     # 모든 위치에 동일 시간대 적용
        "current":  ["temperature_2m", "weather_code"],
        "daily":    ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "forecast_days": 8
    }

    all_results = []

    try:
        api_responses = openmeteo_client.weather_api("https://api.open-meteo.com/v1/forecast", params)
    except Exception as e:
        print(f"API 요청 중 오류 발생: {e}")
        # 모든 위치에 대해 오류 결과 반환
        for lat, lon in zip(lats, lons):
            all_results.append({
                "latitude": lat,
                "longitude": lon,
                "error": str(e),
                "current": None,
                "forecast": None
            })
        return all_results


    for i, resp in enumerate(api_responses): # API는 요청된 좌표 순서대로 응답을 반환
        location_data = {
            "latitude": _attr(resp, "Latitude"),
            "longitude": _attr(resp, "Longitude"),
            "elevation": _attr(resp, "Elevation"),
            "timezone_info": {
                "name": _attr(resp,"Timezone").decode() if isinstance(_attr(resp,"Timezone"), bytes) else _attr(resp,"Timezone"), # bytes일 경우 디코딩
                "abbreviation": _attr(resp,"TimezoneAbbreviation").decode() if isinstance(_attr(resp,"TimezoneAbbreviation"), bytes) else _attr(resp,"TimezoneAbbreviation"),
                "utc_offset_seconds": _attr(resp,"UtcOffsetSeconds")
            },
            "current": None,
            "forecast": []
        }
        
        tz = timezone(timedelta(seconds=location_data["timezone_info"]["utc_offset_seconds"]))

        # ── 현재 날씨 처리 ──
        current_api_data = resp.Current()
        if current_api_data is not None and _series(current_api_data,0) is not None: # 데이터 유효성 체크
            current_ts = _attr(current_api_data, "Time", "Start", "time") # Start, time 순서 고려
            current_temp = round(_value(_series(current_api_data, 0)), 1)
            current_wmo_code = int(_value(_series(current_api_data, 1)))
            
            location_data["current"] = {
                "time": datetime.fromtimestamp(current_ts, tz),
                "temperature": current_temp,
                "weather_code": current_wmo_code,
                "weather_kr": wmo2kr(current_wmo_code)
            }
        else: # 현재 날씨 정보가 없는 경우 (API 응답에 따라 발생 가능)
             location_data["current"] = {"error": "Current weather data not available"}


        # ── 8일 예보 처리 ──
        daily_api_data = resp.Daily()
        if daily_api_data is not None and _series(daily_api_data,0) is not None: # 데이터 유효성 체크
            daily_ts = _attr(daily_api_data, "Time", "Start", "time")
            start_date_dt = datetime.fromtimestamp(daily_ts, tz).date()

            forecast_dates = []
            for day_offset in range(min(8, len(_values_np(_series(daily_api_data,0))))): # API가 8일치 미만 줄 수도 있으니 체크
                forecast_dates.append(start_date_dt + timedelta(days=day_offset))
            
            # 실제 API에서 반환된 일수만큼만 처리
            num_forecast_days = len(forecast_dates)

            temps_max = _values_np(_series(daily_api_data, 0))[:num_forecast_days]
            temps_min = _values_np(_series(daily_api_data, 1))[:num_forecast_days]
            wmo_codes = _values_np(_series(daily_api_data, 2)).astype(int)[:num_forecast_days]

            daily_forecast_list = []
            for day_idx in range(num_forecast_days):
                daily_forecast_list.append({
                    "date": forecast_dates[day_idx],
                    "t_max": round(temps_max[day_idx], 1),
                    "t_min": round(temps_min[day_idx], 1),
                    "weather_code": int(wmo_codes[day_idx]),
                    "weather_kr": wmo2kr(int(wmo_codes[day_idx]))
                })
            location_data["forecast"] = daily_forecast_list
        else: # 예보 정보가 없는 경우
            location_data["forecast"] = [{"error": "Daily forecast data not available"}]


        all_results.append(location_data)

    return all_results

# ── 사용 예시 ──
if __name__ == "__main__":
    # 여러 위치의 위도와 경도 리스트
    # 예시: (1) 서울 시청, (2) 부산 시청 (가상 좌표)
    latitudes = [37.5665, 35.1796]
    longitudes = [126.9780, 129.0756]

    print("여러 위치 날씨 정보 요청 (첫 번째 호출 시 API 요청):")
    weather_data_list = get_kma_weather_multi(latitudes, longitudes)

    for i, weather_data in enumerate(weather_data_list):
        print(f"\n--- 위치 {i+1}: {weather_data.get('latitude')}°N, {weather_data.get('longitude')}°E ---")
        if "error" in weather_data and weather_data["current"] is None :
            print(f"  오류: {weather_data['error']}")
            continue

        print(f"  고도: {weather_data.get('elevation')} m")
        # print(f"  시간대: {weather_data.get('timezone_info')}") # 상세 시간대 정보
        
        current_weather = weather_data.get("current")
        if current_weather and "error" not in current_weather:
            print(f"  현재 날씨 ({current_weather['time'].strftime('%Y-%m-%d %H:%M')}):")
            print(f"    기온: {current_weather['temperature']}°C, 상태: {current_weather['weather_kr']} (코드: {current_weather['weather_code']})")
        elif current_weather and "error" in current_weather:
             print(f"  현재 날씨: {current_weather['error']}")
        else:
            print("  현재 날씨 정보 없음")


        print("  --- 8일 예보 ---")
        forecast_list = weather_data.get("forecast", [])
        if forecast_list and "error" not in forecast_list[0]:
            for daily_forecast in forecast_list:
                print(f"    {daily_forecast['date']}: "
                      f"최고 {daily_forecast['t_max']}°C, "
                      f"최저 {daily_forecast['t_min']}°C, "
                      f"상태: {daily_forecast['weather_kr']} (코드: {daily_forecast['weather_code']})")
        elif forecast_list and "error" in forecast_list[0]:
            print(f"    예보: {forecast_list[0]['error']}")
        else:
            print("    예보 정보 없음")


    print("\n\n두 번째 호출 (캐시된 데이터 사용 가능):")
    weather_data_list_cached = get_kma_weather_multi(latitudes, longitudes)
    # (출력은 위와 유사하므로 생략)
    if weather_data_list_cached and weather_data_list_cached[0].get('current'):
        print(f"두 번째 호출 - 첫 번째 위치 현재 시각: {weather_data_list_cached[0]['current']['time']}")
    else:
        print("두 번째 호출 데이터 확인 필요.")