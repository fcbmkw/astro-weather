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
    "1. Jogashima 馬の背, Kanagawa": [35.1313, 139.6179],
    "2. Tateyama ゴルフ場, Chiba": [34.9517, 139.8103],
    "3. Minamiboso 駐車場, Chiba": [34.9071, 139.8611],
    "4. Onjuku 大波月海岸, Chiba": [35.1795, 140.3729],
    "5. Isumi 雀島, Chiba": [35.3196, 140.4091],
    "6. Manazuru 真鶴岬, Kanagawa": [35.1408, 139.1609],
    "7. Shimoda 灯台, Shizuoka": [34.6588, 138.9868],
    "8. Cape Aiai 愛の鐘, Shizuoka": [34.6073, 138.8284],
    "9. Matsuzaki 千貫門ビーチ, Shizuoka": [34.7213, 138.7431],
    "10. Okuoikojo 奥大井湖上駅展望台, Shizuoka": [35.1704, 138.1811],
    "11. Asagiri Arena Parking, Shizuoka": [35.3832, 138.5836],
    "12. Shoji-ko, Yamanashi": [35.4912, 138.6049],
    "13. Hanamomo-no-sato, Nagano": [35.4457, 137.6617],
    "14. Ontake 御嶽山, Nagano": [35.8989, 137.4887],
    "15. Kamikochi 上高地, Nagano": [36.2502, 137.6392],
    "16. Enzan-so 燕山荘/イルカ岩, Nagano": [36.3991, 137.7151],
    "17. Utsukushihara 美ヶ原, Nagano": [36.2274, 138.1296],
    "18. JAXA宇宙アンテナ, Nagano": [36.1408, 138.3537],
    "19. カラマツの丘 Tsumagoi, Gunma": [36.4773, 138.4646],
    "20. Yugama/Shibutoge 渋峠, Gunma": [36.6534, 138.5274],
    "21. Sakura 上発知のシダレザクラ, Gunma": [36.7325, 139.0601],
    "22. Oku-Nikko 湯ノ湖畔, Tochigi": [36.8036, 139.4236],
    "23. Hoshinomura 天地人橋, Fukushima": [37.3427, 140.6756],
    "24. Azuma-kofuji 浄土平, Fukushima": [37.7230, 140.2551],
    "25. Okama 御釜, Sendai, Miyagi": [38.1361, 140.4468],
    "26. Higashinamekawa 東滑川海浜緑地, Ibaraki": [36.6144, 140.6802],
    "27. Okutama 奥多摩湖, Tokyo": [35.7920, 139.0475]
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
    """Estimate Bortle class and SQM (mag/arcsec²) from coordinates.

    Methodology:
    ─────────────────────────────────────────────────
    Priority 1 — Per-location lookup table: values read directly from
      lightpollutionmap.info (VIIRS 2023 / Sky Brightness layer).
      If coordinates match within 5 km, use that value directly.

    Priority 2 — Geographic zone overrides (mountain/island/coastal zones
      calibrated from lightpollutionmap.info heatmap screenshots covering
      all of Japan from Hokkaido to Kyushu).

    Priority 3 — Weighted multi-city distance heuristic with per-city
      Bortle/SQM curves calibrated against ground-truth samples.

    Calibration sources (v5.17):
      · lightpollutionmap.info popup samples (page 15 of Japan_LPM.pdf):
          SQM 17.71 @ 35.69,139.71 (Tokyo core, Bortle 8-9)
          SQM 18.20 @ 35.54,139.69 (Kawasaki, Bortle 8-9)
          SQM 19.15 @ 35.27,139.67 (Yokohama suburb, Bortle 6)
          SQM 20.43 @ 36.23,137.96 (Nagano highlands elev 588m, Bortle 5)
          SQM 20.63 @ 35.13,139.61 (Boso coastal, Bortle 4)
          SQM 20.86 @ 35.14,139.19 (Sagami Bay coast, Bortle 4)
          SQM 21.62 @ 34.65,138.98 (Izu Peninsula, Bortle 4)
          SQM 21.62 @ 35.45,137.64 (Nagano elev 1172m, Bortle 4)
          SQM 21.77 @ 34.62,138.97 (Shimoda area, Bortle 3)
          SQM 21.94 @ 34.08,139.56 (Oshima Island, Bortle 2)
      · Heatmap visual analysis: pages 1-14 of Japan_LPM.pdf
          Full Japan overview + regional zoom (Kyushu, Kansai, Chubu,
          Kanto, Tohoku, Hokkaido) with coordinate overlays.

    Bortle ↔ SQM reference (Wikipedia / Bortle 2001 / Sky & Telescope):
      Class 1:   21.76–22.0    Class 2:   21.6–21.75
      Class 3:   21.3–21.6     Class 4:   20.8–21.3
      Class 4.5: 20.3–20.8     Class 5:   19.25–20.3
      Class 6:   18.5–19.25    Class 7:   18.0–18.5
      Class 8/9: < 18.0
    Source: lightpollutionmap.info · Falchi et al. 2016 · VIIRS 2023
    """
    # ── Lookup table: verified on lightpollutionmap.info VIIRS 2023 layer ───────
    # Color → Bortle mapping (lightpollutionmap.info standard palette):
    #   white/pink core → 9 | red → 8-9 | orange → 7-8 | yellow → 6-7
    #   yellow-green → 5-6 | light green → 4-5 | green → 4
    #   dark green → 3 | teal/blue-green → 2-3 | light blue → 2 | grey → 1
    _LOC_BORTLE = {
        # ── Kanagawa ──────────────────────────────────────────────────────────
        (35.1313, 139.6179): (4.5, 21.20),   #  1 Jogashima          green     → Bortle 4 (20.8–21.3)
        (35.1408, 139.1609): (4.5, 20.80),   #  6 Manazuru           light green (near Odawara) → 4.5 edge / 5
        (35.5400, 139.7030): (9, 17.80),   # Kawasaki city core    — lightpollutionmap SQM ≈17.8, Bortle 9
        (35.4437, 139.6380): (9, 17.90),   # Yokohama core         — very bright urban core
        # ── Chiba / Boso ──────────────────────────────────────────────────────
        (34.9517, 139.8103): (4, 21.20),   #  2 Tateyama           green
        (34.9071, 139.8611): (4, 21.20),   #  3 Minamiboso         green
        (35.1795, 140.3729): (4, 21.25),   #  4 Onjuku             green
        (35.3196, 140.4091): (4, 21.25),   #  5 Isumi              green
        # ── Shizuoka / Izu ────────────────────────────────────────────────────
        (34.6588, 138.9868): (3.5, 21.77),   #  7 Shimoda — calibrated from sample SQM 21.77
        (34.6073, 138.8284): (3, 21.75),   #  8 Cape Aiai          dark green
        (34.7213, 138.7431): (3, 21.75),   #  9 Matsuzaki          dark green
        # ── Shizuoka inland ───────────────────────────────────────────────────
        (35.1704, 138.1811): (3, 21.75),   # 10 Okuoikojo          dark green
        (35.3832, 138.5836): (3, 21.75),   # 11 Asagiri Arena      dark green
        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.4912, 138.6049): (4, 21.70),   # 12 Shoji-ko           dark green (slight glow from Kofu)
        # ── Nagano ────────────────────────────────────────────────────────────
        (35.4457, 137.6617): (4, 21.62),   # 13 Hanamomo-no-sato   calibrated: SQM 21.62 → Class 3 (21.3–21.6 border)
        (35.8989, 137.4887): (3, 22.00),   # 14 Ontake             light blue (Japan Alps summit)
        (36.2502, 137.6392): (3, 22.00),   # 15 Kamikochi          light blue (deep Alps)
        (36.3991, 137.7151): (3, 21.95),   # 16 Enzan-so           light blue
        (36.2274, 138.1296): (3, 21.75),   # 17 Utsukushihara      dark green
        (36.1408, 138.3537): (3, 21.80),   # 18 JAXA               dark green
        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.4773, 138.4646): (4, 21.75),   # 19 Tsumagoi           dark green
        (36.6534, 138.5274): (3, 21.80),   # 20 Yugama/Shibutoge   dark green
        (36.7325, 139.0601): (4, 21.30),   # 21 Sakura 上発知      green (Numata basin glow)
        # ── Tochigi ───────────────────────────────────────────────────────────
        (36.8036, 139.4236): (4, 21.75),   # 22 Oku-Nikko          dark green
        # ── Fukushima ─────────────────────────────────────────────────────────
        (37.3427, 140.6756): (3, 21.75),   # 23 Hoshinomura        dark green
        (37.7230, 140.2551): (3, 21.80),   # 24 Azuma-kofuji       dark green (volcanic plateau)
        # ── Miyagi ────────────────────────────────────────────────────────────
        (38.1361, 140.4468): (3, 21.75),   # 25 Okama 御釜         dark green
        # ── Ibaraki coast ─────────────────────────────────────────────────────
        (36.6144, 140.6802): (5, 20.80),   # 26 Higashinamekawa    light green (coastal urban) → 4.5/5
        # ── Tokyo ─────────────────────────────────────────────────────────────
        (35.7920, 139.0475): (5, 20.70),   # 27 Okutama            light green (Tokyo glow) → 4.5/5
    }

    def _km(la1, lo1, la2, lo2):
        dlat = (la1 - la2) * 111.0
        dlon = (lo1 - lo2) * 111.0 * math.cos(math.radians((la1 + la2) / 2))
        return math.sqrt(dlat**2 + dlon**2)

    # Priority 1: exact location match within 5 km
    for (plat, plon), (bc, sq) in _LOC_BORTLE.items():
        if _km(lat, lon, plat, plon) < 5.0:
            return bc, sq

    # ── Priority 2: Geographic zone overrides ────────────────────────────────
    # Calibrated from heatmap analysis of Japan_LPM.pdf pages 1-14.
    # Zones listed from darkest (highest priority) to brightest.

    # Japan Alps core — Bortle 1-2 (grey/light-blue on heatmap)
    # Covers: Kamikochi, Hotaka, Yari, Tateyama, Hakuba deep valleys
    if 36.0 < lat < 36.8 and 137.3 < lon < 137.9:
        return 2, 21.95

    # Northern Japan Alps / Ontake / Norikura area
    if 35.7 < lat < 36.2 and 137.2 < lon < 137.7:
        return 2, 22.00

    # Southern Alps (Minami Alps / Akaishi) — Bortle 2-3
    if 35.3 < lat < 35.8 and 137.5 < lon < 138.1:
        return 2, 22.00

    # Shizuoka deep mountain interior (Okuoi / Ikawa)
    if 35.0 < lat < 35.4 and 137.8 < lon < 138.3:
        return 3, 21.80

    # Asagiri Plateau / Fuji Highland area
    if 35.28 < lat < 35.48 and 138.45 < lon < 138.70:
        return 3, 21.75

    # Izu Peninsula tip (south of Shimoda) — dark green
    if lat < 34.72 and 138.70 < lon < 139.10:
        return 3, 21.80

    # Izu Oshima / Izu Islands — Bortle 2 (nearly pitch black, calibrated SQM 21.94)
    if 33.8 < lat < 34.8 and 139.3 < lon < 139.8 and _km(lat, lon, 34.08, 139.56) < 20:
        return 2, 21.94

    # Ogasawara / Bonin Islands — Bortle 1 (extreme remote)
    if lat < 28.0 and 141.0 < lon < 143.0:
        return 1, 22.20

    # Nikko highlands / Oku-Nikko (Yunoko, Senjogahara)
    if 36.70 < lat < 36.90 and 139.35 < lon < 139.60:
        return 3, 21.75

    # Oku-Chichibu mountains (Gunma/Saitama/Yamanashi border)
    if 35.8 < lat < 36.2 and 138.6 < lon < 139.2 and _km(lat, lon, 35.97, 138.87) > 20:
        return 3, 21.75

    # Noto Peninsula tip — Bortle 3 (light blue on heatmap)
    if 37.2 < lat < 37.6 and 136.8 < lon < 137.4:
        return 3, 21.80

    # Tohoku highlands / Ou Mountains core
    if 37.5 < lat < 40.5 and 140.2 < lon < 141.0 and _km(lat, lon, 38.27, 140.87) > 30:
        return 3, 21.75

    # Azuma/Adatara volcanic plateau (Fukushima)
    if 37.60 < lat < 37.90 and 140.1 < lon < 140.4:
        return 3, 21.80

    # Sanriku coast (Iwate/Miyagi) — relatively dark coastal
    if 38.5 < lat < 40.5 and 141.3 < lon < 142.0:
        return 4, 21.30

    # Akita / Yamagata highlands — Bortle 3-4
    if 38.5 < lat < 40.5 and 140.0 < lon < 140.8 and _km(lat, lon, 39.72, 140.10) > 20:
        return 3, 21.75

    # Hokkaido — Daisetsuzan / Shiretoko core (nearly pitch black)
    if 43.3 < lat < 44.0 and 142.5 < lon < 144.5:
        return 2, 22.00

    # Hokkaido interior mountains (away from Sapporo/Asahikawa)
    if 42.5 < lat < 45.5 and 141.5 < lon < 144.5 and _km(lat, lon, 43.06, 141.35) > 40 and _km(lat, lon, 43.77, 142.37) > 25:
        return 3, 21.75

    # Eastern Hokkaido (Kushiro/Abashiri area) — Bortle 4
    if 43.0 < lat < 44.5 and 144.0 < lon < 145.5:
        return 4, 21.30

    # Kyushu highlands (Aso / Kuju / Kirishima) — Bortle 3
    if 32.5 < lat < 33.2 and 130.8 < lon < 131.4:
        return 3, 21.75

    # Miyazaki coast / Nichinan — Bortle 4 (light green on heatmap)
    if 31.3 < lat < 32.2 and 131.2 < lon < 131.8:
        return 4, 21.20

    # Kagoshima south (Satsuma Peninsula tip) — Bortle 4
    if lat < 31.5 and 130.4 < lon < 130.8:
        return 4, 21.20

    # Amami / Okinawa islands — Bortle 3-4 (remote, minimal pollution)
    if lat < 28.5 and 127.0 < lon < 131.0:
        return 3, 21.80

    # Shikoku mountains (Kochi interior) — Bortle 3
    if 33.4 < lat < 33.9 and 133.0 < lon < 133.8:
        return 3, 21.75

    # Sea of Japan coastal Tohoku / Akita — Bortle 4
    if 38.0 < lat < 40.5 and 139.0 < lon < 140.2 and _km(lat, lon, 39.72, 140.10) > 15:
        return 4, 21.30

    # ── Priority 3: Min-distance heuristic (approach from v5.10, extended to all Japan)
    # Concept: inspired by v5.10's simple min-distance threshold approach.
    # Each city has a center SQM (calibrated from lightpollutionmap.info).
    # SQM recovers with distance via a universal delta table.
    # Final SQM = min across all cities (most polluted city wins).
    # Validated against 10 ground-truth samples from Japan_LPM.pdf — all within ±1 Bortle class.
    #
    # Delta table (km from city center → SQM added to city's center_sqm):
    #   ≤4km:+0.0  ≤8km:+0.3  ≤15km:+0.7  ≤25km:+1.2  ≤40km:+1.8
    #   ≤65km:+2.5  ≤100km:+3.2  ≤150km:+3.7  >150km:+4.0
    # Calibration: Tokyo(0km)=17.50 → Machida(27km)=18.81 [delta≈1.3, matches ≤25 band]
    #              Yokohama(0km)=17.80 → Yokosuka(35km)=19.15 [delta≈1.35, matches ≤40 band]
    _DELTA_BANDS = [
        (4,   0.0),
        (8,   0.3),
        (15,  0.7),
        (25,  1.2),
        (40,  1.8),
        (65,  2.5),
        (100, 3.2),
        (150, 3.7),
    ]
    def _get_delta(d):
        for _thresh, _delta in _DELTA_BANDS:
            if d <= _thresh:
                return _delta
        return 4.0  # > 150km → negligible

    # (lat, lon, name, center_sqm) — center_sqm calibrated from lightpollutionmap.info
    _CITIES = [
        # ── Kanto mega-region ──────────────────────────────────────────────────
        (35.6895, 139.6917, "Tokyo",       17.40),
        (35.4437, 139.6380, "Yokohama",    17.60),
        (35.5400, 139.7030, "Kawasaki",    17.60),  # calibrated SQM 18.20 @ 10km
        (35.8616, 139.6455, "Saitama",     18.20),
        (35.6074, 140.1063, "Chiba",       18.20),        # Kanto suburban dense ring — critical for Setagaya/Noborito/Machida accuracy
        (35.6430, 139.6529, "Setagaya",    17.90),  # inner Tokyo ward, between Tokyo & Kawasaki
        (35.5503, 139.5491, "Tama-Plaza",  18.50),  # Kawasaki Aoba-ku
        (35.5480, 139.4454, "Machida",     18.60),  # calibrated from PDF SQM 18.81 nearby
        (35.6993, 139.4107, "Tachikawa",   18.60),
        (35.6598, 139.3188, "Hachioji",    18.60),
        (35.4385, 139.3653, "Atsugi",      18.60),
        (35.9264, 139.4841, "Kawagoe",     19.10),
        (35.2815, 139.6695, "Yokosuka",    19.10),
        (35.2700, 139.6700, "Yokohama-S",  18.25),  # calibrated SQM 19.15 (Totsuka/Yokosuka)
        (35.6562, 138.5692, "Kofu",        19.80),
        (35.2682, 139.1634, "Odawara",     19.75),
        (36.3278, 139.0110, "Takasaki",    19.50),
        # ── Kansai mega-region ─────────────────────────────────────────────────
        (34.6937, 135.5023, "Osaka",       17.60),
        (34.6843, 135.8068, "Nara",        19.20),
        (34.6901, 135.1956, "Kobe",        18.50),
        (35.0116, 135.7681, "Kyoto",       18.70),
        (35.1815, 136.9066, "Nagoya",      17.80),
        # ── Other major cities ─────────────────────────────────────────────────
        (34.7650, 137.3923, "Toyohashi",   19.40),
        (35.4128, 136.7586, "Gifu",        19.30),        
        (43.0621, 141.3544, "Sapporo",     18.50),
        (33.5904, 130.4017, "Fukuoka",     18.50),
        (33.8834, 130.8751, "Kitakyushu",  18.80),
        (38.2682, 140.8694, "Sendai",      19.20),
        (34.6567, 133.9207, "Okayama",     19.20),
        (34.4875, 133.3742, "Fukuyama",    19.70),
        (34.3853, 132.4553, "Hiroshima",   19.20),
        (34.8152, 134.6812, "Himeji",      19.30),
        (34.3380, 134.0495, "Takamatsu",   19.60),
        (34.6551, 133.9195, "Okayama",     19.80),
        (43.7706, 142.3650, "Asahikawa",   20.30),
        (37.9161, 139.0364, "Niigata",     19.50),
        (36.5613, 136.6562, "Kanazawa",    19.40),
        (36.6953, 137.2113, "Toyama",      19.50),
        (36.6485, 138.1949, "Nagano",      20.05),
        (36.0627, 136.2177, "Fukui",       19.65),
        (34.9769, 138.3831, "Shizuoka",    19.40),
        (34.7108, 137.7262, "Hamamatsu",   19.10),
        (36.2380, 137.9720, "Matsumoto",   20.43),  # calibrated SQM 20.43
        (32.7898, 130.7417, "Kumamoto",    19.50),
        (31.5966, 130.5571, "Kagoshima",   19.50),
        (33.8395, 132.7657, "Matsuyama",   20.10),
        (33.2375, 131.6101, "Oita",        19.40),
        (34.0657, 134.5590, "Tokushima",   20.30),
        (34.3400, 134.0434, "Takamatsu",   20.30),
        (33.5597, 133.5311, "Kochi-c",     20.30),
        (36.3898, 139.0634, "Maebashi",    19.50),
        (36.5550, 139.8829, "Utsunomiya",  19.50),
        (37.3983, 140.3870, "Koriyama",    19.50),
        (37.7500, 140.4677, "Fukushima-c", 20.10),
        (39.7186, 140.1023, "Akita-c",     20.10),
        (40.8244, 140.7400, "Aomori-c",    20.30),
        (26.2124, 127.6792, "Naha",        19.50),
    ]

    sqm_est = 22.30  # start pristine, find most polluted influence
    for _clat, _clon, _cname, _csqm in _CITIES:
        _d = _km(lat, lon, _clat, _clon)
        _sqm_here = _csqm + _get_delta(_d)
        sqm_est = min(sqm_est, _sqm_here)

    sqm_est = max(17.5, min(22.3, round(sqm_est, 2)))

    # Convert SQM → Bortle class
    # Thresholds theo Wikipedia / Bortle 2001 / Sky & Telescope:
    #   Class 1:  21.76–22.0   Class 2: 21.6–21.75  Class 3: 21.3–21.6
    #   Class 4:  20.8–21.3    Class 4.5: 20.3–20.8 Class 5: 19.25–20.3
    #   Class 6:  18.5–19.25   Class 7: 18.0–18.5
    #   Class 8+: < 18.0
    if   sqm_est >= 21.76: bc = 1
    elif sqm_est >= 21.60: bc = 2
    elif sqm_est >= 21.30: bc = 3
    elif sqm_est >= 20.30: bc = 4   # gộp 4 và 4.5
    elif sqm_est >= 19.41: bc = 5
    elif sqm_est >= 18.50: bc = 6
    elif sqm_est >= 18.00: bc = 7
    elif sqm_est >= 17.62: bc = 8
    else:                  bc = 9

    return bc, sqm_est

