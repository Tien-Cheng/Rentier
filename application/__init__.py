from flask import Flask
# Persistent Storage
from flask_sqlalchemy import SQLAlchemy
import joblib
app = Flask(__name__)
app.config.from_pyfile("dev_config.cfg")
db = SQLAlchemy(app)
model_path = "./application/static/ai_model_2.joblib"
ai_model = joblib.load(model_path)
from application import routes
