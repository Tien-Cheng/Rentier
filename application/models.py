from application import db
import datetime as dt

class User(db.Model):
    __tablename__ = 'users'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Email
    email = db.Column(db.String(255), unique=True, nullable=False)

    # Password Hash
    password_hash = db.Column(db.String(64), nullable=False)

    # Created
    created = db.Column(db.DateTime, nullable=False)