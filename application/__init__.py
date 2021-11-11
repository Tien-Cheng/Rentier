from flask import Flask
# Persistent Storage
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_pyfile("dev_config.cfg")
db = SQLAlchemy(app)
from application import routes
