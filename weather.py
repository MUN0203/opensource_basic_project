import openmeteo_requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Union, Optional, Any

# ── WMO 날씨코드 → 한국어 ───────────────────────────
WMO_KR = {
    0: "맑음", 1: "대체로 맑음", 2: "부분적 흐림", 3: "흐림",
    45: "안개", 48: "서리 안개",
    51: "약한 안개비", 53: "안개비", 55: "강한 안개비",
    56: "약한 빗방울(얼음)", 57: "강한 빗방울(얼음)",
    61: "약한 비", 63: "비", 65: "강한 비",
    66: "약한 어는비", 67: "강한 어는비",
    71: "약한 눈", 73: "눈", 75: "강한 눈", 77: "싸락 눈",
    80: "소나기", 81: "강한 소나기", 82: "매우 강한 소나기",
    85: "약한 눈소나기", 86: "강한 눈소나기",
    95: "뇌우", 96: "뇌우(약한 우박)", 99: "뇌우(강한 우박)",
}

def wmo2kr(code: int) -> str:
    return WMO_KR.get(code, "알 수 없음")

def _attr(obj, *names):
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

# ── 메인 함수 (항목별 오류 시 "정보 없음" 문자열 반환) ─────
def get_kma_weather_multi(
    lats: Optional[List[Optional[Union[float, int, str]]]],
    lons: Optional[List[Optional[Union[float, int, str]]]],
    expire_after: int = 3600,
    retries: int = 5,
    backoff_factor: float = 0.2
) -> Union[str, List[Union[Dict[str, Any], str]]]: # 반환 리스트 항목이 Dict 또는 str
    if lats is None or lons is None:
        return "정보 없음" # 함수 전체 입력이 None인 경우

    if len(lats) != len(lons):
        raise ValueError("위도와 경도 리스트의 길이가 동일해야 합니다.")

    if not lats: # 빈 리스트 입력
        return []

    num_coords = len(lats)
    # 최종 결과를 담을 리스트, 초기값은 API 처리 대상을 위해 None으로 설정
    all_results: List[Union[Dict[str, Any], str]] = [None] * num_coords

    valid_lats_for_api: List[float] = []
    valid_lons_for_api: List[float] = []
    original_indices_for_valid: List[int] = []

    for i in range(num_coords):
        lat_item = lats[i]
        lon_item = lons[i]

        is_lat_item_numeric = isinstance(lat_item, (int, float))
        is_lon_item_numeric = isinstance(lon_item, (int, float))

        if not (is_lat_item_numeric and is_lon_item_numeric): # 위도 또는 경도 중 하나라도 유효한 숫자가 아닌 경우
            all_results[i] = "정보 없음" # 해당 항목은 "정보 없음" 문자열로 설정
        else: # lat_item과 lon_item 모두 유효한 숫자인 경우
            valid_lats_for_api.append(float(lat_item))
            valid_lons_for_api.append(float(lon_item))
            original_indices_for_valid.append(i)
            # 유효한 항목의 플레이스홀더는 그대로 None 유지 (API 결과 또는 API 오류 Dict로 채워짐)

    if not valid_lats_for_api: # API로 보낼 유효한 좌표가 하나도 없는 경우
        # all_results는 이미 "정보 없음" 문자열로 채워져 있음
        return all_results

    openmeteo_client = openmeteo_requests.Client()

    params = {
        "latitude":  valid_lats_for_api, "longitude": valid_lons_for_api,
        "models":   ["kma_seamless"], "timezone": "Asia/Seoul",
        "current":  ["temperature_2m", "weather_code"],
        "daily":    ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "forecast_days": 8
    }

    api_responses = None
    try:
        api_responses = openmeteo_client.weather_api("https://api.open-meteo.com/v1/forecast", params)
    except Exception as e:
        print(f"API 요청 중 전체 오류 발생: {e}")
        for err_idx, original_idx in enumerate(original_indices_for_valid):
            # API 호출 실패 시, 해당 항목은 오류 정보를 담은 Dict (위/경도 포함)
            all_results[original_idx] = {
                "latitude": valid_lats_for_api[err_idx],
                "longitude": valid_lons_for_api[err_idx],
                "error_type": "API_CALL_FAILED",
                "message": str(e),
                "current": None,
                "forecast": None
            }
        return all_results

    for api_idx, resp_obj in enumerate(api_responses):
        original_idx = original_indices_for_valid[api_idx]
        
        # API 성공 시, 해당 항목은 날씨 정보를 담은 Dict (위/경도 포함)
        location_data_dict: Dict[str, Any] = {
            "latitude": valid_lats_for_api[api_idx],
            "longitude": valid_lons_for_api[api_idx],
            "timezone_info": {
                "name": _attr(resp_obj,"Timezone").decode() if isinstance(_attr(resp_obj,"Timezone"), bytes) else _attr(resp_obj,"Timezone"),
                "abbreviation": _attr(resp_obj,"TimezoneAbbreviation").decode() if isinstance(_attr(resp_obj,"TimezoneAbbreviation"), bytes) else _attr(resp_obj,"TimezoneAbbreviation"),
                "utc_offset_seconds": _attr(resp_obj,"UtcOffsetSeconds")
            },
            "current": None, "forecast": []
        }
        tz = timezone(timedelta(seconds=location_data_dict["timezone_info"]["utc_offset_seconds"]))

        current_api_data = resp_obj.Current()
        if current_api_data and _series(current_api_data,0) is not None:
            current_ts = _attr(current_api_data, "Time", "Start", "time")
            current_temp = round(_value(_series(current_api_data, 0)), 1)
            current_wmo_code = int(_value(_series(current_api_data, 1)))
            location_data_dict["current"] = {
                "time": datetime.fromtimestamp(current_ts, tz),
                "temperature": current_temp, "weather_code": current_wmo_code,
                "weather_kr": wmo2kr(current_wmo_code)
            }
        else:
            location_data_dict["current"] = {"error": "Current weather data not available from API"}

        daily_api_data = resp_obj.Daily()
        if daily_api_data and _series(daily_api_data,0) is not None:
            daily_ts = _attr(daily_api_data, "Time", "Start", "time")
            start_date_dt = datetime.fromtimestamp(daily_ts, tz).date()
            forecast_dates = []
            num_possible_days = len(_values_np(_series(daily_api_data,0))) if _series(daily_api_data,0) is not None else 0
            for day_offset in range(min(8, num_possible_days)):
                forecast_dates.append(start_date_dt + timedelta(days=day_offset))
            
            num_forecast_days = len(forecast_dates)
            if num_forecast_days > 0:
                temps_max = _values_np(_series(daily_api_data, 0))[:num_forecast_days]
                temps_min = _values_np(_series(daily_api_data, 1))[:num_forecast_days]
                wmo_codes = _values_np(_series(daily_api_data, 2)).astype(int)[:num_forecast_days]
                daily_fc_list = []
                for day_idx in range(num_forecast_days):
                    daily_fc_list.append({
                        "date": forecast_dates[day_idx],
                        "t_max": round(temps_max[day_idx], 1), "t_min": round(temps_min[day_idx], 1),
                        "weather_code": int(wmo_codes[day_idx]), "weather_kr": wmo2kr(int(wmo_codes[day_idx]))
                    })
                location_data_dict["forecast"] = daily_fc_list
            else:
                location_data_dict["forecast"] = [{"error": "Daily forecast data empty or not parseable"}]
        else:
            location_data_dict["forecast"] = [{"error": "Daily forecast data not available from API"}]
        
        all_results[original_idx] = location_data_dict

    return all_results

