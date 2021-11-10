from functools import wraps
from flask import redirect, request, url_for, session


def login_required(func):
    """Decorator to check if user is logged in ."""

    @wraps(func)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:  # Check if user is logged in
            return redirect(url_for("login"), next=request.url)
        return func(*args, **kwargs)

    return decorated_func
