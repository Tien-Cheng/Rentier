from application import app, db
from application.models import User, add_user
from flask import render_template, request, flash, redirect, abort, session, url_for
from application.forms import Prediction, Login, Register
from werkzeug.security import check_password_hash, generate_password_hash
from application.utils import login_required
from datetime import datetime
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
    if request.method == "POST":
        if pred_form.validate_on_submit():
            flash(f"Prediction:", "primary")
            show_result = True
        else:
            flash(f"Prediction failed", "danger")
    return render_template(
        "predict.html",
        form=pred_form,
        title="Rentier | Make a Prediction",
        results=show_result,
    )


@app.route("/history", methods=["GET"])
@login_required
def history():
    return render_template("history.html", title="Rentier | History")


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
    session.pop("logged_in", None)
    flash("Logged Out", "warning")
    return redirect(url_for("index"))
