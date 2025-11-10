import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime

st.set_page_config(page_title="天气地图（Open-Meteo 示例）", layout="wide")

st.title("实时气温地图 — Open-Meteo + OpenStreetMap")

# ======= Sidebar =======
with st.sidebar:
    st.header("查询 / 控制")
    address = st.text_input("搜索地名（例如: Seoul, Korea）", value="Seoul, Korea")
    if st.button("搜索地址"):
        st.session_state['search_requested'] = True
    st.write("或在地图上点击任意位置以查看该点的当前气温。")
    st.markdown("---")
    st.markdown("数据来源：OpenStreetMap + Open-Meteo（免费，无需 API Key）")

# ======= Session init =======
if 'lat' not in st.session_state:
    st.session_state['lat'] = 37.5665
if 'lon' not in st.session_state:
    st.session_state['lon'] = 126.9780
if 'search_requested' not in st.session_state:
    st.session_state['search_requested'] = False

# ======= Helper: Geocode using Nominatim API =======
def geocode_osm(address):
    """Use OpenStreetMap Nominatim API (via requests)"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "streamlit-weather-demo (openai-chatgpt)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except Exception as e:
        st.error(f"地址解析失败: {e}")
    return None, None

# ======= Handle address search =======
if st.session_state.get('search_requested'):
    lat, lon = geocode_osm(address)
    if lat and lon:
        st.session_state['lat'], st.session_state['lon'] = lat, lon
    else:
        st.warning("未找到该地址，请尝试更精确的搜索。")
    st.session_state['search_requested'] = False

lat = st.session_state['lat']
lon = st.session_state['lon']

# ======= Map UI =======
st.subheader("地图（可拖动，点击任意点以选择位置）")

m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
folium.Marker([lat, lon], tooltip="当前中心位置").add_to(m)
map_data = st_folium(m, width=900, height=600)

if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    lat, lon = clicked.get("lat"), clicked.get("lng")
    st.session_state['lat'], st.session_state['lon'] = lat, lon

st.sidebar.markdown("---")
st.sidebar.write(f"当前选择坐标：\n纬度: {lat:.5f}, 经度: {lon:.5f}")

# ======= Get weather from Open-Meteo =======
params = {
    "latitude": lat,
    "longitude": lon,
    "current_weather": "true",
    "timezone": "auto"
}
try:
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    st.error(f"天气数据请求失败: {e}")
    data = None

# ======= Display weather =======
st.subheader("当前天气 / 气温")

if data and data.get("current_weather"):
    cw = data["current_weather"]
    temp = cw.get("temperature")
    windspeed = cw.get("windspeed")
    time_str = cw.get("time")

    st.metric(label="当前温度 (°C)", value=f"{temp} °C")
    st.write(f"观测时间：{time_str}")
    st.write(f"风速：{windspeed} m/s")

    # Map with popup
    m2 = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
    popup_html = f"<b>温度：</b>{temp} °C<br><b>时间：</b>{time_str}"
    folium.Marker([lat, lon], popup=popup_html, tooltip=f"{temp} °C").add_to(m2)
    st_folium(m2, width=700, height=400)

    # Download JSON
    raw_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("下载天气 JSON", data=raw_bytes, file_name="weather.json", mime="application/json")

else:
    st.info("尚无天气数据，请点击地图或搜索地点后重试。")

st.write("---")
st.caption("提示：点击地图上的任意位置以查看气温，或输入地名搜索。数据来源：Open-Meteo & OpenStreetMap。")
