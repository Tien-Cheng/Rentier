from application import app, db, ai_model, NEIGHBORHOODS, ROOM_TYPES
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
from werkzeug.exceptions import BadRequest, InternalServerError
from application.utils import login_required, API_Error
from datetime import datetime as dt
import pandas as pd

# Create database if does not exist
db.create_all()


@app.errorhandler(Exception)
def error_handler(error):
    if not hasattr(error, "name") or not hasattr(
        error, "code"
    ):  # Handle Generic Errors
        error = InternalServerError
        error.name = "Internal Server Error"
    return (
        render_template("error.html", error=error, title=f"Rentier | {error.name}"),
        error.code,
    )


@app.errorhandler(API_Error)
def api_error_handler(error):
    return jsonify({"message": error.message}), error.status_code


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
    try:
        pred_form = Prediction()
        show_result = False
        results = {}
        if request.method == "POST":
            if not pred_form.validate_on_submit():
                abort(400)
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
            try:
                assert beds >= 0, "Beds must be greater than or equal to zero"
                assert bathrooms >= 0, "Bathrooms must be greater than or equal to zero"
                assert accomodates >= 0, "Accomodates must be greater than zero"
                assert (
                    accomodates >= beds
                ), "Accomodates must be greater than or equal to number of beds"
                assert (
                    minimum_nights >= 0
                ), "MinimumNights must be greater than or equal to zero"
                assert room_type in ROOM_TYPES, "Room type is invalid"
                assert neighborhood in NEIGHBORHOODS, "Neighborhood is invalid"
                assert type(wifi) is bool, "Wifi must be a boolean"
                assert type(elevator) is bool, "Elevator must be a boolean"
                assert type(pool) is bool, "Pool must be a boolean"
                assert type(actual_price) in {
                    type(None),
                    float,
                    int,
                }, "Actual price should be a number or None"
                if actual_price is not None:
                    assert actual_price > 0, "Actual price should be greater than 0"
            except:
                raise BadRequest
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
            difference = None
            if actual_price is not None:
                difference = float(actual_price - result[0])
                results["price_diff"] = abs(difference)
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
                difference=difference,
            )
            add_entry(new_entry)
    except BadRequest:
        flash(f"Input validation failed. Please try again!", "danger")

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
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))
    col_sort = request.args.get("col_sort", "created")
    desc = request.args.get("dir", "desc") == "desc"
    history = get_history(session["user_id"], page, per_page, col_sort, desc)
    return render_template(
        "history.html",
        title="Rentier | History",
        history=history,
        col_sort=col_sort,
        desc=desc,
        per_page=per_page,
    )


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    """
    Delete entry from history
    """
    id = request.form.get("id")
    user_id = session["user_id"]
    result = db.session.query(Entry).filter_by(id=id, user_id=user_id).first()
    if result is None:
        abort(404, description="We could not find this entry in your history")
    else:
        delete_entry(result)
    return redirect(url_for("history"))


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
        except BadRequest:
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
        except BadRequest:
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
    flash("Logged Out", "success")
    return redirect(url_for("index"))


