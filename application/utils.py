from functools import wraps
from flask import redirect, request, url_for, session, flash


def login_required(func):
    """Flask decorator to check if a user is logged in, else, redirect them to login page, which will direct them back to the original page once logged in. Checks if the secured session cookie contains a user id.

    Args:
        func (Callable): Function to be decorated (usually an endpoint)

    Returns:
        [Callable]: Decorated function, which will first check if a user is logged in
    """

    @wraps(func)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:  # Check if user is logged in
            flash("Please login first!", "warning")
            session["next"] = request.url
            return redirect(url_for("login"), 303) # 303: See Other
        return func(*args, **kwargs)

    return decorated_func
