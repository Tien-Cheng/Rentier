from application import app, db, ai_model
from application.models import (
    User,
    add_user,
    Entry,
    add_entry,
    get_history,
    delete_entry,
)
from flask import (
    render_template,
    request,
    flash,
    redirect,
    abort,
    session,
    url_for,
    jsonify,
)
from application.forms import Prediction, Login, Register
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
from application.utils import login_required
from datetime import datetime as dt
import pandas as pd

# Create database if does not exist
db.create_all()

@app.errorhandler(HTTPException)
def http_error_handler(error):
    return render_template("error.html", error=error)

@app.route("/", methods=["GET"])
def index():
    """
    Returns the home page of the application.
    """
    return render_template("index.html", title="Rentier")


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    """
    Show prediction form page, and handle recieving, predicting and recording down data
    """
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
            wifi = pred_form.wifi.data
            elevator = pred_form.elevator.data
            pool = pred_form.pool.data
            actual_price = pred_form.actual_price.data
            link = pred_form.link.data  # store link for history
            entry_params = pd.DataFrame(
                {
                    "beds": [beds],
                    "bathrooms_cleaned": [bathrooms],
                    "accommodates": [accomodates],
                    "minimum_nights": [minimum_nights],
                    "room_type": [room_type],
                    "neighbourhood_cleansed": [neighborhood],
                    "wifi": [wifi],
                    "elevator": [elevator],
                    "pool": [pool],
                }
            )
            result = ai_model.predict(entry_params)
            show_result = True
            results = {"price": result[0], "actual_price": actual_price}
            if actual_price is not None:
                results["price_diff"] = abs(actual_price - result[0])
                results["same"] = (
                    results["price_diff"] < 0.05
                )  # account for floating point inprecision
            new_entry = Entry(
                beds=beds,
                bathrooms=bathrooms,
                accomodates=accomodates,
                minimum_nights=minimum_nights,
                room_type=room_type,
                neighborhood=neighborhood,
                wifi=wifi,
                elevator=elevator,
                pool=pool,
                actual_price=actual_price,
                link=link,
                prediction=float(result[0]),
                created=dt.utcnow(),
                user_id=session["user_id"],
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
        **results,
    )


