import requests
def get_weather():

    API_KEY = "b700eb7adaa636b86907b6c58538894c"

    CITY = "Gorakhpur"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    data = response.json()

    temperature = data["main"]["temp"]

    humidity = data["main"]["humidity"]

    weather = data["weather"][0]["main"]

    print("Temperature :", temperature, "°C")

    print("Humidity :", humidity, "%")

    print("Weather :", weather)

    if weather == "Rain":
        advice = "🌧️ Aaj sinchai mat kijiye. Barish ho rahi hai."

    elif temperature >= 35:
        advice = "☀️ Shaam 6 baje 30 minute sinchai kijiye."

    elif humidity >= 80:
        advice = "💧 Mitti me nami zyada hai. Sinchai ki zarurat nahi hai."

    else:
        advice = "✅ Aaj 20-30 minute sinchai kar sakte hain."

    return temperature, humidity, weather, advice