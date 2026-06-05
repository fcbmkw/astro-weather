import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt
import math
import ephem

# --- CƠ SỞ DỮ LIỆU ĐỊA ĐIỂM ---
LOCATION_DATABASE = {
    "1. Jogashima, Miura, Kanagawa": [35.1386, 139.6179],
    "2. Tateyama, Chiba": [34.9818, 139.8523],
    "3. Minamiboso, Chiba": [34.9386, 139.9239],
    "4. Onjuku, Chiba": [35.1764, 140.3551],
    "5. Isumi, Chiba": [35.2447, 140.3908],
    "6. Manazuru, Kanagawa": [35.1558, 139.1481],
    "7. Shimoda, Shizuoka": [34.6465, 138.9886],
    "8. Minamiizu, Shizuoka": [34.6181, 138.8247],
    "9. Matsuzaki, Shizuoka": [34.7214, 138.7756],
    "10. Okuoikojo, Shizuoka": [35.0336, 138.1633],
    "11. Asagiri Arena Parking, Shizuoka": [35.3831, 138.5836],
    "12. Shoji-ko, Yamanashi": [35.4578, 138.6044],
    "13. Hanamomo-no-sato, Nagano": [35.4300, 137.7667],
    "14. Otaki, Nagano": [35.8672, 137.6442],
    "15. Kamikochi, Nagano": [36.2428, 137.6356],
    "16. Nakabusa, Azumino, Nagano": [36.3861, 137.7472],
    "17. Wada, Nagawa, Nagano": [36.2081, 138.1408],
    "18. Maeyama, Saku, Nagano": [36.2483, 138.4550],
    "19. Tsumagoi, Gunma": [36.5050, 138.5300],
    "20. Kusatsu, Gunma": [36.6214, 138.5958],
    "21. Kurabuchi, Takasaki, Gunma": [36.3800, 138.7600],
    "22. Kamihotchimachi, Numata, Gunma": [36.6347, 139.0461],
    "23. Takinemachi, Fukushima": [37.3325, 140.7011]
}