@app.route("/api/users/", methods=["POST"])
def api_add_user():
    """
    Api for adding new users
    """
    try:
        # Get json file posted from client
        data = request.get_json()
        if data is None:
            raise TypeError(
                "Invalid request type. Ensure data is in the form of a json file."
            )
        # Retrieve fields from data
        email = data["email"]
        password_hash = generate_password_hash(data["password"])
        created = dt.utcnow()
        # Create a new entry into user table
        new_user = User(email=email, password_hash=password_hash, created=created)

        # Add entry to user table
        result = add_user(new_user)
    except Exception as e:
        raise API_Error(" ".join(e.args), 400)
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
    if data is None:
        raise TypeError(
            "Invalid request type. Ensure data is in the form of a json file."
        )
    email = data["email"]
    password = data["password"]
    remember_me = data["remember_me"]
    rows = db.session.query(User).filter_by(email=email).all()
    if len(rows) == 0:
        raise API_Error("User not found", 404)
    if not check_password_hash(rows[0].password_hash, password):
        raise API_Error("Wrong password", 403)
    session["user_id"] = rows[0].id
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
@login_required
def api_predict():  # TODO: Implement input validation
    """
    Api for requesting and returning user predictions based on user input
    """
    try:
        data = request.get_json()
        if data is None:
            raise TypeError(
                "Invalid request type. Ensure data is in the form of a json file."
            )
        beds = int(data["beds"])
        bathrooms = float(data["bathrooms"])
        accomodates = int(data["accomodates"])
        minimum_nights = data["minimum_nights"]
        room_type = data["room_type"]
        neighborhood = data["neighborhood"]
        wifi = data["wifi"]
        elevator = data["elevator"]
        pool = data["pool"]
        actual_price = data["actual_price"]
        assert beds >= 0, "Beds must be greater than or equal to zero"
        assert bathrooms >= 0, "Bathrooms must be greater than or equal to zero"
        assert accomodates >= 0, "Accomodates must be greater than zero"
        assert (
            accomodates >= beds
        ), "Accomodates must be greater than or equal to number of beds"
        assert (
            minimum_nights >= 0
        ), "MinimumNights must be greater than or equal to zero"
        assert room_type in ROOM_TYPES, "Room type is invalid"
        assert neighborhood in NEIGHBORHOODS, "Neighborhood is invalid"
        assert type(wifi) is bool, "Wifi must be a boolean"
        assert type(elevator) is bool, "Elevator must be a boolean"
        assert type(pool) is bool, "Pool must be a boolean"
        assert type(actual_price) in {
            type(None),
            float,
            int,
        }, "Actual price should be a number or None"
        if actual_price is not None:
            assert actual_price > 0, "Actual price should be greater than 0"
    except Exception as e:
        raise API_Error(" ".join(e.args), 400)

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
    if actual_price is not None:
        difference = actual_price - result[0]
    else:
        difference = None
    return jsonify({"prediction": result[0], "difference": difference})


@app.route("/api/history/<int:id>", methods=["POST"])
@login_required
def api_add_history(id):
    if session["user_id"] != id:
        raise API_Error("Your user id does not match up with the request.", 403)
    data = request.get_json()
    if data is None:
        raise TypeError(
            "Invalid request type. Ensure data is in the form of a json file."
        )
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
    difference = data["difference"]
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
            difference=difference,
        )
        result = add_entry(new_entry)
    except Exception as e:
        raise API_Error(" ".join(e.args), 400)
    return jsonify({"result": result})


AssertionError()


@app.route("/api/history/<int:id>", methods=["GET"])
@login_required
def api_get_user_history(id):
    if session["user_id"] != id:
        raise API_Error("Your user id does not match up with the request.", 403)
    entries = get_history(id)
    result = [
        {
            "entry_id": entry.id,
            "user_id": entry.user_id,
            "beds": entry.beds,
            "bathrooms": entry.bathrooms,
            "accomodates": entry.accomodates,
            "minimum_nights": entry.minimum_nights,
            "room_type": entry.room_type,
            "neighborhood": entry.neighborhood,
            "wifi": entry.wifi,
            "elevator": entry.elevator,
            "pool": entry.pool,
            "actual_price": entry.actual_price,
            "link": entry.link,
            "prediction": entry.prediction,
            "created": entry.created,
            "difference": entry.difference,
        }
        for entry in entries
    ]
    return jsonify(result)


@app.route("/api/history/<int:user_id>/<int:id>/", methods=["DELETE"])
@login_required
def api_delete_entry(user_id, id):
    if session["user_id"] != user_id:
        raise API_Error("Your user id does not match up with the request.", 403)
    result = db.session.query(Entry).filter_by(id=id, user_id=user_id).first()
    if result is None:
        raise API_Error("Entry could not be found", 404)
    result = delete_entry(result)
    return jsonify({"result": result})
