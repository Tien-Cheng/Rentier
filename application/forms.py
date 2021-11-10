from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators

from wtforms import BooleanField, SelectField, SubmitField, PasswordField

from wtforms.fields.html5 import URLField, IntegerField, DecimalField, EmailField
from wtforms.validators import (
    Length,
    InputRequired,
    ValidationError,
    NumberRange,
    Optional,
    URL,
    Email,
    Regexp,
)

password_validator = Regexp(
    "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$",
    message="Password must be at least 8 characters long, have upper and lower case letters, at least one number and one special character",
)


class Prediction(FlaskForm):
    bedrooms = IntegerField(
        "Number of Bedrooms", validators=[InputRequired(), NumberRange(min=0)]
    )

    bathrooms = IntegerField(
        "Number of Bathrooms", validators=[InputRequired(), NumberRange(min=0)]
    )

    accomodates = IntegerField(
        "Accomodates", validators=[InputRequired(), NumberRange(min=0)]
    )

    room_type = SelectField(
        "Room Type",
        validators=[InputRequired()],
        choices=sorted(["Private room", "Entire home/apt", "Shared room"]),
    )

    neighborhood = SelectField(
        "Neighborhood",
        validators=[InputRequired()],
        choices=sorted(
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
        ),
    )

    elevator = BooleanField("Elevator Access?", default=False)

    pool = BooleanField("Pool?", default=False)

    actual_price = DecimalField(
        "Actual Listing Price (Optional)", validators=[Optional(), NumberRange(min=0)]
    )

    link = URLField("Link to Listing (Optional)", validators=[Optional(), URL()])

    submit = SubmitField("Submit")


class Login(FlaskForm):
    email = EmailField("Email address", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            password_validator,
        ],
    )

    remember_me = BooleanField("Remember me?", default=False)

    submit = SubmitField("Submit")


class Register(FlaskForm):
    email = EmailField("Email address", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8), password_validator]
    )

    submit = SubmitField("Submit")