import streamlit as st
from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime

st.set_page_config(page_title="天气地图（Open-Meteo 示例）", layout="wide")

st.title("实时气温地图 — Open-Meteo + OpenStreetMap")

with st.sidebar:
    st.header("查询 / 控制")
    address = st.text_input("搜索地名（例如: Seoul, Korea）", value="Seoul, Korea")
    if st.button("搜索地址"):
        st.session_state['search_requested'] = True
    st.write("或在地图上点击任意位置以查看该点的当前气温。")

if 'lat' not in st.session_state:
    st.session_state['lat'] = 37.5665
if 'lon' not in st.session_state:
    st.session_state['lon'] = 126.9780
if 'search_requested' not in st.session_state:
    st.session_state['search_requested'] = False

if st.session_state.get('search_requested'):
    geolocator = Nominatim(user_agent="streamlit-weather-app")
    loc = geolocator.geocode(address)
    if loc:
        st.session_state['lat'] = loc.latitude
        st.session_state['lon'] = loc.longitude
    else:
        st.warning("地址解析失败。")
    st.session_state['search_requested'] = False

lat, lon = st.session_state['lat'], st.session_state['lon']

m = folium.Map(location=[lat, lon], zoom_start=10)
folium.Marker([lat, lon], tooltip="当前中心").add_to(m)
map_data = st_folium(m, width=900, height=600)

if map_data and map_data.get("last_clicked"):
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.session_state['lat'], st.session_state['lon'] = lat, lon

params = {
    "latitude": lat,
    "longitude": lon,
    "current_weather": "true",
    "timezone": "auto"
}
r = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
data = r.json()

st.subheader("当前气温")
if "current_weather" in data:
    temp = data["current_weather"]["temperature"]
    time = data["current_weather"]["time"]
    st.metric("温度 (°C)", f"{temp} °C")
    st.write(f"时间：{time}")
else:
    st.error("未能获取气温数据。")
