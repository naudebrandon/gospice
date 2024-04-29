from flask import  render_template, session, redirect
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""

    return render_template("apology.html", message, code)

def zar(value):
    """Format value as ZAR."""
    return f"R {value:,.2f}"

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