# ── WEATHER FETCH ─────────────────────────────────────────────────────────────
# Các endpoint fallback theo thứ tự ưu tiên:
#   1. Primary: tất cả 3 models (JMA + ECMWF + GFS) — đầy đủ nhất
#   2. Fallback A: chỉ GFS + ECMWF (bỏ JMA) — nhẹ hơn, ít lỗi hơn
#   3. Fallback B: chỉ GFS — luôn hoạt động, không phụ thuộc Japan server
_FIELDS = "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,relative_humidity_2m,wind_speed_10m,temperature_2m,precipitation"
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

# ── Night-start offset ─────────────────────────────────────────────────────────
# A "night" runs 18:00 → 06:00 next day.
# If current JST time is 00:00–17:59 we are still inside last-night's second half
# (00:00–06:00 already passed, 18:00 tonight is the NEXT upcoming block).
# So: if hour < 18, "night 0" = today's evening (18:00 today → 06:00 tomorrow),
#     which means we base target_date on today's date.
# The past-data problem (18:00-23:59 gone after midnight): we fix it by
# skipping slots that are in the past when rendering the table.
_now_jst        = datetime.now(JST)
_night_base_jst = _now_jst  # the calendar day whose 18:00 starts "night 0"
# If current hour < 18 we're in the morning-after; night 0 still means
# *this* coming 18:00 (same calendar day), so no shift needed.
# date_options i=0 → tonight (18:00 of _night_base_jst)
date_options = [
    f"Đêm {(_night_base_jst+timedelta(days=i)).strftime('%d/%m')} → {(_night_base_jst+timedelta(days=i+1)).strftime('%d/%m')}"
    for i in range(7)
]

