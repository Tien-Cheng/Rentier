from application import app
from flask import render_template, request, flash, redirect, abort, session, url_for
from application.forms import Prediction, Login, Register
@app.route('/', methods=["GET"])
def index():
    return render_template("index.html", title="Rentier")

@app.route('/predict', methods=["GET", "POST"])
def predict():
    pred_form = Prediction()
    show_result = False
    if request.method == "POST":
        if pred_form.validate_on_submit():
            flash(f"Prediction:", "primary")
            show_result = True
        else:
            flash(f"Prediction failed", "danger")
    return render_template("predict.html", form=pred_form, title="Rentier | Make a Prediction", results=show_result)

@app.route('/login', methods=["GET", "POST"])
def login():
    loginForm = Login()
    if request.method == "POST":
        if loginForm.validate_on_submit():
            # Check that password is correct and that user matches
            flash(f"Logged In", "success")
            return redirect(url_for("index"))
        else:
            flash(f"Failed to Log In", "danger")
    return render_template("login.html", form=loginForm,title="Rentier | Login")

@app.route('/register', methods=["GET", "POST"])
def register():
    registerForm = Register()
    if request.method == "POST":
        if registerForm.validate_on_submit():
            flash(f"Account Registered. Please Log In.", "success")
            return redirect(url_for("login"))
        else:
            flash("Failed to register account.", "danger")

    return render_template("register.html", form=registerForm, title="Rentier | Sign Up")


@app.route('/logout', methods=["POST"])
def logout():
    # remove user from session
    session.pop('user_id', None)
    flash("Logged Out", "warning")
    return redirect(url_for("index"))

