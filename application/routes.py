from application import app
from flask import render_template
@app.route('/', methods=["GET"])
def index_page():
    return render_template("index.html")