target_date = (_night_base_jst + timedelta(days=st.session_state.day_offset)).replace(tzinfo=None)
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

# Filter out slots that are already in the past (only for tonight, day_offset=0)
_now_naive = _now_jst.replace(tzinfo=None)
def _slot_is_future(yr, mo, dy, hr):
    # Include the current hour slot (e.g. 20:01 → still show 20:00 row)
    slot_dt = datetime(yr, mo, dy, hr, 0) + timedelta(hours=1)
    return slot_dt > _now_naive

if st.session_state.day_offset == 0:
    desired_slots = [(yr,mo,dy,hr,lbl,dpfx) for yr,mo,dy,hr,lbl,dpfx in desired_slots
                     if _slot_is_future(yr,mo,dy,hr)]

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
        temp_val,  _    = get_val_blended(hourly_data, "temperature_2m",        idx, st.session_state.day_offset)
        precip_val,_    = get_val_blended(hourly_data, "precipitation",         idx, st.session_state.day_offset)
        if src1: sources_used.add(src1)
    elif use_ecmwf:
        # ECMWF IFS025
        avg_cloud  = _get_raw(hourly_data, "cloud_cover",          "_ecmwf_ifs025", idx) or 0.0
        low_c      = _get_raw(hourly_data, "cloud_cover_low",       "_ecmwf_ifs025", idx) or 0.0
        mid_c      = _get_raw(hourly_data, "cloud_cover_mid",       "_ecmwf_ifs025", idx) or 0.0
        high_c     = _get_raw(hourly_data, "cloud_cover_high",      "_ecmwf_ifs025", idx) or 0.0
        humid      = _get_raw(hourly_data, "relative_humidity_2m",  "_ecmwf_ifs025", idx) or 0.0
        wind_speed = _get_raw(hourly_data, "wind_speed_10m",        "_ecmwf_ifs025", idx) or 0.0
        temp_val   = _get_raw(hourly_data, "temperature_2m",        "_ecmwf_ifs025", idx) or 0.0
        precip_val = _get_raw(hourly_data, "precipitation",         "_ecmwf_ifs025", idx) or 0.0
        src1 = "ECMWF"
        sources_used.add("ECMWF")
    else:
        avg_cloud, src1 = get_val(hourly_data, "cloud_cover",          idx, prefer_jma)
        low_c,     _    = get_val(hourly_data, "cloud_cover_low",      idx, prefer_jma)
        mid_c,     _    = get_val(hourly_data, "cloud_cover_mid",      idx, prefer_jma)
        high_c,    _    = get_val(hourly_data, "cloud_cover_high",     idx, prefer_jma)
        humid,     _    = get_val(hourly_data, "relative_humidity_2m", idx, prefer_jma)
        wind_speed,_    = get_val(hourly_data, "wind_speed_10m",       idx, prefer_jma)
        temp_val,  _    = get_val(hourly_data, "temperature_2m",       idx, prefer_jma)
        precip_val,_    = get_val(hourly_data, "precipitation",        idx, prefer_jma)
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
        "📸": stars,
        "_temp": temp_val,
        "_precip": precip_val,
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
               zoom_start=st.session_state.zoom,
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

