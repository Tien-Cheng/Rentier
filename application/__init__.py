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
from application import routes
