from application import db
import datetime as dt
from flask import flash

from sqlalchemy.exc import IntegrityError
class Entry(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    accomodates = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    neighborhood = db.Column(db.String(100), nullable=False)
    elevator = db.Column(db.Boolean, nullable=False)
    pool = db.Column(db.Boolean, nullable=False)
    actual_price = db.Column(db.Float, nullable=True)
    link = db.Column(db.String(500), nullable=False)
    prediction = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

def add_entry(entry):
    try:
        db.session.add(entry)
        db.session.commit()
        return entry.id
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
        raise Exception        

def get_history(user_id):
    try:
        return db.session.query(Entry).filter_by(user_id=user_id).all()
    except Exception as error:
        flash(str(error), "danger")
        raise Exception
class User(db.Model):
    __tablename__ = "users"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Email
    email = db.Column(db.String(255), unique=True, nullable=False)

    # Password Hash
    password_hash = db.Column(db.String(64), nullable=False)

    # Created
    created = db.Column(db.DateTime, nullable=False)

    history = db.relationship("Entry", backref="user", lazy=True)

def add_user(new_user):
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user.id
    except IntegrityError:
        db.session.rollback()
        flash("User with same email already exists", "danger")
        raise Exception
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
        raise Exception


