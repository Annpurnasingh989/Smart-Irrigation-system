from fileinput import filename

from voice import speak
from weather import get_weather
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from database.db import farmers, predictions, db
import joblib
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
from flask import send_from_directory

model = joblib.load("models/irrigation_model.pkl")
encoder = joblib.load("models/crop_encoder.pkl")

leaf_model = load_model("models/leaf_model.keras")

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

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

    total_farmers = farmers.count_documents({})
    total_predictions = predictions.count_documents({})

    data = list(predictions.find())

    if len(data) > 0:
        avg_water = round(
            sum(i["water_required"] for i in data) / len(data), 2
        )
    else:
        avg_water = 0

    return render_template(
        "dashboard.html",
        name=name,
        temperature=temperature,
        humidity=humidity,
        weather=weather,
        advice=advice,
        total_farmers=total_farmers,
        total_predictions=total_predictions,
        avg_water=avg_water
    )

@app.route("/officer")
def officer():

    # Total registered farmers
    total_farmers = farmers.count_documents({})

    # Total irrigation predictions
    total_predictions = predictions.count_documents({})

    # Get all prediction data
    data = list(predictions.find())

    # Average water requirement
    if len(data) > 0:
        avg_water = round(
            sum(
                item.get("water_required", 0)
                for item in data
            ) / len(data),
            2
        )
    else:
        avg_water = 0

    # Unique crops
    crop_names = set()

    for item in data:
        if item.get("crop"):
            crop_names.add(item["crop"])

    total_crops = len(crop_names)

    # Recent predictions
    recent_predictions = list(
        predictions.find().sort("_id", -1).limit(10)
    )
    

    low_humidity_count = sum(
        1 for item in data
        if item.get("humidity", 0) < 40
    )

    irrigation_count = sum(
        1 for item in data
        if item.get("humidity", 0) < 50
    )

    # Crop-wise statistics
    crop_stats = []

    for crop_name in sorted(crop_names):

        crop_data = [
            item for item in data
            if item.get("crop") == crop_name
        ]

        if crop_data:

            crop_avg_water = round(
                sum(
                    item.get("water_required", 0)
                    for item in crop_data
                ) / len(crop_data),
                2
            )

            crop_avg_temp = round(
                sum(
                    item.get("temperature", 0)
                    for item in crop_data
                ) / len(crop_data),
                2
            )

            crop_avg_humidity = round(
                sum(
                    item.get("humidity", 0)
                    for item in crop_data
                ) / len(crop_data),
                2
            )

            crop_stats.append({
                "crop": crop_name,
                "predictions": len(crop_data),
                "avg_water": crop_avg_water,
                "avg_temperature": crop_avg_temp,
                "avg_humidity": crop_avg_humidity
            })

    return render_template(
        "officer.html",
        total_farmers=total_farmers,
        total_predictions=total_predictions,
        total_crops=total_crops,
        avg_water=avg_water,
        recent_predictions=recent_predictions,
        crop_stats=crop_stats,
        low_humidity_count=low_humidity_count,
        irrigation_count=irrigation_count
    )

@app.route("/all_farmers")
def all_farmers():

    # MongoDB se saare farmers
    farmer_data = list(
        farmers.find().sort("_id", -1)
    )

    return render_template(
        "all_farmers.html",
        farmers=farmer_data
    )

@app.route("/research")
def research():
    return render_template("research.html")


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/crop", methods=["POST"])
def crop():

    crop_name = request.form["crop"]

    farmer_name = request.form.get("name", "Farmer")
    farmer_mobile = request.form.get("mobile", "")
    
    temperature, humidity, weather, advice = get_weather()

    crop_encoded = encoder.transform([crop_name])[0]

    prediction = model.predict([[temperature, humidity, crop_encoded]])

    water_required = round(prediction[0], 2)

    predictions.insert_one({
        "farmer_name": farmer_name,
        "farmer_mobile": farmer_mobile,
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
        season=season,
        farmer_name=farmer_name
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

@app.route("/download_pdf")
def download_pdf():

    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors

    data = list(predictions.find())

    pdf_data = [["Crop", "Temperature", "Humidity", "Water Required"]]

    for item in data:
        pdf_data.append([
            item["crop"],
            f'{item["temperature"]} °C',
            f'{item["humidity"]} %',
            f'{item["water_required"]} Liters'
        ])

    pdf = SimpleDocTemplate("prediction_report.pdf")

    table = Table(pdf_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.green),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))

    pdf.build([table])

    return send_file("prediction_report.pdf", as_attachment=True)

@app.route("/history")
def history():

    data = list(db["predictions"].find())

    return render_template("history.html", predictions=data)

@app.route("/leaf", methods=["GET", "POST"])
def leaf():

    if request.method == "POST":

        file = request.files["leaf"]

        filename = secure_filename(file.filename)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(filepath)

        # Image Preprocessing
        img = image.load_img(filepath, target_size=(128, 128))
        img_array = image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Prediction
        prediction = leaf_model.predict(img_array)
        class_index = np.argmax(prediction)
        confidence = round(float(np.max(prediction)) * 100, 2)

        classes = [
            "Potato___Early_blight",
            "Potato___healthy",
            "Potato___Late_blight"
        ]

        disease = classes[class_index]

        if disease == "Potato___healthy":
            result = "🌿 Healthy Leaf"
            treatment = "✅ No disease detected. Continue regular irrigation."
            fertilizer = "🌾 NPK 19:19:19"
            irrigation = "💧 Normal irrigation is sufficient."

        elif disease == "Potato___Early_blight":
            result = "🍂 Early Blight"
            treatment = "🧴 Spray Mancozeb fungicide and remove infected leaves."
            fertilizer = "🌾 Potash + Mancozeb"
            irrigation = "💧 Give light irrigation and avoid overwatering."

        else:
            result = "🍁 Late Blight"
            treatment = "🧪 Spray Metalaxyl fungicide immediately and reduce excess irrigation."
            fertilizer = "🌾 Copper Oxychloride"
            irrigation = "💧 Reduce irrigation until disease is controlled."

        return render_template(
            "leaf.html",
            image=url_for("uploaded_file", filename=filename),
            result=result,
            treatment=treatment,
            fertilizer=fertilizer,
            irrigation=irrigation,
            confidence=confidence
        )

    return render_template("leaf.html")
app.run(debug=True)


