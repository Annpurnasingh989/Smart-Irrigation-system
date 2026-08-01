from voice import speak
from weather import get_weather
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from database.db import farmers, predictions, db
import joblib

model = joblib.load("models/irrigation_model.pkl")
encoder = joblib.load("models/crop_encoder.pkl")

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/save_farmer", methods=["POST"])
def save_farmer():

    name = request.form["name"]

    mobile = request.form["mobile"]

    farmers.insert_one({

        "name": name,

        "mobile": mobile

    })

    return redirect(url_for("dashboard", name=name))

@app.route("/dashboard")
def dashboard():

    name = request.args.get("name", "Farmer")

    temperature, humidity, weather, advice = get_weather()

    return render_template(
        "dashboard.html",
        name=name,
        temperature=temperature,
        humidity=humidity,
        weather=weather,
        advice=advice
    )

@app.route("/crop", methods=["POST"])
def crop():

    crop_name = request.form["crop"]
    
    temperature, humidity, weather, advice = get_weather()

    # Crop Encoding
    crop_encoded = encoder.transform([crop_name])[0]

    # ML Prediction
    prediction = model.predict([[temperature, humidity, crop_encoded]])

    water_required = round(prediction[0], 2)

    predictions.insert_one({
        "crop": crop_name,
        "temperature": temperature,
        "humidity": humidity,
        "water_required": water_required
    })

    if crop_name == "Wheat":
        fertilizer = "Urea"
        irrigation = f"{water_required} Liters"
        season = "Winter"

    elif crop_name == "Rice":
        fertilizer = "DAP"
        irrigation = f"{water_required} Liters"
        season = "Monsoon"

    elif crop_name == "Maize":
        fertilizer = "NPK"
        irrigation = f"{water_required} Liters"
        season = "Summer"

    else:
        fertilizer = "Potash"
        irrigation = f"{water_required} Liters"
        season = "Winter"

    return render_template(
        "crop.html",
        crop=crop_name,
        fertilizer=fertilizer,
        irrigation=irrigation,
        season=season
    )

@app.route("/speak")
def speak_route():
    from voice import speak

    message = "Namaste Kisan Bhai! Aaj 20 se 30 minute sinchai kar sakte hain."

    speak(message)

    return redirect(url_for("dashboard"))

@app.route("/weather")
def weather_page():
    temperature, humidity, weather, advice = get_weather()

    return f"""
    <h2>🌦️ Live Weather Report</h2>

    <p><b>Temperature:</b> {temperature} °C</p>

    <p><b>Humidity:</b> {humidity} %</p>

    <p><b>Weather:</b> {weather}</p>

    <p><b>AI Advice:</b> {advice}</p>

    <br>

    <a href='/dashboard'>⬅ Back</a>
    """
@app.route("/graph")
def graph():

    import matplotlib.pyplot as plt

    data = list(predictions.find())

    crops = [i["crop"] for i in data]
    water = [i["water_required"] for i in data]

    plt.figure(figsize=(6,4))
    plt.bar(crops, water)

    plt.title("Water Requirement")
    plt.xlabel("Crop")
    plt.ylabel("Water (Liters)")

    plt.savefig("static/graph.png")
    plt.close()

    return render_template("graph.html")

@app.route("/history")
def history():

    data = list(db["predictions"].find())

    return render_template("history.html", predictions=data)
app.run(debug=True)