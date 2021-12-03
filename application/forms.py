from flask_wtf import FlaskForm
from application import NEIGHBORHOODS, ROOM_TYPES
from wtforms import BooleanField, SelectField, SubmitField, PasswordField, FloatField, IntegerField

from wtforms.fields.html5 import URLField, EmailField
from wtforms.validators import (
    Length,
    InputRequired,
    NumberRange,
    Optional,
    URL,
    Email,
    Regexp,
    EqualTo,
    ValidationError
)

password_validator = Regexp(
    "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$",
    message="Password must be at least 8 characters long, have upper and lower case letters, at least one number and one special character",
)


class Prediction(FlaskForm):
    beds = IntegerField(
        "Number of Beds", validators=[InputRequired(), NumberRange(min=0)]
    )

    bathrooms = FloatField(
        "Number of Bathrooms", validators=[InputRequired(), NumberRange(min=0)]
    )

    accomodates = IntegerField(
        "Accomodates", validators=[InputRequired(), NumberRange(min=0)]
    )

    minimum_nights = IntegerField(
        "Minimum Nights", validators=[InputRequired(), NumberRange(min=0)]
    )

    room_type = SelectField(
        "Room Type",
        validators=[InputRequired()],
        choices=ROOM_TYPES,
    )

    neighborhood = SelectField(
        "Neighborhood",
        validators=[InputRequired()],
        choices=NEIGHBORHOODS,
    )

    wifi = BooleanField("Wifi", default=True)
    elevator = BooleanField("Elevator Access?", default=False)

    pool = BooleanField("Pool?", default=False)

    actual_price = FloatField(
        "Actual Listing Price (Optional)", validators=[Optional(), NumberRange(min=0)]
    )

    link = URLField("Link to Listing (Optional)", validators=[Optional(), URL()])

    submit = SubmitField("Submit")

    def validate_accomodates(form, field):
        if field.data < form.beds.data:
            raise ValidationError("Accomodates should be greater than or equal to the number of beds")

class Login(FlaskForm):
    email = EmailField("Email address", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
        ],
    )

    remember_me = BooleanField("Remember me?", validators=[Optional()],default=False)

    submit = SubmitField("Submit")


class Register(FlaskForm):
    email = EmailField("Email address", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8), password_validator, EqualTo("confirm", "Passwords must match")]
    )

    confirm = PasswordField("Confirm password")

    submit = SubmitField("Submit")