@app.route("/history", methods=["GET"])
@login_required
def history():
    """
    Return history page, containing the specific history of a user
    """
    history = get_history(session["user_id"])
    return render_template("history.html", title="Rentier | History", history=history)


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    """
    Delete entry from history
    """
    try:
        id = request.form.get("id")
        user_id = session["user_id"]
        result = db.session.query(Entry).filter_by(id=id, user_id=user_id).first()
        if result is None:
            flash("User does not have permission to delete this entry", "danger")
            abort(403)
        delete_entry(result)
        return redirect(url_for("history"))
    except Exception as error:
        flash(str(error), "danger")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Return login page and handle login functionalithy
    """
    loginForm = Login()
    if request.method == "POST":
        try:
            if not loginForm.validate_on_submit():
                abort(400)
            email = loginForm.email.data
            password = loginForm.password.data
            remember = loginForm.remember_me.data
            rows = db.session.query(User).filter_by(email=email).all()
            if len(rows) == 0:
                flash("User does not exist", "danger")
                abort(400)
            if not check_password_hash(rows[0].password_hash, password):
                flash("Password is incorrect!", "danger")
                abort(400)
            session["user_id"] = rows[0].id
            flash(f"Logged In", "success")
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            if "next" in session:  # redirect user back to original url if there was one
                url = session["next"]
                return redirect(url)
            return redirect(url_for("index"))
        except:
            flash(f"Failed to Log In", "danger")
    return render_template("login.html", form=loginForm, title="Rentier | Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle creation of accounts
    """
    registerForm = Register()
    if request.method == "POST":
        try:
            if not registerForm.validate_on_submit():
                abort(400)
            email = registerForm.email.data
            password_hash = generate_password_hash(registerForm.password.data)
            new_user = User(
                email=email, password_hash=password_hash, created=dt.utcnow()
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
    """
    Logout current user from session
    """
    # remove user from session
    session.pop("user_id", None)
    flash("Logged Out", "warning")
    return redirect(url_for("index"))


@app.route("/api/users/", methods=["POST"])
def api_add_user():
    """
    Api for adding new users
    """
    # Get json file posted from client
    data = request.get_json()

    # Retrieve fields from data
    email = data["email"]
    password_hash = generate_password_hash(data["password"])
    created = dt.utcnow()
    # Create a new entry into user table
    new_user = User(email=email, password_hash=password_hash, created=created)

    # Add entry to user table
    result = add_user(new_user)

    return jsonify(
        {
            "id": result,
            "email": email,
            "password_hash": password_hash,
            "created": created,
        }
    )


@app.route("/api/login", methods=["POST"])
def api_login_user():
    """
    Api for logging in new user
    """
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    remember_me = data["remember_me"]
    rows = db.session.query(User).filter_by(email=email).all()
    if len(rows) == 0:
        abort(400)
    if not check_password_hash(rows[0].password_hash, password):
        abort(400)
    session["user_id"] = rows[0].id
    flash(f"Logged In", "success")
    if remember_me:
        session.permanent = True
    else:
        session.permanent = False

    return jsonify(
        {
            "id": rows[0].id,
            "email": email,
            "password": password,
            "remember_me": remember_me,
        }
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():  # TODO: Implement input validation
    """
    Api for requesting and returning user predictions based on user input
    """
    data = request.get_json()
    beds = data["beds"]
    bathrooms = data["bathrooms"]
    accomodates = data["accomodates"]
    minimum_nights = data["minimum_nights"]
    room_type = data["room_type"]
    neighborhood = data["neighborhood"]
    wifi = data["wifi"]
    elevator = data["elevator"]
    pool = data["pool"]
    X = pd.DataFrame(
        {
            "beds": [beds],
            "bathrooms_cleaned": [bathrooms],
            "accommodates": [accomodates],
            "minimum_nights": [minimum_nights],
            "room_type": [room_type],
            "neighbourhood_cleansed": [neighborhood],
            "wifi": [wifi],
            "elevator": [elevator],
            "pool": [pool],
        }
    )
    result = ai_model.predict(X)
    return jsonify({"prediction": result[0]})


@app.route("/api/history/<id>", methods=["POST"])
def api_add_history(id):
    data = request.get_json()
    beds = data["beds"]
    bathrooms = data["bathrooms"]
    accomodates = data["accomodates"]
    minimum_nights = data["minimum_nights"]
    room_type = data["room_type"]
    neighborhood = data["neighborhood"]
    wifi = data["wifi"]
    elevator = data["elevator"]
    pool = data["pool"]
    actual_price = data["actual_price"]
    link = data["link"]
    prediction = data["prediction"]
    try:
        new_entry = Entry(
            beds=beds,
            bathrooms=bathrooms,
            accomodates=accomodates,
            minimum_nights=minimum_nights,
            room_type=room_type,
            neighborhood=neighborhood,
            wifi=wifi,
            elevator=elevator,
            pool=pool,
            actual_price=actual_price,
            link=link,
            prediction=float(prediction),
            created=dt.utcnow(),
            user_id=id,
        )

        result = add_entry(new_entry)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": str(e)})


@app.route('/api/history/<id>', methods=["GET"])
def api_get_user_history(id):
    entries = get_history(id)
    result = [
        {
           "user_id" : entry.user_id,
           "beds" : entry.beds,
           "bathrooms" : entry.bathrooms,
           "accomodates" : entry.accomodates,
           "minimum_nights" : entry.minimum_nights,
           "room_type" : entry.room_type,
           "neighborhood" : entry.neighborhood,
           "wifi" : entry.wifi,
           "elevator" : entry.elevator,
           "pool" : entry.pool,
           "actual_price" : entry.actual_price,
           "link" : entry.link,
           "prediction" : entry.prediction,
           "created" : entry.created
        } for entry in entries
    ]
    return jsonify(result)
    
@app.route('/api/history/<user_id>/<id>/', methods=["DELETE"])
def api_delete_entry(user_id, id):
    result = db.session.query(Entry).filter_by(id=id, user_id=user_id).first()
    if result is None:
        abort(403)
    result = delete_entry(result)
    return jsonify({
        "result" : result
    })