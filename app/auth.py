import secrets
import requests
from flask import (Blueprint, redirect, request, url_for,
                   make_response, render_template, current_app, session)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login_page():
    return render_template("login.html")


@auth_bp.route("/auth/github")
def github_login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    client_id = current_app.config["GITHUB_CLIENT_ID"]
    # Always redirect to backend callback
    backend = current_app.config["BACKEND_URL"]
    redirect_uri = f"{backend}/auth/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=read:user user:email"
        f"&state={state}"
    )


@auth_bp.route("/auth/callback")
def auth_callback():
    # Cookies already set by backend, just go to dashboard
    return redirect(url_for("routes.dashboard"))


@auth_bp.route("/logout")
def logout():
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        backend = current_app.config["BACKEND_URL"]
        requests.post(f"{backend}/auth/logout", json={"refresh_token": refresh_token})

    response = make_response(redirect(url_for("auth.login_page")))
    for cookie in ["access_token", "refresh_token", "username", "role", "avatar_url"]:
        response.delete_cookie(cookie)
    return response
