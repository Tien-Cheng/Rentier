from application import app, db, ai_model
from application.models import User, add_user, Entry, add_entry, get_history
from flask import render_template, request, flash, redirect, abort, session, url_for
from application.forms import Prediction, Login, Register
from werkzeug.security import check_password_hash, generate_password_hash
from application.utils import login_required
from datetime import datetime
import pandas as pd
# Create database if does not exist
db.create_all()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Rentier")


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    pred_form = Prediction()
    show_result = False
    results = {}
    if request.method == "POST":
        if pred_form.validate_on_submit():
            beds = pred_form.beds.data
            bathrooms = pred_form.bathrooms.data
            accomodates = pred_form.accomodates.data
            minimum_nights = pred_form.minimum_nights.data
            room_type = pred_form.room_type.data
            neighborhood = pred_form.neighborhood.data
            wifi = int(pred_form.wifi.data)
            elevator = int(pred_form.elevator.data)
            pool = int(pred_form.pool.data)
            actual_price = pred_form.actual_price.data
            link = pred_form.link.data # store link for history
            entry_params = pd.DataFrame(
                {
                    "beds": [beds],
                    "bathrooms_cleaned" : [bathrooms],
                    "accommodates" : [accomodates],
                    "minimum_nights" : [minimum_nights],
                    "room_type" : [room_type],
                    "neighbourhood_cleansed" : [neighborhood],
                    "wifi" : [wifi],
                    "elevator" : [elevator],
                    "pool" : [pool],
                }
            )
            result = ai_model.predict(entry_params)
            show_result = True
            results = {
                "price" : result[0],
                "actual_price" : actual_price
            }
            if actual_price is not None:
                results["price_diff"] = abs(actual_price - result[0])
                results["same"] = results["price_diff"] < 0.05 # account for floating point inprecision
            new_entry = Entry(
                beds = beds,
                bathrooms = bathrooms,
                accomodates = accomodates,
                minimum_nights = minimum_nights,
                room_type = room_type,
                neighborhood = neighborhood,
                wifi = wifi,
                elevator = elevator,
                pool = pool,
                actual_price = actual_price,
                link = link,
                prediction = result[0],
                created = datetime.utcnow(),
                user_id = session["user_id"]
            )
            try:
                add_entry(new_entry)
            except Exception as error:
                flash(f"Failed to add entry to history. Error: {error}", "danger")
        else:
            flash(f"Prediction failed", "danger")
    return render_template(
        "predict.html",
        form=pred_form,
        title="Rentier | Make a Prediction",
        results=show_result,
        **results
    )


@app.route("/history", methods=["GET"])
@login_required
def history():
    history = get_history(session["user_id"])
    return render_template("history.html", title="Rentier | History", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    loginForm = Login()
    if request.method == "POST":
        try:
            if not loginForm.validate_on_submit():
                raise Exception
            email = loginForm.email.data
            password = loginForm.password.data
            remember = loginForm.remember_me.data
            rows = db.session.query(User).filter_by(email = email).all()
            if len(rows) == 0:
                flash("User does not exist", "danger")
                raise Exception
            if not check_password_hash(rows[0].password_hash, password):
                flash("Password is incorrect!", "danger")
                raise Exception
            session["user_id"] = rows[0].id
            flash(f"Logged In", "success")
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            if 'next' in session: # redirect user back to original url if there was one
                url = session['next']
                return redirect(url)
            return redirect(url_for("index"))
        except:
            flash(f"Failed to Log In", "danger")
    return render_template("login.html", form=loginForm, title="Rentier | Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    registerForm = Register()
    if request.method == "POST":
        try:
            if not registerForm.validate_on_submit():
                raise Exception
            email = registerForm.email.data
            password_hash = generate_password_hash(registerForm.password.data)
            new_user = User(
                email=email,
                password_hash=password_hash,
                created = datetime.utcnow()
            )
            add_user(new_user)
            flash(f"Account Registered. Please Log In.", "success")
            return redirect(url_for("login"))
        except:
            flash("Failed to register account.", "danger")

    return render_template(
        "register.html", form=registerForm, title="Rentier | Sign Up"
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    # remove user from session
    session.pop("user_id", None)
    flash("Logged Out", "warning")
    return redirect(url_for("index"))
