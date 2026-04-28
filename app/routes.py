import requests
from flask import (Blueprint, render_template, request,
                   redirect, url_for, current_app, make_response)
from app.middleware import login_required

routes_bp = Blueprint("routes", __name__)


def _api(method, path, cookies, **kwargs):
    """Make an authenticated request to the backend."""
    backend = current_app.config["BACKEND_URL"]
    access_token = cookies.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-API-Version": "1"
    }
    return getattr(requests, method)(f"{backend}{path}", headers=headers, **kwargs)


def _try_refresh(response_obj):
    """Attempt token refresh and redirect if needed."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None
    backend = current_app.config["BACKEND_URL"]
    resp = requests.post(f"{backend}/auth/refresh", json={"refresh_token": refresh_token})
    if resp.status_code == 200:
        data = resp.json()
        response_obj.set_cookie("access_token", data["access_token"], httponly=True, samesite="Lax")
        response_obj.set_cookie("refresh_token", data["refresh_token"], httponly=True, samesite="Lax")
        return data["access_token"]
    return None


@routes_bp.route("/")
@login_required
def dashboard():
    resp = _api("get", "/api/profiles", request.cookies, params={"limit": 1})

    if resp.status_code == 401:
        return redirect(url_for("auth.login_page"))

    total = resp.json().get("total", 0)

    gender_male = _api("get", "/api/profiles", request.cookies, params={"gender": "male", "limit": 1}).json().get("total", 0)
    gender_female = _api("get", "/api/profiles", request.cookies, params={"gender": "female", "limit": 1}).json().get("total", 0)

    return render_template("dashboard.html",
        total=total,
        male=gender_male,
        female=gender_female,
        username=request.cookies.get("username"),
        avatar_url=request.cookies.get("avatar_url"),
        role=request.cookies.get("role")
    )


@routes_bp.route("/profiles")
@login_required
def profiles():
    params = {k: v for k, v in request.args.items() if v}
    params.setdefault("page", "1")
    params.setdefault("limit", "10")

    resp = _api("get", "/api/profiles", request.cookies, params=params)
    if resp.status_code == 401:
        return redirect(url_for("auth.login_page"))

    data = resp.json()
    return render_template("profiles.html",
        data=data,
        args=request.args,
        username=request.cookies.get("username"),
        role=request.cookies.get("role")
    )


@routes_bp.route("/profiles/<profile_id>")
@login_required
def profile_detail(profile_id):
    resp = _api("get", f"/api/profiles/{profile_id}", request.cookies)
    if resp.status_code == 404:
        return render_template("profile_detail.html", profile=None,
            username=request.cookies.get("username"), role=request.cookies.get("role"))
    if resp.status_code == 401:
        return redirect(url_for("auth.login_page"))

    return render_template("profile_detail.html",
        profile=resp.json().get("data"),
        username=request.cookies.get("username"),
        role=request.cookies.get("role")
    )


@routes_bp.route("/search")
@login_required
def search():
    q = request.args.get("q", "")
    data = None

    if q:
        resp = _api("get", "/api/profiles/search", request.cookies, params={"q": q})
        if resp.status_code == 401:
            return redirect(url_for("auth.login_page"))
        data = resp.json()

    return render_template("search.html",
        q=q,
        data=data,
        username=request.cookies.get("username"),
        role=request.cookies.get("role")
    )


@routes_bp.route("/account")
@login_required
def account():
    return render_template("account.html",
        username=request.cookies.get("username"),
        avatar_url=request.cookies.get("avatar_url"),
        role=request.cookies.get("role")
    )