# Inject CSS to hide all tooltip text on star markers (but keep tooltip firing for click detection)
m.get_root().html.add_child(folium.Element("""
<style>
.star-tip .leaflet-tooltip { 
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: transparent !important;
    font-size: 0 !important; padding: 0 !important;
    pointer-events: none !important;
}
</style>
"""))

for loc_name, loc_coords in LOCATION_DATABASE.items():
    is_sel = abs(loc_coords[0]-st.session_state.lat)<0.001 and abs(loc_coords[1]-st.session_state.lon)<0.001
    folium.Marker(
        loc_coords,
        icon=folium.DivIcon(
            html=f'<div style="font-size:{"22px" if is_sel else "16px"};color:{"#FFD700" if is_sel else "#FFA500"};'
                 f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{"drop-shadow(0 0 6px gold)" if is_sel else "none"};'
                 f'cursor:pointer;">⭐</div>',
            icon_size=(24,24), icon_anchor=(12,12)),
        tooltip=folium.Tooltip(loc_name, sticky=False, class_name="star-tip"),
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

# Key cố định → component không bị recreate khi map_center thay đổi
_map_key = "astro_map_main"
map_data = st_folium(m, use_container_width=True, height=600, key=_map_key,
                     center=st.session_state.map_center,
                     returned_objects=["last_clicked", "last_object_clicked_tooltip", "zoom", "center"],
)

# ── LPM EXTERNAL LINK ─────────────────────────────────────────────────────────
# URL is used inline in the nav row beside the location selectbox
_lpm_url = (f"https://www.lightpollutionmap.info/"
            f"#zoom=10&lat={st.session_state.lat:.4f}&lon={st.session_state.lon:.4f}"
            f"&layers=B0FFFFFFFFFFFFFFFFFFF")

# ── MAP CLICK HANDLER ─────────────────────────────────────────────────────────
if map_data:
    # Zoom: lưu khi thay đổi, không rerun
    new_zoom = map_data.get("zoom")
    if new_zoom is not None and new_zoom != st.session_state.zoom:
        st.session_state.zoom = new_zoom

    # Lưu center thực tế từ map trả về → map_center phản ánh vị trí đang nhìn
    # Quan trọng: phải lưu TRƯỚC khi xử lý click để rerun không làm nhảy map
    _ret_center = map_data.get("center")
    if _ret_center and isinstance(_ret_center, dict):
        _rc = [_ret_center["lat"], _ret_center["lng"]]
        # Chỉ cập nhật nếu khác đáng kể (tránh ghi đè không cần thiết)
        if (abs(_rc[0] - st.session_state.map_center[0]) > 0.001 or
                abs(_rc[1] - st.session_state.map_center[1]) > 0.001):
            st.session_state.map_center = _rc

    clicked_tip = map_data.get("last_object_clicked_tooltip")
    lc          = map_data.get("last_clicked")

    # ── Priority 1: star marker click (via tooltip) ───────────────────────────
    # last_clicked luôn NULL với DivIcon, chỉ dùng tooltip để detect click ngôi sao.
    # _last_tip được reset về None sau mỗi rerun thành công → click lại cùng sao vẫn hoạt động.
    if clicked_tip:
        matched = None
        for bname, bcoords in LOCATION_DATABASE.items():
            if bname in str(clicked_tip):
                matched = (bname, bcoords)
                break
        if matched:
            bname, bcoords = matched
            _tip_key = f"{bcoords[0]:.4f},{bcoords[1]:.4f}"
            if _tip_key != st.session_state._last_tip:
                st.session_state._last_tip       = None   # reset → click lại cùng sao lần sau không bị block
                st.session_state._last_lc        = lc
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                # KHÔNG set map_center = bcoords → key cố định, map không recreate
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.rerun()

    # ── Priority 2: free-click on empty map ──────────────────────────────────
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
                # KHÔNG set map_center = bcoords
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._last_tip       = None
                st.rerun()
        else:
            if abs(c_lat - st.session_state.lat) > 0.0001 or abs(c_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat             = c_lat
                st.session_state.lon             = c_lon
                # KHÔNG set map_center — đã lưu từ _ret_center ở trên
                st.session_state.location_name   = fetch_location_name(c_lat, c_lon)
                st.session_state.is_custom_point = True
                st.session_state._last_tip       = None
                st.rerun()

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
col_left, col_right = st.columns([2.5, 1.1])

with col_right:
    # Bortle
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌌 SKY QUALITY</span>
        <div style="font-size:28px;font-weight:bold;color:#38bdf8;margin-top:5px;">Bortle Class {bortle_class}</div>
        <div style="font-size:14px;color:#e2e8f0;margin-top:2px;">SQM: <b>{sqm_val}</b> mag/arcsec²</div>
        <div style="font-size:11px;color:#64748b;margin-top:6px;border-top:1px solid #334155;padding-top:5px;">
            Estimate · Falchi et al. 2016 (lightpollutionmap.info) ±1 class
        </div>
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

    # 7-Day Forecast Table — replaces Random Overlap Assumption
    def _cloud_status_icon(cloud_pct, precip=0.0):
        """Return weather icon + label based on cloud cover and precipitation."""
        if precip is not None and precip > 2.0:
            if cloud_pct > 70:
                return "\u26c8\ufe0f", "Storm"
            return "\U0001f327\ufe0f", "Rainy"
        if cloud_pct <= 20:
            return "\u2600\ufe0f", "Sunny"
        elif cloud_pct <= 45:
            return "\u26c5", "Partly"
        elif cloud_pct <= 70:
            return "\U0001f325\ufe0f", "Cloudy"
        else:
            return "\u2601\ufe0f", "Overcast"

    # Build 7-day daily summary from hourly_data
    JST_now = datetime.now(JST)
    _7day_rows = []
    for _doff in range(7):
        _d = (JST_now + timedelta(days=_doff)).replace(tzinfo=None)
        _dpfx = _d.strftime("%Y-%m-%d")
        _day_label = _d.strftime("%a %d/%m")

        _temps, _clouds, _precips = [], [], []
        _tlist = hourly_data.get("time", []) if hourly_data else []
        for _i, _t in enumerate(_tlist):
            if _t.startswith(_dpfx):
                _hr = int(_t[11:13])
                for _sfx in ["_jma_msm", "_gfs_seamless", "_ecmwf_ifs025"]:
                    _v = _get_raw(hourly_data, "temperature_2m", _sfx, _i)
                    if _v is not None:
                        _temps.append((_hr, _v))
                        break
                else:
                    _raw_t = hourly_data.get("temperature_2m", [])
                    if _i < len(_raw_t) and _raw_t[_i] is not None:
                        _temps.append((_hr, float(_raw_t[_i])))
                _cv, _ = get_val(hourly_data, "cloud_cover", _i, prefer_jma)
                _clouds.append(_cv)
                for _sfx in ["_gfs_seamless", "_jma_msm", "_ecmwf_ifs025"]:
                    _pv = _get_raw(hourly_data, "precipitation", _sfx, _i)
                    if _pv is not None:
                        _precips.append(_pv)
                        break

        if _temps:
            _noon = min(_temps, key=lambda x: abs(x[0] - 12))
            _temp_noon = round(_noon[1], 1)
            _temp_min  = round(min(v for _, v in _temps), 1)
            _temp_max  = round(max(v for _, v in _temps), 1)
        else:
            _temp_noon = _temp_min = _temp_max = None

        _avg_cloud = round(sum(_clouds) / len(_clouds)) if _clouds else 0
        _total_precip = round(sum(_precips), 1) if _precips else 0.0
        _icon, _status = _cloud_status_icon(_avg_cloud, _total_precip)

        if _temp_max is not None and _temp_max < 3.0 and _total_precip > 0.5:
            _icon, _status = "\u2744\ufe0f", "Snowy"

        _7day_rows.append({
            "day": _day_label,
            "icon": _icon,
            "status": _status,
            "temp_max": _temp_max,
            "temp_min": _temp_min,
            "cloud": _avg_cloud,
        })

    if _7day_rows:
        _rows7 = ""
        for _r in _7day_rows:
            _tmax_str = f"{_r['temp_max']}\u00b0" if _r['temp_max'] is not None else "\u2014"
            _tmin_str = f"{_r['temp_min']}\u00b0" if _r['temp_min'] is not None else "\u2014"
            _cloud_color = '#22c55e' if _r['cloud'] <= 25 else ('#eab308' if _r['cloud'] <= 50 else ('#f97316' if _r['cloud'] <= 75 else '#ef4444'))
            _rows7 += (
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;'
                f'background:rgba(255,255,255,0.04);border-radius:10px;padding:10px 6px;'
                f'border:1px solid #1e293b;flex:1;min-width:0;">'
                f'<div style="font-size:11px;color:#94a3b8;font-weight:600;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis;max-width:100%;text-align:center;">{_r["day"]}</div>'
                f'<div style="font-size:26px;line-height:1.1;">{_r["icon"]}</div>'
                f'<div style="font-size:11px;color:#cbd5e1;font-weight:500;">{_r["status"]}</div>'
                f'<div style="font-size:13px;font-weight:700;color:#f97316;">{_tmax_str}</div>'
                f'<div style="font-size:11px;color:#60a5fa;">{_tmin_str}</div>'
                f'<div style="font-size:10px;color:{_cloud_color};margin-top:2px;">{_r["cloud"]}%</div>'
                f'</div>'
            )
        _forecast_html = (
            '<div style="margin-top:8px;">'
            '<div style="font-size:12px;color:#94a3b8;font-weight:700;margin-bottom:6px;letter-spacing:0.5px;">'
            '\U0001f5d3\ufe0f 7-DAY FORECAST</div>'
            '<div style="display:flex;gap:4px;width:100%;">'
            + _rows7 +
            '</div>'
            '<div style="font-size:10px;color:#475569;margin-top:5px;text-align:right;">'
            '\u2191 High &nbsp;\u2193 Low &nbsp;\u2601 Cloud%</div>'
            '</div>'
        )
        st.markdown(_forecast_html, unsafe_allow_html=True)


with col_left:
    # Inject CSS:
    # 1. Orange styling for date selectbox (nav2)
    # 2. Compact styling for location selectbox (nav3) — smaller font, tighter padding
    st.markdown("""
<style>
/* ── Date selectbox: shrink to fit content ── */
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] > div:first-child {
    background: rgba(154,52,18,0.60) !important;
    border: 1.5px solid rgba(234,88,12,0.75) !important;
    box-shadow: 0 0 8px rgba(234,88,12,0.18) !important;
}
div[data-testid="column"]:nth-child(2) div[data-baseweb="select"] span {
    color: #fb923c !important;
    font-weight: 700 !important;
}
/* ── Location selectbox: compact font ── */
[data-testid="stSelectbox"]:has(select[id*="sel_loc"]) div[data-baseweb="select"] > div:first-child {
    padding-top: 4px !important; padding-bottom: 4px !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_loc"]) span {
    font-size: 12px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
/* ── LPM button styling ── */
.lpm-btn a {
    display:inline-flex;align-items:center;justify-content:center;
    background:rgba(124,58,237,0.20);border:1.5px solid rgba(124,58,237,0.60);
    border-radius:8px;padding:6px 10px;text-decoration:none;
    color:#a78bfa;font-size:13px;font-weight:700;
    height:38px;box-sizing:border-box;white-space:nowrap;
}
.lpm-btn a:hover { background:rgba(124,58,237,0.35); }
</style>""", unsafe_allow_html=True)

    # Nav controls: 1 hàng [← prev] [date] [next →] [location] [LPM]
    nav1, nav2, nav4, nav3, nav_lpm = st.columns([0.12, 0.48, 0.12, 1.50, 0.26])
    with nav1:
        if st.button("⬅️", use_container_width=True, key="btn_prev"):
            if st.session_state.day_offset > 0:
                st.session_state.day_offset -= 1
                st.rerun()
    with nav2:
        sel_label = st.selectbox("ngay", date_options, index=st.session_state.day_offset,
                                 label_visibility="collapsed",
                                 key=f"sel_date_{st.session_state.day_offset}")
        new_off = date_options.index(sel_label)
        if new_off != st.session_state.day_offset:
            st.session_state.day_offset = new_off
            st.rerun()
    with nav4:
        if st.button("➡️", use_container_width=True, key="btn_next"):
            if st.session_state.day_offset < 6:
                st.session_state.day_offset += 1
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
    with nav_lpm:
        st.markdown(
            f'<div class="lpm-btn" style="padding-top:2px;">'
            f'<a href="{_lpm_url}" target="_blank" rel="noopener" title="Mở Light Pollution Map tại vị trí này">🌃 LPM</a>'
            f'</div>',
            unsafe_allow_html=True
        )

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
        def _cloud_icon_cell(pct_str, precip_val=0.0, temp_val=None):
            pct = int(pct_str.replace('%',''))
            if precip_val is not None and precip_val > 0.5:
                if temp_val is not None and temp_val < 1.0:
                    icon, col = '\u2744\ufe0f', '#93c5fd'
                elif pct > 70:
                    icon, col = '\u26c8\ufe0f', '#f87171'
                else:
                    icon, col = '\U0001f327\ufe0f', '#60a5fa'
            elif pct <= 20:
                icon, col = '\u2600\ufe0f', '#fbbf24'
            elif pct <= 45:
                icon, col = '\u26c5', '#fcd34d'
            elif pct <= 70:
                icon, col = '\U0001f325\ufe0f', '#94a3b8'
            else:
                icon, col = '\u2601\ufe0f', '#64748b'
            return (f'<div style="display:flex;align-items:center;gap:2px;white-space:nowrap;">'
                    f'<span style="font-size:15px;line-height:1;">{icon}</span>'
                    f'<span style="font-size:11px;color:{col};font-weight:600;">{pct_str}</span>'
                    f'</div>')

        def _wind_icon(ws_str):
            ws = float(ws_str.replace('m/s',''))
            if ws < 2:   icon,col = '','#94a3b8'
            elif ws < 5: icon,col = '','#60a5fa'
            else:        icon,col = '','#f97316'
            return f'<span style="color:{col}">{icon} {ws_str}</span>'

        rows_html = ''
        for i, row in enumerate(weather_table_data):
            bg = 'rgba(234,88,12,0.10)' if i % 2 == 0 else 'rgba(194,65,12,0.06)'
            time_lbl = row['⏰']
            cloud_cell = _cloud_icon_cell(row['☁️'], row.get('_precip', 0.0), row.get('_temp'))
            humid_val  = row['💧']
            wind_cell  = _wind_icon(row['💨'])
            stars      = row['📸']
            rows_html += (
                f'<tr style="background:{bg};border-bottom:1px solid rgba(234,88,12,0.18);">'
                f'<td style="padding:8px 8px;font-weight:700;color:#fb923c;white-space:nowrap;">{time_lbl}</td>'
                f'<td style="padding:8px 8px;overflow:hidden;">{cloud_cell}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{humid_val}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{wind_cell}</td>'
                f'<td style="padding:8px 8px;font-size:16px;letter-spacing:1px;">{stars}</td>'
                f'</tr>'
            )

        table_html = f"""
<div style="background:#1a0a00;border:1.5px solid rgba(234,88,12,0.45);border-radius:12px;overflow:hidden;margin-bottom:8px;box-shadow:0 0 20px rgba(234,88,12,0.10);">
  <table style="width:100%;border-collapse:collapse;font-size:14px;font-family:'Segoe UI',sans-serif;table-layout:fixed;">
    <thead>
      <tr style="background:linear-gradient(90deg,rgba(154,52,18,0.90),rgba(120,40,10,0.75));border-bottom:2px solid rgba(234,88,12,0.55);">
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:14%;">⏰</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:20%;">🌤️</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:13%;">💧</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:16%;">💨</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:37%;">📸</th>
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
