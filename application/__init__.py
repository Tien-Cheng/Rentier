from flask import Flask
import os

# Persistent Storage
from flask_sqlalchemy import SQLAlchemy
import joblib

app = Flask(__name__)

if "TESTING" in os.environ:
    app.config.from_envvar("TESTING")
    print("Using config for TESTING")
elif "DEVELOPMENT" in os.environ:
    app.config.from_envvar("DEVELOPMENT")
    print("Using config for DEVELOPMENT")

db = SQLAlchemy(app)
model_path = "./application/static/ai_model_2.joblib"
ai_model = joblib.load(model_path)

NEIGHBORHOODS = sorted(
    [
        "Bukit Timah",
        "Tampines",
        "Bukit Merah",
        "Queenstown",
        "Newton",
        "Geylang",
        "River Valley",
        "Serangoon",
        "Jurong West",
        "Rochor",
        "Downtown Core",
        "Marine Parade",
        "Outram",
        "Bedok",
        "Kallang",
        "Novena",
        "Tanglin",
        "Pasir Ris",
        "Ang Mo Kio",
        "Bukit Batok",
        "Choa Chu Kang",
        "Hougang",
        "Woodlands",
        "Singapore River",
        "Jurong East",
        "Orchard",
        "Museum",
        "Toa Payoh",
        "Bukit Panjang",
        "Sembawang",
        "Bishan",
        "Yishun",
        "Sengkang",
        "Punggol",
        "Clementi",
        "Mandai",
        "Western Water Catchment",
        "Southern Islands",
        "Tuas",
        "Sungei Kadut",
        "Pioneer",
        "Central Water Catchment",
        "Marina South",
        "Lim Chu Kang",
    ]
)


ROOM_TYPES = set(sorted(["Private room", "Entire home/apt", "Shared room"]))

from application import routes
