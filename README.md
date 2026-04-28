````markdown
# Insighta Labs+ — Web Portal

A simple, functional web interface for non-technical users to explore demographic data.
Built with Flask + Jinja2 templates. Communicates with the Insighta Labs+ backend API.

---

## System Architecture

```
insighta-web/
├── app/
│   ├── __init__.py      ← app factory, CSRF setup
│   ├── auth.py          ← GitHub OAuth, cookie management
│   ├── routes.py        ← page routes, backend API calls
│   ├── middleware.py    ← login_required decorator
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── profiles.html
│       ├── profile_detail.html
│       ├── search.html
│       └── account.html
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

The web portal is a thin client — it holds no business logic.
Every data operation is delegated to the backend API.

```
Browser
   │
   ▼
Web Portal (Flask, port 3000)
   │
   │  Forwards all data requests with auth headers
   ▼
Backend API (Flask, port 5000)
   │
   ▼
SQLite Database
```

---

## Authentication Flow

```
User visits any protected page
         │
    No access_token cookie → redirect to /login
         │
         ▼
User clicks "Continue with GitHub"
         │
         ▼
GET /auth/github
         │
    Redirects to GitHub OAuth page
         │
         ▼
User authenticates on GitHub
         │
    GitHub redirects to backend:
    http://localhost:5000/auth/github/callback?code=xxx
         │
         ▼
Backend processes callback:
    - Exchanges code for GitHub token
    - Creates or updates user
    - Issues access token + refresh token
    - Sets HTTP-only cookies
    - Redirects browser to web portal /auth/callback
         │
         ▼
Web portal /auth/callback
         │
    Cookies already set → redirect to /dashboard
         │
         ▼
User is now logged in
```

### Why HTTP-Only Cookies

Tokens are stored in HTTP-only cookies, meaning:

- JavaScript cannot read them (`document.cookie` returns nothing)
- They are automatically sent with every request by the browser
- Protected against XSS attacks

### CSRF Protection

All forms are protected by Flask-WTF CSRF tokens.
Every state-changing request includes a hidden CSRF token that the server validates.

---

## Token Handling Approach

| Token         | Storage          | Expiry    |
| ------------- | ---------------- | --------- |
| Access token  | HTTP-only cookie | 3 minutes |
| Refresh token | HTTP-only cookie | 5 minutes |

When the backend returns `401 Unauthorized`, the web portal attempts to refresh the token pair by calling `POST /auth/refresh` with the refresh token cookie. If refresh fails, the user is redirected to the login page and all cookies are cleared.

---

## Role Enforcement Logic

Role enforcement happens entirely on the backend.
The web portal reads the `role` cookie only for display purposes (e.g. showing/hiding the create profile button).

| Role      | What they see                                   |
| --------- | ----------------------------------------------- |
| `analyst` | Dashboard, Profiles list, Search, Account       |
| `admin`   | Everything analyst sees + Create Profile button |

If an analyst tries to access an admin endpoint directly, the backend returns `403 Forbidden`.

---

## Pages

| Route            | Page                       | Auth Required |
| ---------------- | -------------------------- | ------------- |
| `/login`         | Login with GitHub          | No            |
| `/`              | Dashboard (stats)          | Yes           |
| `/profiles`      | Profiles list with filters | Yes           |
| `/profiles/<id>` | Profile detail view        | Yes           |
| `/search`        | Natural language search    | Yes           |
| `/account`       | Account info + logout      | Yes           |

---

## Natural Language Parsing Approach

The search page sends the raw query string to the backend:

```
GET /api/profiles/search?q=young females from nigeria
```

The backend's rule-based parser handles all interpretation.
The web portal simply displays the results — it does no parsing itself.

See the [backend README](https://github.com/DevChris-1/insighta-backend) for full parsing documentation.

---

## Environment Variables

Create a `.env` file in the project root:

```env
BACKEND_URL=http://localhost:5000
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:5000/auth/github/callback
SECRET_KEY=your_random_secret_key
```

---

## Running Locally

```bash
pip install -r requirements.txt
python run.py
```

Web portal starts at `http://localhost:3000`

> Make sure the backend is running at `http://localhost:5000` before starting the web portal.

---

## Running Tests

```bash
pytest tests/ -v
```
````