st.set_page_config(page_title="Astro Map Pro", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 2rem; padding-right: 2rem; }
    iframe { width: 100% !important; }
    .stTable table { width: 100% !important; margin-bottom: 0px !important; }
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .source-card {
        background-color: #1e293b;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
        padding: 10px 15px 4px 15px;
    }
    .geo-highlight {
        font-family: 'Courier New', monospace;
        font-size: 19px;
        font-weight: bold;
        line-height: 1.6;
        margin-top: 5px;
    }
    .zenith-subtext {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
        border-top: 1px solid #475569;
        padding-top: 6px;
    }
    .footer-copyright {
        text-align: center; color: #64748b; font-size: 13px;
        font-weight: 500; margin-top: 30px; padding-top: 15px;
        border-top: 1px solid #334155;
    }
    /* Shrink gap between source label div and the selectbox below it */
    .source-card + div { margin-top: -10px !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in [("lat", 35.6895), ("lon", 139.6917),
             ("map_center", [35.6895, 139.6917]), ("zoom", 9),
             ("day_offset", 0), ("location_name", "Tokyo, Japan"),
             ("is_custom_point", True), ("weather_source", "JMA"),
             ("active_source_used", "JMA"),
             ("_last_tip", None), ("_last_lc", None),
             ("_source_auto", True), ("_ecmwf_available", True),
             ("map_tile", "satellite")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)   # cache 1 giờ — tên địa điểm không đổi
def fetch_location_name(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    try:
        res = requests.get(url, headers={"User-Agent": "AstroMapPro/7.0"}, timeout=3)
        if res.status_code == 200:
            addr = res.json().get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county")
            state = addr.get("state")
            if city and state: return f"{city}, {state}"
            return state or city or "Unknown"
    except: pass
    return "Unknown Location"

def get_moon_phase_percent(date_obj):
    base = datetime(2024, 1, 11)
    phase = ((date_obj - base).total_seconds() / 86400.0 / 29.53059) % 1.0
    illum = round((1 - math.cos(phase * 2 * math.pi)) / 2 * 100, 1)
    if phase < 0.03 or phase > 0.97: desc = "Trăng Non (New Moon) 🌌"
    elif phase < 0.22: desc = "Trăng Lưỡi Liềm Đầu Tháng"
    elif phase < 0.28: desc = "Trăng Bán Nguyệt Đầu Tháng"
    elif phase < 0.47: desc = "Trăng Khuyết Đầu Tháng"
    elif phase < 0.53: desc = "Trăng Tròn (Full Moon) 🌕"
    elif phase < 0.72: desc = "Trăng Khuyết Cuối Tháng"
    elif phase < 0.78: desc = "Trăng Bán Nguyệt Cuối Tháng"
    else: desc = "Trăng Lưỡi Liềm Cuối Tháng"
    return illum, desc

@st.cache_data(ttl=86400, show_spinner=False)  # cache 24 giờ — quỹ đạo trăng không đổi trong ngày
def calculate_exact_moon_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao mặt trăng (có thể âm khi dưới đường chân trời).
    utc_offset_h là offset của location (JST=+9, CST=-6, v.v.)"""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0  # tắt refraction để góc âm chính xác
    local_dt = datetime(year, month, day, hour_local, 0, 0)
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    moon = ephem.Moon(); moon.compute(obs)
    return round(math.degrees(float(moon.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_exact_sun_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao mặt trời (có thể âm khi dưới đường chân trời = ban đêm).
    utc_offset_h là offset của location (JST=+9, CST=-6, v.v.)"""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0  # tắt refraction để góc âm chính xác
    local_dt = datetime(year, month, day, hour_local, 0, 0)
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    sun = ephem.Sun(); sun.compute(obs)
    return round(math.degrees(float(sun.alt)), 1)

def calculate_zenith_ra_dec(lat, lon):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    d = (now - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    lst = (18.697374558 + 24.06570982441908 * d + lon / 15.0) % 24
    ra_h, ra_m = int(lst), int((lst % 1) * 60)
    dec_d, dec_m = int(lat), int((lat % 1) * 60)
    return f"{ra_h:02d}h {ra_m:02d}m", f"{dec_d:+03d}° {dec_m:02d}'"

def calculate_accurate_bortle(lat, lon):
    cities = {
        "Tokyo": (35.6895, 139.6917), "Yokohama": (35.4437, 139.6380),
        "Nagoya": (35.1815, 136.9066), "Chiba": (35.6074, 140.1063), "Saitama": (35.8616, 139.6455)
    }
    min_dist = min(
        math.sqrt(((lon-p[1])*111*math.cos(math.radians(lat)))**2 + ((lat-p[0])*111)**2)
        for p in cities.values()
    )
    if math.sqrt(((lon-137.98)*90)**2 + ((lat-35.92)*111)**2) < 22.0: return 3, 21.75
    if lat < 35.15 and 139.60 < lon < 139.90: return 4, 21.20
    if min_dist <= 12: return 9, 18.10
    elif min_dist <= 25: return 7, 19.20
    elif min_dist <= 45: return 6, 20.10
    elif min_dist <= 75: return 5, 20.80
    elif min_dist <= 110: return 4, 21.30
    else: return 3, 21.80

# ── WEATHER FETCH ─────────────────────────────────────────────────────────────
# Các endpoint fallback theo thứ tự ưu tiên:
#   1. Primary: tất cả 3 models (JMA + ECMWF + GFS) — đầy đủ nhất
#   2. Fallback A: chỉ GFS + ECMWF (bỏ JMA) — nhẹ hơn, ít lỗi hơn
#   3. Fallback B: chỉ GFS — luôn hoạt động, không phụ thuộc Japan server
_FIELDS = "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,relative_humidity_2m,wind_speed_10m"
_ENDPOINTS = [
    # (label, url_suffix)
    ("full",    f"&hourly={_FIELDS}&models=jma_msm,gfs_seamless,ecmwf_ifs025&wind_speed_unit=ms&timezone=auto"),
    ("no_jma",  f"&hourly={_FIELDS}&models=gfs_seamless,ecmwf_ifs025&wind_speed_unit=ms&timezone=auto"),
    ("gfs_only",f"&hourly={_FIELDS}&models=gfs_seamless&wind_speed_unit=ms&timezone=auto"),
]

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_weather_raw(lat, lon):
    """Raw API fetch với retry + multi-endpoint fallback.
    Returns (hourly_dict, utc_offset_seconds, endpoint_used_label)"""
    base = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    for ep_label, ep_suffix in _ENDPOINTS:
        url = base + ep_suffix
        for attempt in range(2):   # 2 lần thử mỗi endpoint
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    j = res.json()
                    return j.get("hourly", {}), j.get("utc_offset_seconds", 32400), ep_label
                # 5xx = server lỗi → thử endpoint tiếp theo ngay
                if res.status_code >= 500:
                    break
            except requests.exceptions.Timeout:
                pass   # timeout → thử lại 1 lần, sau đó chuyển endpoint
            except Exception:
                break  # lỗi khác → chuyển endpoint ngay
    return {}, 32400, "offline"

def fetch_weather_7days(lat, lon, source="JMA"):
    """Wrapper giữ nguyên interface cũ — delegate sang cached raw fetch."""
    hourly, utc_offset, ep_label = _fetch_weather_raw(lat, lon)
    return hourly, source, utc_offset, ep_label

def get_val(hourly, field, idx, prefer_jma=True):
    """
    Extract a single numeric value for a field at index idx.
    If prefer_jma: try _jma_msm first, fallback to _gfs_seamless.
    Else: try _gfs_seamless first, fallback to _jma_msm.
    Also tries bare key as last resort.
    Returns (float_value, source_used: 'JMA'|'GFS'|None)
    """
    order = ["_jma_msm", "_gfs_seamless"] if prefer_jma else ["_gfs_seamless", "_jma_msm"]
    labels = ["JMA", "GFS"] if prefer_jma else ["GFS", "JMA"]
    for suffix, label in zip(order, labels):
        lst = hourly.get(f"{field}{suffix}", [])
        if idx < len(lst) and lst[idx] is not None:
            return float(lst[idx]), label
    # bare key fallback
    lst = hourly.get(field, [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx]), "?"
    return 0.0, None

def _get_raw(hourly, field, suffix, idx):
    """Get raw value for a specific model suffix. Returns None if missing."""
    lst = hourly.get(f"{field}{suffix}", [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx])
    return None

def get_val_blended(hourly, field, idx, day_offset):
    """
    Weighted blend of JMA + ECMWF + GFS based on day_offset.
    Day 0-3: JMA x0.60 + ECMWF x0.30 + GFS x0.10  (JMA MSM 3km grid, best short-range for Japan)
    Day 4-7: ECMWF x0.55 + GFS x0.30 + JMA x0.15  (JMA MSM coverage ends ~day 3.5)
    Re-normalises weights if any model has missing data.
    Returns (float_value, label_string)
    """
    jma   = _get_raw(hourly, field, "_jma_msm",      idx)
    ecmwf = _get_raw(hourly, field, "_ecmwf_ifs025",  idx)
    gfs   = _get_raw(hourly, field, "_gfs_seamless",  idx)

    if day_offset <= 3:
        weights = {"jma": 0.60, "ecmwf": 0.30, "gfs": 0.10}
    else:
        weights = {"jma": 0.15, "ecmwf": 0.55, "gfs": 0.30}

    vals  = {"jma": jma, "ecmwf": ecmwf, "gfs": gfs}
    avail = {k: v for k, v in vals.items() if v is not None}
    if not avail:
        return 0.0, None

    total_w = sum(weights[k] for k in avail)
    blended = sum(weights[k] * v for k, v in avail.items()) / total_w
    return round(blended, 1), "Blend"

# ── COMPUTED STATE ────────────────────────────────────────────────────────────
bortle_class, sqm_val = calculate_accurate_bortle(st.session_state.lat, st.session_state.lon)
ra_val, dec_val = calculate_zenith_ra_dec(st.session_state.lat, st.session_state.lon)

JST = timezone(timedelta(hours=9))
date_options = [
    f"Đêm {(datetime.now(JST)+timedelta(days=i)).strftime('%d/%m')} ➔ Sáng {(datetime.now(JST)+timedelta(days=i+1)).strftime('%d/%m')}"
    for i in range(7)
]

target_date = (datetime.now(JST) + timedelta(days=st.session_state.day_offset)).replace(tzinfo=None)
next_date   = target_date + timedelta(days=1)

moon_pct, moon_text = get_moon_phase_percent(target_date)

prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Tổng hợp (Best)")
use_ecmwf  = (st.session_state.weather_source == "EU (ECMWF)")
hourly_data, _, _loc_utc_offset, _ep_label = fetch_weather_7days(st.session_state.lat, st.session_state.lon, st.session_state.weather_source)

# ── AUTO-DETECT JMA COVERAGE cho ngày được chọn ───────────────────────────────
# JMA MSM chỉ có ~3-4 ngày. Nếu user chọn JMA nhưng ngày đó JMA toàn null
# → tự động dùng GFS thay thế (prefer_jma=False) mà không cần user đổi tay.
def _jma_has_data_for_date(hourly, date_prefix):
    """Trả về True nếu JMA có ít nhất 1 giá trị không-None cho ngày date_prefix."""
    times = hourly.get("time", [])
    cc_jma = hourly.get("cloud_cover_jma_msm", [])
    for i, t in enumerate(times):
        if t.startswith(date_prefix) and i < len(cc_jma) and cc_jma[i] is not None:
            return True
    return False

# Auto-switch: luôn kiểm tra JMA coverage nếu đang ở chế độ auto (kể cả khi đang dùng GFS)
if st.session_state._source_auto and hourly_data:
    jma_ok = (_jma_has_data_for_date(hourly_data, target_date.strftime("%Y-%m-%d")) or
              _jma_has_data_for_date(hourly_data, next_date.strftime("%Y-%m-%d")))
    if jma_ok and st.session_state.weather_source != "JMA":
        # JMA có data → switch về JMA
        st.session_state.weather_source = "JMA"
        st.rerun()
    elif not jma_ok and st.session_state.weather_source == "JMA":
        # JMA không có data → switch sang GFS
        st.session_state.weather_source = "US (GFS)"
        st.rerun()

# Sau auto-switch, cập nhật lại flags theo source hiện tại
prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Tổng hợp (Best)")
use_ecmwf  = (st.session_state.weather_source == "EU (ECMWF)")

# UTC offset của location hiện tại (tính bằng giây) — dùng cho moon altitude
loc_utc_offset_h = _loc_utc_offset / 3600.0  # đổi sang giờ, ví dụ JST=+9, CST=-6

desired_slots = [
    (target_date.year, target_date.month, target_date.day, 18, "18:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 19, "19:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 20, "20:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 21, "21:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 22, "22:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 23, "23:00", target_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 0,  "00:00", next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 1,  "01:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 2,  "02:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 3,  "03:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 4,  "04:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 5,  "05:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 6,  "06:00",    next_date.strftime("%Y-%m-%d")),
]

weather_table_data = []
hours_labels = []
moon_altitudes = []
sun_altitudes  = []
current_cloud_debug = {"low": 0, "mid": 0, "high": 0, "total": 0}
sources_used = set()

times_list = hourly_data.get("time", []) if hourly_data else []

for yr, mo, dy, hr_local, label, date_prefix in desired_slots:
    hours_labels.append(label)
    moon_alt = calculate_exact_moon_altitude_ephem(st.session_state.lat, st.session_state.lon, yr, mo, dy, hr_local, loc_utc_offset_h)
    moon_altitudes.append(moon_alt)
    sun_alt  = calculate_exact_sun_altitude_ephem(st.session_state.lat, st.session_state.lon, yr, mo, dy, hr_local, loc_utc_offset_h)
    sun_altitudes.append(sun_alt)

    if not times_list:
        continue

    target_ts = f"{date_prefix}T{hr_local:02d}:00"
    idx = next((i for i, t in enumerate(times_list) if t.startswith(target_ts)), -1)
    if idx == -1:
        continue

    if use_blend:
        avg_cloud, src1 = get_val_blended(hourly_data, "cloud_cover",          idx, st.session_state.day_offset)
        low_c,     _    = get_val_blended(hourly_data, "cloud_cover_low",       idx, st.session_state.day_offset)
        mid_c,     _    = get_val_blended(hourly_data, "cloud_cover_mid",       idx, st.session_state.day_offset)
        high_c,    _    = get_val_blended(hourly_data, "cloud_cover_high",      idx, st.session_state.day_offset)
        humid,     _    = get_val_blended(hourly_data, "relative_humidity_2m",  idx, st.session_state.day_offset)
        wind_speed,_    = get_val_blended(hourly_data, "wind_speed_10m",        idx, st.session_state.day_offset)
        if src1: sources_used.add(src1)
    elif use_ecmwf:
        # ECMWF IFS025
        avg_cloud  = _get_raw(hourly_data, "cloud_cover",          "_ecmwf_ifs025", idx) or 0.0
        low_c      = _get_raw(hourly_data, "cloud_cover_low",       "_ecmwf_ifs025", idx) or 0.0
        mid_c      = _get_raw(hourly_data, "cloud_cover_mid",       "_ecmwf_ifs025", idx) or 0.0
        high_c     = _get_raw(hourly_data, "cloud_cover_high",      "_ecmwf_ifs025", idx) or 0.0
        humid      = _get_raw(hourly_data, "relative_humidity_2m",  "_ecmwf_ifs025", idx) or 0.0
        wind_speed = _get_raw(hourly_data, "wind_speed_10m",        "_ecmwf_ifs025", idx) or 0.0
        src1 = "ECMWF"
        sources_used.add("ECMWF")
    else:
        avg_cloud, src1 = get_val(hourly_data, "cloud_cover",          idx, prefer_jma)
        low_c,     _    = get_val(hourly_data, "cloud_cover_low",      idx, prefer_jma)
        mid_c,     _    = get_val(hourly_data, "cloud_cover_mid",      idx, prefer_jma)
        high_c,    _    = get_val(hourly_data, "cloud_cover_high",     idx, prefer_jma)
        humid,     _    = get_val(hourly_data, "relative_humidity_2m", idx, prefer_jma)
        wind_speed,_    = get_val(hourly_data, "wind_speed_10m",       idx, prefer_jma)
        if src1: sources_used.add(src1)

    if len(weather_table_data) == 0:
        current_cloud_debug = {"low": int(low_c), "mid": int(mid_c), "high": int(high_c), "total": int(avg_cloud)}

    # Đánh giá CHỈ dựa vào avg_cloud — hoàn toàn tương ứng với % hiển thị trên bảng
    # → không bao giờ mâu thuẫn: cloud cao hơn = sao ít hơn hoặc bằng
    # Ngưỡng:  cloud <= 8%  → 4 sao
    #          cloud <= 25% → 3 sao
    #          cloud <= 50% → 2 sao
    #          cloud <= 80% → 1 sao
    #          cloud >  80% → 0 sao
    score = 100 - avg_cloud  # 1-to-1 với % mây

    if score >= 92:   stars = "⭐⭐⭐⭐"   # cloud <= 8%
    elif score >= 75: stars = "⭐⭐⭐☆"   # cloud <= 25%
    elif score >= 50: stars = "⭐⭐☆☆"   # cloud <= 50%
    elif score >= 20: stars = "⭐☆☆☆"   # cloud <= 80%
    else:             stars = "☆☆☆☆"    # cloud > 80%

    weather_table_data.append({
        "⏰": label,
        "☁️": f"{int(avg_cloud)}%",
        "💧": f"{int(humid)}%",
        "💨": f"{round(wind_speed,1)}m/s",
        "📸": stars
    })

# Label thực tế đã dùng — phân biệt auto-fallback với user chọn tay
if use_blend:
    active_source_label = "🔀 Tổng hợp (JMA+ECMWF+GFS)"
elif "ECMWF" in sources_used:
    active_source_label = "EU (ECMWF IFS025)"
elif "JMA" in sources_used and "GFS" in sources_used:
    active_source_label = "JMA + US (GFS)"
elif "GFS" in sources_used and prefer_jma:
    # User chọn JMA nhưng JMA không có data → auto-fallback
    active_source_label = "US (GFS) [auto-fallback]"
elif "GFS" in sources_used:
    active_source_label = "US (GFS)"
elif "JMA" in sources_used:
    active_source_label = "JMA"
else:
    active_source_label = st.session_state.weather_source

# ── MAP ───────────────────────────────────────────────────────────────────────
# Add top margin so the in-map tile buttons are not obscured by Streamlit toolbar
st.markdown("<div style='margin-top:38px'></div>", unsafe_allow_html=True)

# ── MAP tile switcher — ASCII keys only, no emoji in any string passed to folium ──
_TILE_SAT_URL  = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
_TILE_STR_URL  = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'

if st.session_state.map_tile not in ("satellite", "street"):
    st.session_state.map_tile = "satellite"

# Always start map with satellite base (we switch via JS); center never touched by star-clicks
m = folium.Map(location=st.session_state.map_center,
               tiles=_TILE_SAT_URL, attr='Google Satellite Hybrid')

# Second tile layer for street — added to map so JS can reference it
_street_layer = folium.TileLayer(
    tiles=_TILE_STR_URL, attr='CartoDB Voyager', name='street', overlay=False
)
_street_layer.add_to(m)

folium.TileLayer(
    tiles='https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
    name='OpenRailwayMap', overlay=True, control=True, opacity=0.25, attr='OpenRailwayMap'
).add_to(m)

# Tile toggle via Folium MacroElement — injects a proper Leaflet L.Control
# into the map iframe so it has access to the map object directly.
# All strings are ASCII-only to avoid streamlit-folium JS hash encoding issues.
from folium import MacroElement
from jinja2 import Template

_TILE_CTRL_TEMPLATE = Template("""
{% macro script(this, kwargs) %}
(function(){
  var TileCtrl = L.Control.extend({
    options: { position: 'topright' },
    onAdd: function(map) {
      var div = L.DomUtil.create('div', '');
      div.style.cssText = 'display:flex;gap:4px;background:rgba(15,23,42,0.88);'
        + 'border:1px solid #334155;border-radius:8px;padding:5px 8px;'
        + 'box-shadow:0 2px 8px rgba(0,0,0,0.6);';
      L.DomEvent.disableClickPropagation(div);

      var tiles = {
        satellite: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        street:    'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
      };
      var attrs  = { satellite: 'Google Satellite Hybrid', street: 'CartoDB Voyager' };
      var current = null;
      var btns = {};

      function switchTile(mode) {
        if (current) { map.removeLayer(current); }
        current = L.tileLayer(tiles[mode], { attribution: attrs[mode], maxZoom: 19 });
        current.addTo(map);
        Object.keys(btns).forEach(function(k){
          btns[k].style.background = (k === mode) ? '#3b82f6' : 'transparent';
          btns[k].style.color      = (k === mode) ? '#ffffff' : '#94a3b8';
        });
      }

      ['satellite','street'].forEach(function(mode){
        var btn = L.DomUtil.create('button', '', div);
        btn.textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
        btn.style.cssText = 'border:none;cursor:pointer;border-radius:5px;'
          + 'padding:3px 10px;font-size:12px;font-weight:600;'
          + 'transition:background 0.2s,color 0.2s;background:transparent;color:#94a3b8;';
        btns[mode] = btn;
        L.DomEvent.on(btn, 'click', function(){ switchTile(mode); });
      });

      // Set default after map is ready
      map.whenReady(function(){ switchTile('satellite'); });
      return div;
    }
  });
  new TileCtrl().addTo({{ this._parent.get_name() }});
})();
{% endmacro %}
""")

class _TileControl(MacroElement):
    def __init__(self):
        super().__init__()
        self._name = '_TileControl'
        self._template = _TILE_CTRL_TEMPLATE

_TileControl().add_to(m)

for loc_name, loc_coords in LOCATION_DATABASE.items():
    is_sel = abs(loc_coords[0]-st.session_state.lat)<0.001 and abs(loc_coords[1]-st.session_state.lon)<0.001
    folium.Marker(
        loc_coords,
        icon=folium.DivIcon(
            html=f'<div style="font-size:{"22px" if is_sel else "16px"};color:{"#FFD700" if is_sel else "#FFA500"};'
                 f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{"drop-shadow(0 0 6px gold)" if is_sel else "none"};'
                 f'cursor:pointer;">⭐</div>',
            icon_size=(24,24), icon_anchor=(12,12)),
        tooltip=folium.Tooltip(loc_name, sticky=True)
    ).add_to(m)

is_bookmark = any(abs(c[0]-st.session_state.lat)<0.001 and abs(c[1]-st.session_state.lon)<0.001
                  for c in LOCATION_DATABASE.values())
if not is_bookmark:
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        icon=folium.DivIcon(
            html='<div style="font-size:28px;line-height:1;filter:drop-shadow(0 0 6px rgba(255,50,50,0.9));cursor:pointer;">📍</div>',
            icon_size=(32,32), icon_anchor=(10,30)),
        tooltip=folium.Tooltip(f"📍 {st.session_state.location_name}", sticky=True)
    ).add_to(m)

# center + zoom truyền trực tiếp vào st_folium để map không nhảy về vị trí cũ khi rerun
map_data = st_folium(m, use_container_width=True, height=600, key="astro_map_v70",
                     center=st.session_state.map_center,
                     zoom=st.session_state.zoom,
                     returned_objects=["last_clicked", "last_object_clicked_tooltip", "zoom", "center"],
)

# ── MAP CLICK HANDLER ─────────────────────────────────────────────────────────
if map_data:
    # Zoom: lưu khi thay đổi, không rerun
    new_zoom = map_data.get("zoom")
    if new_zoom is not None and new_zoom != st.session_state.zoom:
        st.session_state.zoom = new_zoom
    # KHÔNG theo dõi center ở đây — việc lưu center sau mỗi drag gây rerun liên tục
    # map_center chỉ được cập nhật khi user click vào điểm mới trên bản đồ trống

    clicked_tip = map_data.get("last_object_clicked_tooltip")
    lc          = map_data.get("last_clicked")

    # ── Ưu tiên tooltip (click ngôi sao) ────────────────────────────────────
    # Dùng tọa độ làm key dedup thay vì tooltip string — tránh bỏ qua click đầu tiên
    if clicked_tip:
        # Tìm location khớp tooltip
        matched = None
        for bname, bcoords in LOCATION_DATABASE.items():
            if bname in str(clicked_tip):
                matched = (bname, bcoords)
                break
        if matched:
            bname, bcoords = matched
            _tip_key = f"{bcoords[0]:.4f},{bcoords[1]:.4f}"
            if _tip_key != st.session_state._last_tip:
                st.session_state._last_tip = _tip_key
                st.session_state._last_lc  = lc
                if (abs(bcoords[0] - st.session_state.lat) > 0.0001 or
                        abs(bcoords[1] - st.session_state.lon) > 0.0001 or
                        st.session_state.is_custom_point):
                    st.session_state.lat             = bcoords[0]
                    st.session_state.lon             = bcoords[1]
                    st.session_state.location_name   = bname
                    st.session_state.is_custom_point = False
                    st.rerun()

    # ── Free-click vùng trống — bỏ qua nếu lc này đã gắn với tooltip trên ──
    elif lc and lc != st.session_state._last_lc:
        st.session_state._last_lc = lc
        c_lat = round(lc["lat"], 4)
        c_lon = ((round(lc["lng"], 4) + 180) % 360) - 180
        hit = next(((n, c) for n, c in LOCATION_DATABASE.items()
                    if abs(c_lat - c[0]) < 0.03 and abs(c_lon - c[1]) < 0.03), None)
        if hit:
            bname, bcoords = hit
            if (abs(bcoords[0] - st.session_state.lat) > 0.0001 or
                    abs(bcoords[1] - st.session_state.lon) > 0.0001 or
                    st.session_state.is_custom_point):
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.rerun()
        else:
            if abs(c_lat - st.session_state.lat) > 0.0001 or abs(c_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat             = c_lat
                st.session_state.lon             = c_lon
                st.session_state.map_center      = [c_lat, c_lon]
                st.session_state.location_name   = fetch_location_name(c_lat, c_lon)
                st.session_state.is_custom_point = True
                st.rerun()
    else:
        # Không có click — lấy center hiện tại từ map để giữ đúng vị trí pan sau rerun
        # Dùng returned_objects khi cần nhưng không trigger rerun
        _raw_center = map_data.get("center")
        if isinstance(_raw_center, dict) and "lat" in _raw_center and "lng" in _raw_center:
            _nc = [round(_raw_center["lat"], 5), round(_raw_center["lng"], 5)]
            if abs(_nc[0] - st.session_state.map_center[0]) > 0.0001 or abs(_nc[1] - st.session_state.map_center[1]) > 0.0001:
                st.session_state.map_center = _nc

# ── LAYOUT: LEFT PANEL + RIGHT PANEL ─────────────────────────────────────────
st.markdown("""
    <style>
        /* Ép bảng chiếm toàn bộ chiều rộng nhưng cột 2 (Mây) chỉ chiếm 10% */
        [data-testid="stTable"] table { width: 100% !important; table-layout: fixed; }
        [data-testid="stTable"] td:nth-child(2), [data-testid="stTable"] th:nth-child(2) { width: 10% !important; }
        /* Đảm bảo cột 📸 Đánh giá có đủ chỗ hiển thị sao */
        [data-testid="stTable"] td:nth-child(5), [data-testid="stTable"] th:nth-child(5) { width: 35% !important; }
    </style>
""", unsafe_allow_html=True)
col_left, col_right = st.columns([1.1, 2.5])

with col_left:
    # Bortle
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌌 SKY QUALITY</span>
        <div style="font-size:28px;font-weight:bold;color:#38bdf8;margin-top:5px;">Bortle Class {bortle_class}</div>
        <div style="font-size:14px;color:#e2e8f0;margin-top:2px;">SQM: <b>{sqm_val}</b> mag/arcsec²</div>
    </div>""", unsafe_allow_html=True)

    # Moon
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌙 MOON PHASE</span>
        <div style="font-size:28px;font-weight:bold;color:#fbbf24;margin-top:5px;">{moon_pct}%</div>
        <div style="font-size:12px;color:#cbd5e1;margin-top:4px;font-style:italic;">{moon_text}</div>
    </div>""", unsafe_allow_html=True)

    # Location
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#94a3b8;font-size:13px;font-weight:bold;">📍 POSITION & COORDINATE</span>
        <div style="font-size:15px;font-weight:bold;color:#f43f5e;margin-top:4px;margin-bottom:4px;">📍 {st.session_state.location_name}</div>
        <div class="geo-highlight">
            <span style="color:#60a5fa;">LON:</span> {round(st.session_state.lon,4)}<br>
            <span style="color:#34d399;">LAT:</span> {round(st.session_state.lat,4)}
    </div>""", unsafe_allow_html=True)

    # Weather source selectbox + source label
    # Dynamic key theo weather_source → widget re-render đúng khi auto-fallback sang GFS
    source_options = ["JMA", "US (GFS)", "EU (ECMWF)", "🔀 Tổng hợp (Best)"]
    cur_src = st.session_state.weather_source
    if cur_src not in source_options:
        cur_src = "JMA"
    src_key = f"sel_source_{cur_src.replace(' ', '_').replace('(', '').replace(')', '').replace('🔀','')}"
    chosen = st.selectbox("src", source_options,
                          index=source_options.index(cur_src),
                          label_visibility="collapsed", key=src_key)
    if chosen != st.session_state.weather_source:
        st.session_state.weather_source = chosen
        st.session_state._source_auto = False  # user chọn tay → không auto-switch nữa
        st.rerun()

    # Random Overlap expander — left panel, below source selector
    with st.expander("🔬 Random Overlap Assumption"):
        st.markdown("Thuật toán xác suất khoảng trống hình học:")
        st.latex(r"P_{clear} = (1-C_{low})(1-C_{mid})(1-C_{high})")
        _l,_m_c,_h = current_cloud_debug["low"]/100, current_cloud_debug["mid"]/100, current_cloud_debug["high"]/100
        _cs = (1-_l)*(1-_m_c)*(1-_h)
        st.caption(f"18:00 — Low={current_cloud_debug['low']}% Mid={current_cloud_debug['mid']}% High={current_cloud_debug['high']}% → clear {_cs*100:.1f}% → cloud **{current_cloud_debug['total']}%**")


with col_right:
    # Nav controls row
    nav1, nav2, nav3, nav4 = st.columns([0.55, 1.1, 2.2, 0.65])
    with nav1:
        if st.button("⬅️ Đêm trước", use_container_width=True, key="btn_prev"):
            if st.session_state.day_offset > 0:
                st.session_state.day_offset -= 1
                st.rerun()
    with nav2:
        # Dùng dynamic key theo day_offset → Streamlit tạo widget mới mỗi khi offset thay đổi
        # → không bao giờ hiển thị ngày cũ bị cache
        sel_label = st.selectbox("ngay", date_options, index=st.session_state.day_offset,
                                 label_visibility="collapsed",
                                 key=f"sel_date_{st.session_state.day_offset}")
        new_off = date_options.index(sel_label)
        if new_off != st.session_state.day_offset:
            st.session_state.day_offset = new_off
            st.rerun()
    with nav3:
        loc_opts = list(LOCATION_DATABASE.keys())
        if st.session_state.is_custom_point:
            disp_opts = [f"📍 {st.session_state.location_name}"] + loc_opts
            def_idx = 0
        else:
            disp_opts = loc_opts
            def_idx = loc_opts.index(st.session_state.location_name) if st.session_state.location_name in loc_opts else 0
        # Dùng dynamic key theo location_name → widget luôn sync với session state
        loc_key = f"sel_loc_{st.session_state.location_name.replace(' ', '_')[:30]}"
        sel_loc = st.selectbox("loc", disp_opts, index=def_idx,
                               label_visibility="collapsed", key=loc_key)
        if sel_loc in LOCATION_DATABASE:
            nlat, nlon = LOCATION_DATABASE[sel_loc]
            if abs(nlat-st.session_state.lat)>0.001 or abs(nlon-st.session_state.lon)>0.001 or st.session_state.is_custom_point:
                st.session_state.lat, st.session_state.lon = nlat, nlon
                # Do NOT update map_center — keep current view
                st.session_state.location_name = sel_loc
                st.session_state.is_custom_point = False
                st.rerun()
    with nav4:
        if st.button("Đêm kế tiếp ➡️", use_container_width=True, key="btn_next"):
            if st.session_state.day_offset < 6:
                st.session_state.day_offset += 1
                st.rerun()

    # Table — custom styled HTML card
    if weather_table_data:
        # Hiện badge nếu đang dùng fallback endpoint
        if _ep_label == "no_jma":
            st.markdown('<div style="background:#422006;border:1px solid #f97316;border-radius:8px;'
                        'padding:6px 14px;margin-bottom:8px;font-size:13px;color:#fed7aa;">'
                        '⚠️ JMA MSM server lỗi — đang dùng <b>ECMWF + GFS</b> thay thế</div>',
                        unsafe_allow_html=True)
        elif _ep_label == "gfs_only":
            st.markdown('<div style="background:#422006;border:1px solid #f97316;border-radius:8px;'
                        'padding:6px 14px;margin-bottom:8px;font-size:13px;color:#fed7aa;">'
                        '⚠️ JMA/ECMWF server lỗi — đang dùng <b>GFS only</b> thay thế</div>',
                        unsafe_allow_html=True)
        def _cloud_bar(pct_str):
            pct = int(pct_str.replace('%',''))
            if pct <= 25:   col = '#22c55e'
            elif pct <= 50: col = '#eab308'
            elif pct <= 75: col = '#f97316'
            else:           col = '#ef4444'
            return (f'<div style="display:flex;align-items:center;gap:5px;max-width:110px;">'
                    f'<div style="width:60px;flex-shrink:0;background:#1e293b;border-radius:4px;height:6px;overflow:hidden;">'
                    f'<div style="width:{pct}%;height:100%;background:{col};border-radius:4px;"></div></div>'
                    f'<span style="min-width:30px;text-align:right;color:{col};font-weight:600;font-size:13px;">{pct_str}</span></div>')

        def _wind_icon(ws_str):
            ws = float(ws_str.replace('m/s',''))
            if ws < 2:   icon,col = '','#94a3b8'
            elif ws < 5: icon,col = '','#60a5fa'
            else:        icon,col = '','#f97316'
            return f'<span style="color:{col}">{icon} {ws_str}</span>'

        rows_html = ''
        for i, row in enumerate(weather_table_data):
            bg = 'rgba(255,255,255,0.03)' if i % 2 == 0 else 'transparent'
            time_lbl = row['⏰']
            cloud_cell = _cloud_bar(row['☁️'])
            humid_val  = row['💧']
            wind_cell  = _wind_icon(row['💨'])
            stars      = row['📸']
            rows_html += (
                f'<tr style="background:{bg};border-bottom:1px solid #1e293b;">'
                f'<td style="padding:8px 12px;font-weight:600;color:#e2e8f0;white-space:nowrap;">{time_lbl}</td>'
                f'<td style="padding:8px 12px;width:140px;max-width:140px;">{cloud_cell}</td>'
                f'<td style="padding:8px 12px;color:#93c5fd;">{humid_val}</td>'
                f'<td style="padding:8px 12px;">{wind_cell}</td>'
                f'<td style="padding:8px 12px;font-size:16px;letter-spacing:2px;">{stars}</td>'
                f'</tr>'
            )

        table_html = f"""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;overflow:hidden;margin-bottom:8px;">
  <table style="width:100%;border-collapse:collapse;font-size:14px;font-family:'Segoe UI',sans-serif;">
    <thead>
      <tr style="background:#1e293b;border-bottom:2px solid #334155;">
        <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-weight:700;">⏰</th>
        <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-weight:700;width:140px;min-width:140px;max-width:140px;">☁️</th>
        <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-weight:700;">💧</th>
        <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-weight:700;">💨</th>
        <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-weight:700;">📸</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:#1e293b;border:1px solid #ef4444;border-radius:12px;padding:20px 24px;margin-top:8px;">
    <div style="font-size:18px;font-weight:700;color:#ef4444;margin-bottom:8px;">
        ⚠️ Open-Meteo API tạm thời không phản hồi
    </div>
    <div style="color:#cbd5e1;font-size:14px;line-height:1.7;">
        Server <code style="color:#fbbf24;">api.open-meteo.com</code> đang trả lỗi <b>502 Bad Gateway</b>
        — đây là sự cố từ phía nhà cung cấp, không phải lỗi của app.<br><br>
        <span style="color:#94a3b8;">Thường tự khỏi sau 5–30 phút. Bấm <b>Thử lại</b> để xoá cache và fetch lại.</span>
    </div>
</div>""", unsafe_allow_html=True)
        if st.button("🔄 Thử lại", key="btn_retry_weather"):
            st.cache_data.clear()
            st.rerun()

# ── MOON + SUN ALTITUDE CHART ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 MOON & SUN ALTITUDE")

# Build combined dataframe
_chart_rows = []
for _lbl, _m, _s in zip(hours_labels, moon_altitudes, sun_altitudes):
    _chart_rows.append({"Khung Giờ": _lbl, "Altitude (°)": _m,  "Body": "🌙 Moon"})
    _chart_rows.append({"Khung Giờ": _lbl, "Altitude (°)": _s,  "Body": "☀️ Sun"})
chart_df = pd.DataFrame(_chart_rows)

# Moon: filled area (gold), Sun: line only (cyan-blue)
_moon_df = chart_df[chart_df["Body"] == "🌙 Moon"]
_sun_df  = chart_df[chart_df["Body"] == "☀️ Sun"]

_base_x = alt.X('Khung Giờ:N', sort=hours_labels,
                 title="Time 18:00 ~ 06:00")
_base_y = alt.Y('Altitude (°):Q',
                scale=alt.Scale(zero=True),
                title="Altitude (°)")

_moon_area = alt.Chart(_moon_df).mark_area(
    line={'color': '#fbbf24', 'size': 2.5},
    color=alt.Gradient(gradient='linear',
        stops=[alt.GradientStop(color='rgba(251,191,36,0.55)', offset=0),
               alt.GradientStop(color='rgba(30,41,59,0.0)',    offset=1)],
        x1=1, y1=1, x2=1, y2=0),
).encode(x=_base_x, y=_base_y,
         tooltip=[alt.Tooltip('Khung Giờ:N', title='Time'),
                  alt.Tooltip('Altitude (°):Q', title='Moon Alt')])

_sun_line = alt.Chart(_sun_df).mark_line(
    color='#38bdf8', size=2.5, strokeDash=[6, 3]
).encode(x=_base_x, y=_base_y,
         tooltip=[alt.Tooltip('Khung Giờ:N', title='Time'),
                  alt.Tooltip('Altitude (°):Q', title='Sun Alt')])

# Horizon zero rule
_horizon = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
    color='#475569', strokeDash=[4, 4], size=1
).encode(y='y:Q')

moon_chart = (_moon_area + _sun_line + _horizon).properties(height=480).resolve_scale(y='shared')
st.altair_chart(moon_chart, use_container_width=True)

# Legend note
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#94a3b8;margin-top:-8px;'>"
    "<span style='color:#fbbf24;'>▬</span> Moon &nbsp;&nbsp;"
    "<span style='color:#38bdf8;'>╌╌</span> Sun &nbsp;&nbsp;"
    "Values below 0° = below horizon</div>",
    unsafe_allow_html=True
)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer-copyright">© Copyright: insta: fcbmkw</div>', unsafe_allow_html=True)