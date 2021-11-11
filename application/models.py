from application import db
import datetime as dt
from flask import flash

from sqlalchemy.exc import IntegrityError


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
