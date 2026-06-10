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
    "27. Okutama 奥多摩湖, Tokyo": [35.7920, 139.0475],
    "28. Choshi Inubosaki 犬吠埼灯台, Chiba": [35.7077, 140.8685],
    "29. Kujukuri Beach 九十九里浜, Chiba": [35.5307, 140.4428],
    "30. Nokogiriyama 鋸山展望台, Chiba": [35.1604, 139.8357],
    "31. Oarai Isosaki Shrine 神磯の鳥居, Ibaraki": [36.3145, 140.5844],
    "32. Fukuroda Falls 袋田の滝, Ibaraki": [36.7657, 140.3542],
    "33. Plateau Satomi プラトーさとみ, Ibaraki": [36.6658, 140.4986],
    "34. Oze Numata 尾瀬ヶ原, Gunma": [36.9306, 139.2150],
    "35. Tanbara Highlands 玉原高原, Gunma": [36.7833, 139.0830],
    "36. Chichibu Misotsuchi 三十槌氷柱周辺, Saitama": [35.9563, 138.9255],
    "37. Nakatsu Gorge 中津峡, Saitama": [35.9977, 139.0124],
    "38. Kozushima Maehama 前浜海岸, Tokyo": [34.2086, 139.1358],
    "39. Mikurajima Observatory 御蔵島展望地, Tokyo": [33.8740, 139.5950],
    "40. Hachijojima Nambara 南原千畳岩海岸, Tokyo": [33.1003, 139.7706],
    "41. Yamanakako Panorama 山中湖パノラマ台, Yamanashi": [35.4154, 138.8758],
    "42. Kiyosato Seisenryo 清泉寮, Yamanashi": [35.8967, 138.4355],
    "43. Misaka Pass 御坂峠, Yamanashi": [35.5493, 138.7090],
    "44. Nobeyama Radio Observatory 野辺山, Nagano": [35.9405, 138.4740],
    "45. Takabocchi Highlands 高ボッチ高原, Nagano": [36.1045, 138.0170],
    "46. Soni Highlands 曽爾高原, Nara": [34.5346, 136.1506],
    "47. Norikura Tatamidaira 乗鞍畳平, Gifu": [36.1068, 137.5538],
    "48. Hirayu Pass 平湯峠, Gifu": [36.1658, 137.5507],
    "49. Shinhotaka Ropeway 新穂高, Gifu": [36.2898, 137.6462],
    "50. Hakusan Shirakawago White Road, Ishikawa": [36.2212, 136.7928],
    "51. Chirihama Beach 千里浜なぎさドライブウェイ, Ishikawa": [36.8157, 136.7448],
    "52. Mikatagoko Rainbow Line 三方五湖, Fukui": [35.5945, 135.8824],
    "53. Kumano Oni-ga-jo 鬼ヶ城, Mie": [33.8930, 136.1113],
    "54. Daiozaki Lighthouse 大王崎, Mie": [34.2708, 136.8964],
    "55. Odaigahara Driveway 大台ヶ原, Nara": [34.1856, 136.1090],
    "56. Tenkawa Miroku Pass 天川村, Nara": [34.2460, 135.8680],
    "57. Nishiharima Observatory 西はりま天文台, Hyogo": [35.0258, 134.3553],
    "58. Bisei Observatory 美星天文台, Okayama": [34.6712, 133.5483],
    "59. Hiruzen Highlands 蒜山高原, Okayama": [35.2770, 133.6740],
    "60. Tottori Sand Dunes 鳥取砂丘, Tottori": [35.5397, 134.2383],
    "61. Misasa Onsen Observatory 三朝温泉周辺, Tottori": [35.4087, 133.8618],
    "62. Akiyoshidai Karst 秋吉台, Yamaguchi": [34.2576, 131.3070],
    "63. Shikoku Karst 四国カルスト, Ehime": [33.3804, 132.9536],
    "64. Ashizuri Cape 足摺岬, Kochi": [32.7196, 133.0182],
    "65. Sata Cape 佐田岬, Ehime": [33.4304, 132.1062],
    "66. Aso Kusasenri 草千里ヶ浜, Kumamoto": [32.8845, 131.0808],
    "67. Daikanbo 大観峰, Kumamoto": [32.9506, 131.0904],
    "68. Ikitsuki Island 生月島, Nagasaki": [33.3720, 129.3988],
    "69. Yobuko Cape Hado 波戸岬, Saga": [33.5878, 129.8780],
    "70. Takachiho Amaterasu Railway 高千穂, Miyazaki": [32.7092, 131.3086],
    "71. Cape Toi 都井岬, Miyazaki": [31.3750, 131.3450],
    "72. Kaimondake 開聞岳周辺, Kagoshima": [31.1805, 130.5284],
    "73. Yoron Island 百合ヶ浜, Kagoshima": [27.0452, 128.4246],
    "74. Ishigaki Hirakubozaki 平久保崎, Okinawa": [24.6053, 124.3427],
    "75. Tamatorizaki Observatory 玉取崎展望台, Okinawa": [24.4553, 124.2520],
    "76. Iriomote Hoshizuna Beach 星砂の浜, Okinawa": [24.4078, 123.7575],
    "77. Hateruma Observatory 波照間島, Okinawa": [24.0558, 123.8060],
    "78. Cape Zanpa 残波岬, Okinawa": [26.4360, 127.7045],
    "79. Kouri Bridge 古宇利大橋, Okinawa": [26.7069, 128.0188],
    "80. Cape Hedo 辺戸岬, Okinawa": [26.8716, 128.2695],
    "81. Miyakojima Higashi-Hennazaki 東平安名崎, Okinawa": [24.7353, 125.4672],
    "82. Kurima Bridge 来間大橋, Okinawa": [24.7248, 125.2478],
    "83. Aogashima Observatory 青ヶ島展望公園, Tokyo": [32.4666, 139.7678],
    "84. Niijima Habushiura 羽伏浦海岸, Tokyo": [34.3872, 139.2878],
    "85. Shikinejima Tomari Beach 泊海岸, Tokyo": [34.3265, 139.2158],
    "86. Ogasawara Weather Station 小笠原, Tokyo": [27.0944, 142.1917],
    "87. Kirigamine Highlands 霧ヶ峰, Nagano": [36.1030, 138.1946],
    "88. Kurumayama 車山高原, Nagano": [36.1038, 138.1926],
    "89. Yachiho Plateau 八千穂高原, Nagano": [36.0690, 138.4567],
    "90. Senjojiki Cirque 千畳敷カール, Nagano": [35.7725, 137.8173],
    "91. Happo Pond 八方池, Nagano": [36.6988, 137.8355],
    "92. Tsugaike Nature Park 栂池自然園, Nagano": [36.7582, 137.8758],
    "93. Hakuba Iwatake 白馬岩岳, Nagano": [36.7083, 137.8443],
    "94. Shiga Highlands 志賀高原, Nagano": [36.7172, 138.5177],
    "95. Mt. Myoko 妙高高原, Niigata": [36.8917, 138.1708],
    "96. Yahiko Skyline 弥彦山, Niigata": [37.7052, 138.8178],
    "97. Senami Coast 瀬波海岸, Niigata": [38.2410, 139.4628],
    "98. Gassan Hachigome 月山八合目, Yamagata": [38.5484, 140.0264],
    "99. Toriumi Observatory 鳥海山鉾立, Akita": [39.0933, 140.0497],
    "100. Cape Tappi 龍飛崎, Aomori": [41.2570, 140.3495]
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
             ("is_custom_point", True), ("weather_source", "🔀 Blend (JMA+ECMWF+GFS)"),
             ("active_source_used", "JMA"),
             ("_last_tip", None), ("_last_lc", None),
             ("_source_auto", True), ("_ecmwf_available", True),
             ("map_tile", "satellite"),
             ("_need_fly", False)]:
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
    utc_offset_h là offset của location (JST=+9).
    Dùng +30 phút để tính giữa khung giờ → chính xác hơn khi hiển thị trên chart."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    moon = ephem.Moon(); moon.compute(obs)
    return round(math.degrees(float(moon.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_exact_sun_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao mặt trời (có thể âm khi dưới đường chân trời = ban đêm).
    utc_offset_h là offset của location (JST=+9)."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    sun = ephem.Sun(); sun.compute(obs)
    return round(math.degrees(float(sun.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_milkyway_altitude(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao trung tâm Dải Ngân Hà (Galactic Center, Sgr A*).
    RA = 17h45m40s, Dec = -29°00'28" (J2000)
    Trả về (altitude_deg, azimuth_deg) — altitude < 0 = dưới chân trời."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    # Galactic Center: RA 17h45m40s, Dec -29°00'28" (J2000)
    gc = ephem.FixedBody()
    gc._ra  = ephem.hours('17:45:40.04')
    gc._dec = ephem.degrees('-29:00:28.1')
    gc._epoch = ephem.J2000
    gc.compute(obs)
    return round(math.degrees(float(gc.alt)), 1), round(math.degrees(float(gc.az)), 1)

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
        (35.1313, 139.6179): (4.5, 21.20), #  1 Jogashima          green     → Bortle 4 (20.8–21.3)
        (35.1408, 139.1609): (4.5, 20.80), #  6 Manazuru           light green (near Odawara) → 4.5 edge / 5
        (35.5400, 139.7030): (9, 17.80),   # Kawasaki city core    — lightpollutionmap SQM ≈17.8, Bortle 9
        (35.4437, 139.6380): (9, 17.90),   # Yokohama core         — very bright urban core
        # ── Chiba / Boso ──────────────────────────────────────────────────────
        (34.9517, 139.8103): (4, 21.20),   #  2 Tateyama           green
        (34.9071, 139.8611): (4, 21.20),   #  3 Minamiboso         green
        (35.1795, 140.3729): (4, 21.25),   #  4 Onjuku             green
        (35.3196, 140.4091): (4, 21.25),   #  5 Isumi              green
        # ── Shizuoka / Izu ────────────────────────────────────────────────────
        (34.6588, 138.9868): (3.5, 21.77), #  7 Shimoda — calibrated from sample SQM 21.77
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
        
        # ── Chiba ─────────────────────────────────────────────────────────────
        (35.7077, 140.8685): (4, 21.20),   # 28 Inubosaki
        (35.5307, 140.4428): (4.5, 21.00), # 29 Kujukuri
        (35.1604, 139.8357): (4.5, 21.00), # 30 Nokogiriyama
        # ── Ibaraki ───────────────────────────────────────────────────────────
        (36.3145, 140.5844): (5, 20.80),   # 31 Oarai
        (36.7657, 140.3542): (4, 21.40),   # 32 Fukuroda
        (36.6658, 140.4986): (4, 21.75),   # 33 Plateau Satomi
        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.9306, 139.2150): (3, 21.90),   # 34 Oze
        (36.7833, 139.0830): (3.5, 21.60), # 35 Tanbara
        # ── Saitama ───────────────────────────────────────────────────────────
        (35.9563, 138.9255): (4, 21.40),   # 36 Misotsuchi
        (35.9977, 139.0124): (4, 21.40),   # 37 Nakatsu Gorge (replaced Mitsumine — too close to 36)
        # ── Tokyo Islands ─────────────────────────────────────────────────────
        (34.2086, 139.1358): (3, 21.80),   # 38 Kozushima
        (33.8740, 139.5950): (2.5, 21.95), # 39 Mikurajima
        (33.1003, 139.7706): (2.5, 21.95), # 40 Hachijojima
        (32.4666, 139.7678): (2, 22.00),   # 83 Aogashima
        (34.3872, 139.2878): (3, 21.80),   # 84 Niijima
        (34.3265, 139.2158): (3, 21.80),   # 85 Shikinejima
        (27.0944, 142.1917): (2, 22.00),   # 86 Ogasawara
        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.4154, 138.8758): (4, 21.50),   # 41 Yamanakako Panorama
        (35.8967, 138.4355): (3.5, 21.65), # 42 Kiyosato
        (35.5493, 138.7090): (4, 21.40),   # 43 Misaka Pass
        # ── Nagano ────────────────────────────────────────────────────────────
        (35.9405, 138.4740): (3, 21.80),   # 44 Nobeyama
        (36.1045, 138.0170): (4, 21.80),   # 45 Takabocchi
        (36.1030, 138.1946): (4, 21.75),   # 87 Kirigamine
        (36.1038, 138.1926): (4, 21.75),   # 88 Kurumayama
        (36.0690, 138.4567): (3, 21.80),   # 89 Yachiho
        (35.7725, 137.8173): (3, 21.90),   # 90 Senjojiki
        (36.6988, 137.8355): (3, 21.85),   # 91 Happo Pond
        (36.7582, 137.8758): (3, 21.85),   # 92 Tsugaike
        (36.7083, 137.8443): (3, 21.85),   # 93 Hakuba Iwatake
        (36.7172, 138.5177): (3, 21.80),   # 94 Shiga Highlands
        # ── Niigata ───────────────────────────────────────────────────────────
        (36.8917, 138.1708): (3, 21.75),   # 95 Myoko
        (37.7052, 138.8178): (4, 21.20),   # 96 Yahiko
        (38.2410, 139.4628): (4, 21.20),   # 97 Senami Coast
        # ── Yamagata ──────────────────────────────────────────────────────────
        (38.5484, 140.0264): (3, 21.85),   # 98 Gassan
        # ── Akita ─────────────────────────────────────────────────────────────
        (39.0933, 140.0497): (2.5, 21.90), # 99 Toriumi
        # ── Aomori ────────────────────────────────────────────────────────────
        (41.2570, 140.3495): (3, 21.75),   # 100 Cape Tappi
        # ── Gifu ──────────────────────────────────────────────────────────────
        (36.1068, 137.5538): (2.5, 21.95), # 47 Norikura
        (36.1658, 137.5507): (3, 21.90),   # 48 Hirayu
        (36.2898, 137.6462): (3, 21.90),   # 49 Shinhotaka
        # ── Ishikawa ──────────────────────────────────────────────────────────
        (36.2212, 136.7928): (3, 21.80),   # 50 Hakusan
        (36.8157, 136.7448): (4, 21.30),   # 51 Chirihama
        # ── Fukui ─────────────────────────────────────────────────────────────
        (35.5945, 135.8824): (4, 21.30),   # 52 Mikatagoko
        # ── Mie ───────────────────────────────────────────────────────────────
        (33.8930, 136.1113): (3, 21.80),   # 53 Oni-ga-jo
        (34.2708, 136.8964): (3.5, 21.60), # 54 Daiozaki
        # ── Nara ──────────────────────────────────────────────────────────────
        (34.5346, 136.1506): (3, 21.80),   # 46 Soni Highlands
        (34.1856, 136.1090): (2.5, 21.95), # 55 Odaigahara
        (34.2460, 135.8680): (3, 21.85),   # 56 Tenkawa
        # ── Hyogo ─────────────────────────────────────────────────────────────
        (35.0258, 134.3553): (2.5, 21.90), # 57 Nishiharima
        # ── Okayama ───────────────────────────────────────────────────────────
        (34.6712, 133.5483): (3, 21.80),   # 58 Bisei
        (35.2770, 133.6740): (3, 21.80),   # 59 Hiruzen
        # ── Tottori ───────────────────────────────────────────────────────────
        (35.5397, 134.2383): (3.5, 21.60), # 60 Tottori Sand Dunes
        (35.4087, 133.8618): (3.5, 21.60), # 61 Misasa
        # ── Yamaguchi ─────────────────────────────────────────────────────────
        (34.2576, 131.3070): (3, 21.80),   # 62 Akiyoshidai
        # ── Ehime ─────────────────────────────────────────────────────────────
        (33.3804, 132.9536): (2.5, 21.95), # 63 Shikoku Karst
        (33.4304, 132.1062): (3, 21.80),   # 65 Sata Cape
        # ── Kochi ─────────────────────────────────────────────────────────────
        (32.7196, 133.0182): (2.5, 21.95), # 64 Ashizuri
        # ── Saga ──────────────────────────────────────────────────────────────
        (33.5878, 129.8780): (3.5, 21.50), # 69 Yobuko
        # ── Nagasaki ──────────────────────────────────────────────────────────
        (33.3720, 129.3988): (3, 21.80),   # 68 Ikitsuki
        # ── Kumamoto ──────────────────────────────────────────────────────────
        (32.8845, 131.0808): (2.5, 21.95), # 66 Kusasenri
        (32.9506, 131.0904): (2.5, 21.95), # 67 Daikanbo
        # ── Miyazaki ──────────────────────────────────────────────────────────
        (32.7092, 131.3086): (3, 21.80),   # 70 Takachiho
        (31.3750, 131.3450): (2.5, 21.95), # 71 Cape Toi
        # ── Kagoshima ─────────────────────────────────────────────────────────
        (31.1805, 130.5284): (3, 21.80),   # 72 Kaimondake
        (27.0452, 128.4246): (2, 22.00),   # 73 Yoron
        # ── Okinawa ───────────────────────────────────────────────────────────
        (24.6053, 124.3427): (2, 22.00),   # 74 Hirakubozaki
        (24.4553, 124.2520): (2, 22.00),   # 75 Tamatorizaki
        (24.4078, 123.7575): (2, 22.00),   # 76 Iriomote
        (24.0558, 123.8060): (1.5, 22.00), # 77 Hateruma
        (26.4360, 127.7045): (3.5, 21.50), # 78 Cape Zanpa
        (26.7069, 128.0188): (3, 21.80),   # 79 Kouri Bridge
        (26.8716, 128.2695): (2.5, 21.95), # 80 Cape Hedo
        (24.7353, 125.4672): (2, 22.00),   # 81 Higashi-Hennazaki
        (24.7248, 125.2478): (2, 22.00),   # 82 Kurima Bridge
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
        
        # ── Hokkaido ──────────────────────────────────────────────────────────
        (42.9849, 144.3814, "Kushiro",      20.40),
        (44.0206, 144.2730, "Abashiri",     20.60),
        (45.4156, 141.6731, "Wakkanai",     20.80),
        (42.3172, 140.9738, "Muroran",      19.60),
        (42.5510, 141.3550, "Tomakomai",    19.40),
        (42.9238, 143.1968, "Obihiro",      20.20),
        (43.8031, 143.8958, "Kitami",       20.40),
        (41.7687, 140.7288, "Hakodate",     19.60),

        # ── Tohoku ────────────────────────────────────────────────────────────
        (40.5123, 141.4880, "Hachinohe",    19.90),
        (39.7036, 141.1527, "Morioka",      20.10),
        (39.6411, 141.9571, "Miyako",       20.50),
        (39.3150, 141.1167, "Hanamaki",     20.20),
        (38.2554, 140.8777, "Natori",       19.40),
        (38.4342, 141.3028, "Ishinomaki",   19.80),
        (38.9081, 139.8365, "Sakata",       20.20),
        (38.9140, 139.8500, "Tsuruoka",     20.20),
        (37.4947, 139.9297, "Aizuwakamatsu",20.30),
        (37.0505, 140.8877, "Iwaki",        19.70),

        # ── Ibaraki ───────────────────────────────────────────────────────────
        (36.3418, 140.4468, "Mito",         19.50),
        (36.0835, 140.0764, "Tsukuba",      19.20),
        (36.3966, 140.5348, "Hitachi",      19.50),
        (35.9654, 140.6448, "Kashima",      19.60),
        (36.1812, 139.9930, "Koga",         19.30),

        # ── Tochigi ───────────────────────────────────────────────────────────
        (36.5658, 139.8836, "Kanuma",       19.70),
        (36.8717, 139.9959, "Nasu-Shiobara",20.10),
        (36.3140, 139.8000, "Oyama",        19.30),

        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.3219, 139.0033, "Isesaki",      19.30),
        (36.2916, 139.3753, "Ota",          19.20),
        (36.3380, 139.1970, "Kiryu",        19.60),

        # ── Saitama ───────────────────────────────────────────────────────────
        (35.9756, 139.7528, "Kasukabe",     18.80),
        (35.8303, 139.8057, "Koshigaya",    18.60),
        (35.9917, 139.0858, "Chichibu",     20.30),
        (35.8569, 139.6489, "Kawaguchi",    18.20),

        # ── Chiba ─────────────────────────────────────────────────────────────
        (35.7345, 140.8266, "Choshi",       19.60),
        (35.6047, 140.1233, "Funabashi",    18.10),
        (35.7876, 140.3186, "Narita",       19.10),
        (35.7204, 140.1024, "Matsudo",      18.20),
        (35.4979, 140.1141, "Ichihara",     18.70),

        # ── Tokyo Metro ───────────────────────────────────────────────────────
        (35.7289, 139.7100, "Ikebukuro",    17.30),
        (35.6938, 139.7034, "Shinjuku",     17.20),
        (35.6580, 139.7016, "Shibuya",      17.20),
        (35.7138, 139.7772, "Ueno",         17.40),
        (35.6812, 139.7671, "Tokyo-Sta",    17.20),

        # ── Kanagawa ──────────────────────────────────────────────────────────
        (35.3358, 139.3496, "Hiratsuka",    18.90),
        (35.3192, 139.5467, "Kamakura",     19.10),
        (35.2646, 139.1521, "Hakone",       20.30),
        (35.2836, 139.6722, "Miura",        19.40),

        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.6639, 138.5684, "Kai",          19.80),
        (35.4875, 138.8078, "Fujiyoshida",  20.20),
        (35.5500, 138.9000, "Yamanakako",   20.60),

        # ── Nagano ────────────────────────────────────────────────────────────
        (36.6513, 138.1810, "Suzaka",       20.20),
        (36.3134, 138.5968, "Saku",         20.60),
        (36.2140, 138.2520, "Komoro",       20.50),
        (35.5147, 137.8218, "Iida",         20.30),
        (35.7286, 137.9537, "Ina",          20.40),

        # ── Niigata ───────────────────────────────────────────────────────────
        (37.4464, 138.8512, "Nagaoka",      19.90),
        (37.1483, 138.2364, "Joetsu",       20.10),
        (38.0603, 138.4376, "Sado",         20.80),

        # ── Hokuriku ──────────────────────────────────────────────────────────
        (36.7500, 137.0167, "Takaoka",      19.60),
        (36.0652, 136.2216, "Sabae",        19.60),
        (36.4026, 136.4508, "Komatsu",      19.60),

        # ── Tokai ─────────────────────────────────────────────────────────────
        (35.4233, 136.7607, "Ogaki",        19.30),
        (34.7303, 136.5086, "Tsu",          19.50),
        (34.7180, 137.8515, "Iwata",        19.20),
        (34.7687, 137.9980, "Kakegawa",     19.40),
        (35.0956, 138.8635, "Numazu",       19.40),
        (35.1223, 138.9185, "Mishima",      19.40),

        # ── Kansai ────────────────────────────────────────────────────────────
        (34.6851, 135.8048, "Tenri",        19.50),
        (34.5733, 135.4828, "Sakai",        18.10),
        (34.8164, 135.5683, "Takatsuki",    18.50),
        (34.6930, 135.1940, "Akashi",       18.70),
        (34.2305, 135.1708, "Wakayama",     19.50),

        # ── Chugoku ───────────────────────────────────────────────────────────
        (35.4723, 133.0505, "Matsue",       20.20),
        (35.4281, 133.3309, "Yonago",       20.10),
        (35.5011, 134.2351, "Tottori",      20.20),
        (34.1785, 131.4737, "Yamaguchi",    20.20),
        (33.9578, 130.9414, "Shimonoseki",  19.40),

        # ── Shikoku ───────────────────────────────────────────────────────────
        (33.9196, 133.1810, "Niihama",      19.90),
        (33.8416, 132.7661, "Iyo",          20.10),
        (33.5624, 133.5373, "Nankoku",      20.20),
        (33.3636, 134.1520, "Muroto",       20.80),

        # ── Kyushu ────────────────────────────────────────────────────────────
        (32.7448, 129.8737, "Nagasaki",     19.50),
        (33.1799, 129.7150, "Sasebo",       19.80),
        (32.7503, 129.8780, "Nagasaki-C",   19.50),
        (31.9111, 131.4239, "Miyazaki",     19.60),
        (32.5833, 131.6667, "Nobeoka",      20.00),
        (31.7196, 131.0616, "Kobayashi",    20.40),
        (32.0686, 131.6514, "Hyuga",        20.00),
        (33.2635, 130.3009, "Karatsu",      19.80),
        (32.0134, 130.2110, "Izumi",        20.20),
        (31.3783, 130.8528, "Kanoya",       20.00),

        # ── Okinawa ───────────────────────────────────────────────────────────
        (26.3344, 127.8056, "Okinawa-C",    19.20),
        (26.2122, 127.6873, "Naha-Airport", 19.30),
        (24.3448, 124.1572, "Ishigaki",     20.80),
        (24.8056, 125.2811, "Miyakojima",   20.90),
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
    Day 0-3: ECMWF x0.50 + JMA x0.40 + GFS x0.10  (ECMWF 51-member ensemble > JMA single-run)
    Day 4-7: ECMWF x0.56 + GFS x0.30 + JMA x0.14  (JMA MSM coverage ends ~day 3.5)
    Re-normalises weights if any model has missing data.
    Returns (float_value, label_string)
    """
    jma   = _get_raw(hourly, field, "_jma_msm",      idx)
    ecmwf = _get_raw(hourly, field, "_ecmwf_ifs025",  idx)
    gfs   = _get_raw(hourly, field, "_gfs_seamless",  idx)

    if day_offset <= 3:
        weights = {"jma": 0.40, "ecmwf": 0.50, "gfs": 0.10}  # ECMWF ensemble > JMA single-run
    else:
        weights = {"jma": 0.14, "ecmwf": 0.56, "gfs": 0.30}  # JMA MSM hết coverage ~day 3.5

    vals  = {"jma": jma, "ecmwf": ecmwf, "gfs": gfs}
    avail = {k: v for k, v in vals.items() if v is not None}
    if not avail:
        return 0.0, None

    total_w = sum(weights[k] for k in avail)
    blended = sum(weights[k] * v for k, v in avail.items()) / total_w
    return round(blended, 1), "Blend"

def calc_tcc(low_pct, mid_pct, high_pct):
    """TCC = 1-(1-L)(1-M)(1-H) — công thức xác suất, CHỈ để so sánh/debug,
    không dùng cho stars rating (API cloud tích phân 3D chính xác hơn)."""
    l = max(0.0, min(100.0, low_pct))  / 100.0
    m = max(0.0, min(100.0, mid_pct))  / 100.0
    h = max(0.0, min(100.0, high_pct)) / 100.0
    return round((1.0 - (1.0 - l) * (1.0 - m) * (1.0 - h)) * 100.0, 1)

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
# If 00:00~05:59 → we're still in the previous night (18:00 yesterday → 06:00 today)
# so shift base back 1 day to keep tonight's 00:00~06:00 slots visible
if _now_jst.hour < 6:
    _night_base_jst = _now_jst - timedelta(days=1)
else:
    _night_base_jst = _now_jst
# date_options i=0 → tonight (18:00 of _night_base_jst)
date_options = [
    f"Evening {(_night_base_jst+timedelta(days=i)).strftime('%d/%m(%a)')} → Morning {(_night_base_jst+timedelta(days=i+1)).strftime('%d/%m(%a)')}"
    for i in range(7)
]

target_date = (_night_base_jst + timedelta(days=st.session_state.day_offset)).replace(tzinfo=None)
next_date   = target_date + timedelta(days=1)

moon_pct, moon_text = get_moon_phase_percent(target_date)

prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Blend (JMA+ECMWF+GFS)")
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

# Auto-switch: chỉ áp dụng khi đang dùng JMA đơn lẻ (không can thiệp Blend)
# Blend tự xử lý JMA missing bên trong get_val_blended (re-normalise weights).
if st.session_state._source_auto and hourly_data:
    _cur = st.session_state.weather_source
    _blend_name = "🔀 Blend (JMA+ECMWF+GFS)"
    if _cur not in (_blend_name, "US (GFS)", "EU (ECMWF)"):
        # Đang ở JMA (hoặc auto chưa set) → kiểm tra JMA coverage
        jma_ok = (_jma_has_data_for_date(hourly_data, target_date.strftime("%Y-%m-%d")) or
                  _jma_has_data_for_date(hourly_data, next_date.strftime("%Y-%m-%d")))
        if not jma_ok:
            # JMA hết data → fallback GFS
            st.session_state.weather_source = "US (GFS)"

# Sau auto-switch, cập nhật lại flags theo source hiện tại
prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Blend (JMA+ECMWF+GFS)")
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

@st.cache_data(ttl=1800, show_spinner=False)
def _build_night_data(lat, lon, slots, hourly_data_frozen, weather_source, loc_utc_offset_h):
    """Cache toàn bộ vòng lặp tính weather table + moon/sun/MW altitudes.
    Key cache = (lat, lon, slots, source) — chỉ recompute khi thực sự đổi ngày/địa điểm/source."""
    # hourly_data_frozen là tuple-of-items để hashable
    hourly = dict(hourly_data_frozen) if hourly_data_frozen else {}

    _prefer_jma = weather_source not in ["US (GFS)", "EU (ECMWF)"]
    _use_blend  = weather_source == "🔀 Blend (JMA+ECMWF+GFS)"
    _use_ecmwf  = weather_source == "EU (ECMWF)"

    # day_offset chỉ ảnh hưởng blend weight — dùng slot index 0 làm proxy
    _day_offset_proxy = 0
    if slots:
        yr0, mo0, dy0 = slots[0][0], slots[0][1], slots[0][2]
        from datetime import date as _date
        _today = _date.today()
        _day_offset_proxy = (_date(yr0, mo0, dy0) - _today).days
        _day_offset_proxy = max(0, min(6, _day_offset_proxy))

    out_table  = []
    out_hours  = []
    out_moon   = []
    out_sun    = []
    out_mw     = []
    out_debug  = {"low": 0, "mid": 0, "high": 0, "total": 0}
    out_srcs   = set()

    times_list = hourly.get("time", [])

    for yr, mo, dy, hr_local, label, date_prefix in slots:
        out_hours.append(label)
        out_moon.append(calculate_exact_moon_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        out_sun.append(calculate_exact_sun_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        mw_alt, _ = calculate_milkyway_altitude(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h)
        out_mw.append(mw_alt)

        if not times_list:
            continue

        target_ts = f"{date_prefix}T{hr_local:02d}:00"
        idx = next((i for i, t in enumerate(times_list) if t.startswith(target_ts)), -1)
        if idx == -1:
            continue

        if _use_blend:
            avg_cloud, src1 = get_val_blended(hourly, "cloud_cover",          idx, _day_offset_proxy)
            low_c,     _    = get_val_blended(hourly, "cloud_cover_low",       idx, _day_offset_proxy)
            mid_c,     _    = get_val_blended(hourly, "cloud_cover_mid",       idx, _day_offset_proxy)
            high_c,    _    = get_val_blended(hourly, "cloud_cover_high",      idx, _day_offset_proxy)
            humid,     _    = get_val_blended(hourly, "relative_humidity_2m",  idx, _day_offset_proxy)
            wind_speed,_    = get_val_blended(hourly, "wind_speed_10m",        idx, _day_offset_proxy)
            temp_val,  _    = get_val_blended(hourly, "temperature_2m",        idx, _day_offset_proxy)
            precip_val,_    = get_val_blended(hourly, "precipitation",         idx, _day_offset_proxy)
            if src1: out_srcs.add(src1)
        elif _use_ecmwf:
            avg_cloud  = _get_raw(hourly, "cloud_cover",          "_ecmwf_ifs025", idx) or 0.0
            low_c      = _get_raw(hourly, "cloud_cover_low",       "_ecmwf_ifs025", idx) or 0.0
            mid_c      = _get_raw(hourly, "cloud_cover_mid",       "_ecmwf_ifs025", idx) or 0.0
            high_c     = _get_raw(hourly, "cloud_cover_high",      "_ecmwf_ifs025", idx) or 0.0
            humid      = _get_raw(hourly, "relative_humidity_2m",  "_ecmwf_ifs025", idx) or 0.0
            wind_speed = _get_raw(hourly, "wind_speed_10m",        "_ecmwf_ifs025", idx) or 0.0
            temp_val   = _get_raw(hourly, "temperature_2m",        "_ecmwf_ifs025", idx) or 0.0
            precip_val = _get_raw(hourly, "precipitation",         "_ecmwf_ifs025", idx) or 0.0
            src1 = "ECMWF"
            out_srcs.add("ECMWF")
        else:
            avg_cloud, src1 = get_val(hourly, "cloud_cover",          idx, _prefer_jma)
            low_c,     _    = get_val(hourly, "cloud_cover_low",      idx, _prefer_jma)
            mid_c,     _    = get_val(hourly, "cloud_cover_mid",      idx, _prefer_jma)
            high_c,    _    = get_val(hourly, "cloud_cover_high",     idx, _prefer_jma)
            humid,     _    = get_val(hourly, "relative_humidity_2m", idx, _prefer_jma)
            wind_speed,_    = get_val(hourly, "wind_speed_10m",       idx, _prefer_jma)
            temp_val,  _    = get_val(hourly, "temperature_2m",       idx, _prefer_jma)
            precip_val,_    = get_val(hourly, "precipitation",        idx, _prefer_jma)
            if src1: out_srcs.add(src1)

        if len(out_table) == 0:
            out_debug = {
                "low":   int(low_c),
                "mid":   int(mid_c),
                "high":  int(high_c),
                "total": int(avg_cloud),                        # API cloud → rating
                "tcc":   int(calc_tcc(low_c, mid_c, high_c)),  # công thức xác suất → compare
            }

        score = 100 - avg_cloud
        if score >= 92:   stars = "⭐⭐⭐⭐"
        elif score >= 75: stars = "⭐⭐⭐☆"
        elif score >= 50: stars = "⭐⭐☆☆"
        elif score >= 20: stars = "⭐☆☆☆"
        else:             stars = "☆☆☆☆"

        out_table.append({
            "⏰": label,
            "☁️": f"{int(avg_cloud)}%",
            "💧": f"{int(humid)}%",
            "💨": f"{round(wind_speed,1)}m/s",
            "📸": stars,
            "_temp": temp_val,
            "_precip": precip_val,
        })

    return out_table, out_hours, out_moon, out_sun, out_mw, out_debug, out_srcs

# Chuyển hourly_data sang dạng hashable để cache key hoạt động
_hourly_frozen = tuple(
    (k, tuple(v) if isinstance(v, list) else v)
    for k, v in (hourly_data.items() if hourly_data else [])
)

# ── PREFETCH TẤT CẢ 7 ĐÊM ngay sau khi có hourly_data ────────────────────────
# Mục đích: warm up cache cho toàn bộ 7 ngày ngay khi chọn location.
# Khi user bấm Next/Prev → _build_night_data đã có cache → gần như instant.
# Chạy tuần tự (không thread) vì @st.cache_data không thread-safe khi write.
def _make_slots_for_offset(base_jst, day_off):
    td = (base_jst + timedelta(days=day_off)).replace(tzinfo=None)
    nd = td + timedelta(days=1)
    return tuple([
        (td.year, td.month, td.day, 18, "18:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 19, "19:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 20, "20:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 21, "21:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 22, "22:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 23, "23:00", td.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  0, "00:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  1, "01:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  2, "02:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  3, "03:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  4, "04:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  5, "05:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  6, "06:00", nd.strftime("%Y-%m-%d")),
    ])

# Prefetch các ngày KHÁC ngày hiện tại (ngày hiện tại sẽ được tính ngay bên dưới)
for _poff in range(7):
    if _poff != st.session_state.day_offset:
        _build_night_data(
            st.session_state.lat, st.session_state.lon,
            _make_slots_for_offset(_night_base_jst, _poff),
            _hourly_frozen,
            st.session_state.weather_source,
            loc_utc_offset_h,
        )

(weather_table_data, hours_labels, moon_altitudes, sun_altitudes,
 milkyway_altitudes, current_cloud_debug, sources_used) = _build_night_data(
    st.session_state.lat, st.session_state.lon,
    tuple(desired_slots),
    _hourly_frozen,
    st.session_state.weather_source,
    loc_utc_offset_h,
)
sources_used = set(sources_used)  # trả về từ cache là frozenset hoặc set, đảm bảo là set

# Label thực tế đã dùng — phân biệt auto-fallback với user chọn tay
if use_blend:
    active_source_label = "🔀 Blend (JMA+ECMWF+GFS)"
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

# ── Folium map — location/zoom CỐ ĐỊNH, không thay đổi theo session state ──
# st_folium với key cố định giữ nguyên camera (pan/zoom) của user giữa các rerun.
# Nếu truyền location động → folium object thay đổi → st_folium reset view.
# → Luôn dùng tọa độ khởi tạo cố định; map_center chỉ còn dùng cho lần init đầu tiên.
_MAP_INIT_LOC  = [35.6895, 139.6917]   # Tokyo — không thay đổi
_MAP_INIT_ZOOM = 9
m = folium.Map(
    location=_MAP_INIT_LOC,
    zoom_start=_MAP_INIT_ZOOM,
    tiles=None,
    prefer_canvas=True,
)

# ── Tile layers (chỉ để JS switchTile có thể gọi; không load ngay) ──
_street_layer = folium.TileLayer(
    tiles=_TILE_STR_URL, attr='CartoDB Voyager', name='street', overlay=False
)
_street_layer.add_to(m)

folium.TileLayer(
    tiles='https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
    name='OpenRailwayMap', overlay=True, control=True, opacity=0.25, attr='OpenRailwayMap'
).add_to(m)

# ── Tile switcher control (Satellite / Street) — inject qua MacroElement ──
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

# ── CSS cho tooltip (hover) ────────────────────────────────────────────────────
m.get_root().html.add_child(folium.Element("""
<style>
.leaflet-tooltip {
    background: white !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
    padding: 6px !important;
    max-width: 240px !important;
}
.leaflet-tooltip::before { display: none !important; }
</style>
"""))

# ── LOCATION MARKERS ──────────────────────────────────────────────────────────
import os, base64

def _get_loc_image_b64(loc_name: str):
    """Tìm ảnh theo số thứ tự ở đầu tên địa danh (vd: '23. Hoshinomura...' → tìm images/23.*).
    Trả về (base64_string, mime_type) hoặc (None, None) nếu không tìm thấy."""
    num = loc_name.split(".")[0].strip()
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.isdir(img_dir):
        return None, None
    for ext, mime in [("jpg","image/jpeg"),("jpeg","image/jpeg"),("png","image/png"),("webp","image/webp")]:
        path = os.path.join(img_dir, f"{num}.{ext}")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode(), mime
    return None, None

for loc_name, loc_coords in LOCATION_DATABASE.items():
    is_sel = abs(loc_coords[0]-st.session_state.lat)<0.001 and abs(loc_coords[1]-st.session_state.lon)<0.001
    try:
        loc_num = int(loc_name.split(".")[0].strip())
    except ValueError:
        loc_num = 99
    is_frequent = (loc_num <= 27)
    if is_sel:
        star_color = "#00FFFF" if is_frequent else "#FFD700"
        star_glow  = "drop-shadow(0 0 7px cyan)" if is_frequent else "drop-shadow(0 0 6px gold)"
        star_size  = "22px"
    else:
        star_color = "#22D3EE" if is_frequent else "#FFA500"
        star_glow  = "none"
        star_size  = "16px"
    b64, mime = _get_loc_image_b64(loc_name)
    if b64:
        img_html = (f'<img src="data:{mime};base64,{b64}" '
                    f'style="width:220px;max-height:150px;object-fit:cover;border-radius:6px;'
                    f'display:block;margin-bottom:6px;">')
    else:
        img_html = ""
    tooltip_html = (f'<div style="font-family:sans-serif;font-size:13px;font-weight:600;'
                    f'color:#1e293b;max-width:230px;line-height:1.4;">'
                    f'{img_html}{loc_name}</div>')
    folium.Marker(
        loc_coords,
        icon=folium.DivIcon(
            html=f'<div style="font-size:{star_size};color:{star_color};'
                 f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{star_glow};'
                 f'cursor:pointer;line-height:1;font-family:serif;">★</div>',
            icon_size=(24,24), icon_anchor=(12,12)),
        tooltip=folium.Tooltip(tooltip_html, sticky=False, offset=(20, -10), parse_html=False),
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

# ── st_folium ─────────────────────────────────────────────────────────────────
# "zoom" và "center" trong returned_objects KHÔNG gây rerun tự động —
# st_folium chỉ rerun khi last_clicked / last_object_clicked_tooltip thay đổi.
# Nhưng chúng cho phép đọc view hiện tại của user khi có click,
# để lưu lại và restore sau rerun.
_map_key = "astro_map_main"
_stfolium_kwargs = dict(
    width='stretch', height=600, key=_map_key,
    returned_objects=["last_clicked", "last_object_clicked_tooltip", "zoom", "center"],
    center=st.session_state.map_center,
    zoom=st.session_state.zoom,
)
map_data = st_folium(m, **_stfolium_kwargs)

# ── LPM EXTERNAL LINK ─────────────────────────────────────────────────────────
# URL is used inline in the nav row beside the location selectbox
_lpm_url = (f"https://www.lightpollutionmap.info/"
            f"#zoom=10&lat={st.session_state.lat:.4f}&lon={st.session_state.lon:.4f}"
            f"&layers=B0FFFFFFFFFFFFFFFFFFF")

# ── MAP CLICK HANDLER ─────────────────────────────────────────────────────────
if map_data:
    # Luôn lưu zoom/center hiện tại của user trước khi xử lý click.
    # Đây là giá trị map đang hiển thị — sẽ được restore sau rerun qua
    # center= và zoom= params của st_folium phía trên.
    _cur_center = map_data.get("center")
    _cur_zoom   = map_data.get("zoom")
    if _cur_center and isinstance(_cur_center, (list, dict)):
        if isinstance(_cur_center, dict):
            _cur_center = [_cur_center.get("lat", st.session_state.map_center[0]),
                           _cur_center.get("lng", st.session_state.map_center[1])]
        st.session_state.map_center = _cur_center
    if _cur_zoom is not None:
        st.session_state.zoom = _cur_zoom

    clicked_tip = map_data.get("last_object_clicked_tooltip")
    lc          = map_data.get("last_clicked")

    # ── Priority 1: star marker click (via tooltip) ───────────────────────────
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
                st.session_state._last_tip       = _tip_key
                st.session_state._last_lc        = lc
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.rerun()
        else:
            st.session_state._last_tip = None

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
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._last_tip       = None
                st.rerun()
        else:
            if abs(c_lat - st.session_state.lat) > 0.0001 or abs(c_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat             = c_lat
                st.session_state.lon             = c_lon
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
    source_options = ["JMA", "US (GFS)", "EU (ECMWF)", "🔀 Blend (JMA+ECMWF+GFS)"]
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
    nav1, nav2, nav4, nav3, nav_lpm = st.columns([0.42, 1.20, 0.36, 1.30, 0.26])

    def _go_prev():
        if st.session_state.day_offset > 0:
            st.session_state.day_offset -= 1
            st.session_state.sel_date = date_options[st.session_state.day_offset]

    def _go_next():
        if st.session_state.day_offset < 6:
            st.session_state.day_offset += 1
            st.session_state.sel_date = date_options[st.session_state.day_offset]

    with nav1:
        st.button("⬅️Previous", use_container_width=True, key="btn_prev", on_click=_go_prev)
    with nav2:
        sel_label = st.selectbox("ngay", date_options, index=st.session_state.day_offset,
                                 label_visibility="collapsed",
                                 key="sel_date")
        new_off = date_options.index(sel_label)
        if new_off != st.session_state.day_offset:
            st.session_state.day_offset = new_off
            st.rerun()
    with nav4:
        st.button("Next➡️", use_container_width=True, key="btn_next", on_click=_go_next)
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
                # KHÔNG set map_center / _need_fly → map giữ nguyên view hiện tại
                st.session_state.location_name   = sel_loc
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

        # ── Cloud debug bar: API cloud (rating) vs TCC (compare) ─────────────
        _d        = current_cloud_debug
        _api      = _d.get("total", 0)
        _tcc      = _d.get("tcc",   0)
        _delta    = _tcc - _api
        _delta_s  = f"+{_delta}%" if _delta > 0 else (f"{_delta}%" if _delta < 0 else "±0%")
        _dcol     = "#f97316" if _delta > 15 else ("#60a5fa" if _delta < -5 else "#64748b")
        _hint     = "← mây nhiều tầng / front" if _delta > 15 else ("← mây đơn tầng" if _delta < -5 else "")
        _src_tag  = active_source_label.replace("🔀 ","").split("(")[0].strip()
        st.markdown(f"""
<div style="background:rgba(15,23,42,0.70);border:1px solid #1e3a5f;border-radius:9px;
            padding:8px 13px;margin-bottom:6px;font-size:12px;font-family:'Segoe UI',sans-serif;">
  <div style="color:#475569;font-weight:600;margin-bottom:4px;">
    🧮 CLOUD LAYERS · slot 1 · {_src_tag}
    <span style="font-weight:400;color:#334155;font-size:11px;margin-left:6px;">
      ☁️ rating dùng API cloud · TCC chỉ để so sánh với Himawari
    </span>
  </div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;">
    <span style="color:#64748b;">Low <b style="color:#7dd3fc;">{_d.get('low',0)}%</b></span>
    <span style="color:#64748b;">Mid <b style="color:#93c5fd;">{_d.get('mid',0)}%</b></span>
    <span style="color:#64748b;">High <b style="color:#bae6fd;">{_d.get('high',0)}%</b></span>
    <span style="color:#64748b;border-left:1px solid #1e3a5f;padding-left:10px;">
      API cloud <b style="color:#fbbf24;">{_api}%</b></span>
    <span style="color:#64748b;">
      TCC <b style="color:#a3e635;">{_tcc}%</b></span>
    <span style="color:#64748b;">
      Δ <b style="color:{_dcol};">{_delta_s}</b>
      <span style="color:#374151;font-size:10px;"> {_hint}</span>
    </span>
  </div>
  <div style="margin-top:5px;color:#334155;font-size:10px;">
    📋 Excel: <code style="color:#475569;">DateTime · Low · Mid · High · API_cloud · TCC · Himawari_B13(IR) · Thực_tế</code>
    &nbsp;|&nbsp; Himawari IR band: <a href="https://himawari8.nict.go.jp" target="_blank"
    style="color:#4f6ef7;">himawari8.nict.go.jp</a> → chọn <b>B13/IRC</b> (hoạt động 24/7, kể cả ban đêm)
  </div>
</div>""", unsafe_allow_html=True)

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

# ── MOON + SUN + MILKY WAY ALTITUDE CHART ────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 MOON, SUN & MILKY WAY ALTITUDE")

import plotly.graph_objects as go

# ── Sun brightness: opacity gradient theo Sun altitude ────────────────────────
# Sun > 0°  → cam đậm | Sun 0°~-13° → mờ dần | Sun <= -13° → tắt hẳn (full dark)
def _sun_bright_opacity(sun_alt):
    if sun_alt <= -13:
        return 0.0
    op = (sun_alt + 13) / 23.0 * 0.50   # -13°→0.0, 0°→0.28, +10°→0.50
    return round(min(max(op, 0.0), 0.50), 3)

fig = go.Figure()

# ── Background brightness bands (vrect per slot) ─────────────────────────────
_x_positions = list(range(len(hours_labels)))
for _i, (_lbl, _sa) in enumerate(zip(hours_labels, sun_altitudes)):
    _op = _sun_bright_opacity(_sa)
    if _op > 0.005:
        fig.add_vrect(
            x0=_i - 0.5, x1=_i + 0.5,
            fillcolor="rgba(251,146,60,1.0)",
            opacity=_op,
            layer="below",
            line_width=0,
        )

# ── Moon: filled area ─────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=moon_altitudes,
    mode='lines',
    name='🌙 Moon',
    line=dict(color='#fbbf24', width=2.5),
    fill='tozeroy',
    fillcolor='rgba(251,191,36,0.20)',
    hovertemplate='%{customdata}<br>Moon: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Sun: dashed blue line ─────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=sun_altitudes,
    mode='lines',
    name='☀️ Sun',
    line=dict(color='#38bdf8', width=2.5, dash='dash'),
    hovertemplate='%{customdata}<br>Sun: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Milky Way GC: dashed purple ───────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=milkyway_altitudes,
    mode='lines',
    name='🌌 MW GC',
    line=dict(color='#a78bfa', width=2.0, dash='dot'),
    hovertemplate='%{customdata}<br>MW GC: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Horizon rule ──────────────────────────────────────────────────────────────
fig.add_hline(y=0, line=dict(color='#475569', dash='dot', width=1))

# ── -13° rule ─────────────────────────────────────────────────────────────────
fig.add_hline(y=-13, line=dict(color='rgba(251,146,60,0.50)', dash='dot', width=1),
              annotation_text="−13° full dark", annotation_font_color="rgba(251,146,60,0.7)",
              annotation_position="bottom right")

# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    height=480,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.0)',
    font=dict(color='#94a3b8', size=12),
    xaxis=dict(
        tickmode='array',
        tickvals=_x_positions,
        ticktext=hours_labels,
        gridcolor='rgba(71,85,105,0.3)',
        title='Time 18:00 ~ 06:00',
        title_font_color='#94a3b8',
    ),
    yaxis=dict(
        gridcolor='rgba(71,85,105,0.3)',
        title='Altitude (°)',
        title_font_color='#94a3b8',
        zeroline=False,
    ),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
        font=dict(color='#cbd5e1'),
        bgcolor='rgba(0,0,0,0)',
    ),
    margin=dict(l=50, r=20, t=40, b=40),
    hovermode='x unified',
)

st.plotly_chart(fig, use_container_width=True)

# Legend note
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#94a3b8;margin-top:-8px;'>"
    "<span style='color:#fbbf24;'>▬</span> Moon &nbsp;&nbsp;"
    "<span style='color:#38bdf8;'>╌╌</span> Sun &nbsp;&nbsp;"
    "<span style='color:#a78bfa;'>·····</span> Milky Way GC &nbsp;&nbsp;|&nbsp;&nbsp;"
    "<span style='color:rgba(251,146,60,0.8);'>▓▒░</span> Sky brightness gradient (tắt khi Sun &lt;−13°)</div>",
    unsafe_allow_html=True
)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer-copyright">© Copyright: insta: fcbmkw</div>', unsafe_allow_html=True)
