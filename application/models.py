from application import db
import datetime as dt
from flask import flash
from sqlalchemy.orm import validates

from sqlalchemy.exc import IntegrityError


class Entry(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    beds = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    accomodates = db.Column(db.Integer, nullable=False)
    minimum_nights = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    neighborhood = db.Column(db.String(100), nullable=False)
    wifi = db.Column(db.Boolean, nullable=False)
    elevator = db.Column(db.Boolean, nullable=False)
    pool = db.Column(db.Boolean, nullable=False)
    actual_price = db.Column(db.Float, nullable=True)
    link = db.Column(db.String(500), nullable=False)
    prediction = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    @validates("beds")
    def validate_beds(self, key, beds):
        assert type(beds) is int, "Beds should be an integer"
        assert (
            beds >= 0
        ), "Beds should be greater than or equal to 0 (some AirBNB listings have no beds)"
        return beds

    @validates("bathrooms")
    def validate_bathrooms(self, key, bathrooms):
        assert bathrooms >= 0, "Bathrooms should be greater than or equal to 0"
        return bathrooms

    @validates("accomodates")
    def validate_accomodates(self, key, accomodates):
        assert type(accomodates) is int, "Accomodates should be an integer"
        assert accomodates > 0, "A room should accomodate at least one"
        return accomodates

    @validates("minimum_nights")
    def validate_minimum_nights(self, key, minimum_nights):
        assert (
            type(minimum_nights) is int
        ), "Minimum number of lights should be an integer"
        assert minimum_nights >= 0, "Minimum number of lights should not be negative"
        return minimum_nights


    @validates("wifi")
    def validate_wifi(self, key, wifi):
        assert type(wifi) is int, "Data type should be a int"
        assert wifi in {1, 0}, "Wifi should be 1 or 0"
        return wifi

    @validates("elevator")
    def validate_elevator(self, key, elevator):
        assert type(elevator) is int, "Data type should be a int"
        assert elevator in {1, 0}, "Elevator should be 1 or 0"
        return elevator

    @validates("pool")
    def validate_pool(self, key, pool):
        assert type(pool) is int, "Data type should be a int"
        assert pool in {1, 0}, "Pool should be 1 or 0"
        return pool

    @validates("neighborhood")
    def validate_neighborhood(self, key, neighborhood):
        assert type(neighborhood) is str, "Data type should be a string"
        return neighborhood

    @validates("room_type")
    def validate_room_type(self, key, room_type):
        assert type(room_type) is str, "Data type should be a string"
        return room_type
    
    @validates("actual_price")
    def validate_actual_price(self, key, actual_price):
        assert actual_price is None or type(actual_price) is float, "Either actual price should be None or float"
        if actual_price is not None:
            assert actual_price >= 0, "Actual price should be greater than or equal to 0"
        return actual_price

    @validates("prediction")
    def validate_prediction(self, key, prediction):
        assert prediction > 0, "Prediction should be positive"
        return prediction

    
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
