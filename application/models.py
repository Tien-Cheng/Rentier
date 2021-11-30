from application import db, NEIGHBORHOODS, ROOM_TYPES
import datetime as dt
import re
from flask import flash
from sqlalchemy.orm import validates

from sqlalchemy.exc import IntegrityError


class Entry(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    beds = db.Column(db.SmallInteger, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    accomodates = db.Column(db.SmallInteger, nullable=False)
    minimum_nights = db.Column(db.SmallInteger, nullable=False)
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
        # TODO: Consider putting upper bound on parameters
        return beds

    @validates("bathrooms")
    def validate_bathrooms(self, key, bathrooms):
        assert type(bathrooms) in {int, float}, "Bathrooms should be an integer or float"
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
        assert type(wifi) is bool, "data type should be a boolean"
        return wifi

    @validates("elevator")
    def validate_elevator(self, key, elevator):
        assert type(elevator) is bool, "data type should be a boolean"
        return elevator

    @validates("pool")
    def validate_pool(self, key, pool):
        assert type(pool) is bool, "data type should be a boolean"
        return pool

    @validates("neighborhood")
    def validate_neighborhood(self, key, neighborhood):
        assert type(neighborhood) is str, "Data type should be a string"
        assert neighborhood in NEIGHBORHOODS, "Neighborhood should be one of the recognized neighborhoods"
        return neighborhood

    @validates("room_type")
    def validate_room_type(self, key, room_type):
        assert type(room_type) is str, "Data type should be a string"
        assert room_type in ROOM_TYPES, "Room Type should be one of the valid Room Types"
        return room_type
    
    @validates("actual_price")
    def validate_actual_price(self, key, actual_price):
        assert type(actual_price) in {type(None), int, float}, "Either actual price should be None, int or float"
        if actual_price is not None:
            assert actual_price >= 0, "Actual price should be greater than or equal to 0"
        return actual_price

    @validates("prediction")
    def validate_prediction(self, key, prediction):
        assert type(prediction) in {int, float} , "Data type should be a float or int"
        assert prediction > 0, "Prediction should be positive"
        return prediction

    @validates("created")
    def validates_created(self, key, created):
        assert type(created) is dt.datetime, "created should be a datetime object"
        return created
    
def add_entry(entry):
    try:
        db.session.add(entry)
        db.session.commit()
        return entry.id
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
        raise Exception

def delete_entry(entry):
    try:
        db.session.delete(entry)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
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

    @validates("email")
    def validate_email(self, key, email):
        """
        Validate email address. Email address should already have been validated by the Flask Form, but we double check the input here just in case
        """
        assert len(email) <= 255, "Email address should be at most 255 characters long."
        assert re.search(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", email) is not None, "Email address is invalid"
        return email

    @validates("password_hash")
    def validate_hash(self, key, password_hash):
        assert len(password_hash) >= 64, "Password hash should be at least 64 characters long."
        return password_hash

    @validates("created")
    def validates_created(self, key, created):
        assert type(created) is dt.datetime, "created should be a datetime object"
        return created

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
