import streamlit as st
import requests

st.set_page_config(page_title="Weather Forecast API", page_icon="☀️", layout="wide")

st.title("☀️ Weather Forecast API")
st.write("Enter a city name to get the current weather forecast using OpenWeatherMap API.")

# User input
city = st.text_input("🌆 Enter city name", placeholder="e.g., London, New York, Tokyo").strip()

# API key (replace with your own key)
API_KEY = "407cc785f57aabaed3706fa1b5436368"

if city:
    st.info("Fetching weather data...")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        weather_desc = data.get("weather", [{}])[0].get("description", "N/A").title()
        icon = data.get("weather", [{}])[0].get("icon", "")
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png" if icon else None

        st.subheader(f"Weather in {name}, {country}")
        if icon_url:
            st.image(icon_url, width=100)
        st.markdown(f"**Temperature:** {temp} °C")
        st.markdown(f"**Humidity:** {humidity}%")
        st.markdown(f"**Wind Speed:** {wind_speed} m/s")
        st.markdown(f"**Condition:** {weather_desc}")
    else:
        st.error("City not found or API error. Please check the city name and your API key.")
