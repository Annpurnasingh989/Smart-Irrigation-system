
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_weather():
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CITY = "Gorakhpur"

    if not API_KEY:
        raise ValueError(
            "OPENWEATHER_API_KEY .env file mein set nahi hai."
        )

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITY}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather = data["weather"][0]["main"]

    print("Temperature:", temperature, "°C")
    print("Humidity:", humidity, "%")
    print("Weather:", weather)

    if weather in ("Rain", "Drizzle", "Thunderstorm"):
        advice = "🌧️ Barish ka mausam hai. Filhaal sinchai rok dein."
    elif temperature >= 35:
        advice = "☀️ Garmi zyada hai. Zarurat ke hisaab se sinchai karein."
    elif humidity >= 80:
        advice = "💧 Hawa mein nami zyada hai. Sinchai se pehle mitti check karein."
    else:
        advice = "✅ Sinchai se pehle mausam aur mitti ki nami check karein."

    return temperature, humidity, weather, advice
