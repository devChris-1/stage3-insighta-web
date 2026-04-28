from functools import wraps
from flask import redirect, url_for, request


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.cookies.get("access_token"):
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated
