"""APP-002 browser forms and JSON endpoints use the same prepared guards."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as RequestError

from app import security
from app.schemas import LoginInput, PublicUser, SignupInput

router = APIRouter()


def _api_csrf(request: Request, x_csrf_token: str | None = Header(default=None)):
    """Require the same-origin session token before any API state change."""
    security.require_csrf(request, x_csrf_token)


def _form(request: Request, page: str, error=None, username: str = ""):
    """Render a fresh protected form without ever retaining a password."""
    cookie_response = Response()
    token = security.csrf_token(request, cookie_response)
    response = request.app.state.templates.TemplateResponse(
        request=request,
        name=f"{page}.html",
        context={
            "csrf_token": token,
            "error": error.detail if error else None,
            "username": username,
        },
        status_code=error.status_code if error else 200,
        headers=error.headers if error else None,
    )
    response.raw_headers.extend(
        (name, value)
        for name, value in cookie_response.raw_headers
        if name.lower() == b"set-cookie"
    )
    return response


async def _credentials(request: Request, schema):
    """Check bounded form data and CSRF before using the shared input schema."""
    fields = dict(await request.form(max_files=0, max_fields=4, max_part_size=4096))
    security.require_csrf(request, fields.pop("csrf_token", None))
    try:
        return schema.model_validate(fields)
    except ValidationError as error:
        message = (
            "Use a username with 3–32 letters, numbers or underscores and a "
            "password with 15–128 characters. Only username and password are allowed."
            if schema is SignupInput
            else "Enter a username and password within the form limits."
        )
        raise HTTPException(422, message) from error


@router.get("/api/csrf")
def api_csrf(request: Request, response: Response):
    """Issue the prepared pre-session or current-session synchronizer token."""
    return {"csrf_token": security.csrf_token(request, response)}


@router.post(
    "/api/signup",
    status_code=201,
    response_model=PublicUser,
    dependencies=[Depends(_api_csrf)],
)
def api_signup(request: Request, credentials: SignupInput):
    """Create a member, never accepting a client-supplied role or user ID."""
    security.limit_signup(request)
    return security.signup(
        request.app.state.settings, credentials.username, credentials.password
    )


@router.post("/api/login", response_model=PublicUser, dependencies=[Depends(_api_csrf)])
def api_login(request: Request, response: Response, credentials: LoginInput):
    """Set the prepared HttpOnly session cookie, returning public identity only."""
    return security.login(request, response, credentials.username, credentials.password)


@router.get("/api/me", response_model=PublicUser)
def api_me(request: Request):
    """The private identity API requires a live authenticated server session."""
    return security.require_user(request)


@router.post("/api/logout", dependencies=[Depends(_api_csrf)])
def api_logout(request: Request, response: Response):
    """Revoke on the server before clearing the browser cookie."""
    security.require_user(request)
    security.logout(request, response)
    return {"detail": "Logged out."}


@router.get("/signup", include_in_schema=False)
def signup_form(request: Request):
    """Show the member registration form in the shared automotive design."""
    if security.authenticate(request):
        return RedirectResponse("/dashboard", status_code=303)
    return _form(request, "signup")


@router.post("/signup", include_in_schema=False)
async def signup_submit(request: Request):
    """Use the same validation, creation throttle and hash service as the API."""
    credentials = None
    try:
        credentials = await _credentials(request, SignupInput)
        security.limit_signup(request)
        security.signup(
            request.app.state.settings, credentials.username, credentials.password
        )
    except RequestError as error:
        return _form(
            request, "signup", error, credentials.username if credentials else ""
        )
    return RedirectResponse("/login?registered=1", status_code=303)


@router.get("/login", include_in_schema=False)
def login_form(request: Request):
    """Anonymous visitors can sign in; live members go to their dashboard."""
    if security.authenticate(request):
        return RedirectResponse("/dashboard", status_code=303)
    return _form(request, "login")


@router.post("/login", include_in_schema=False)
async def login_submit(request: Request):
    """Wrong credentials keep only a validated username, not the password."""
    credentials = None
    try:
        credentials = await _credentials(request, LoginInput)
        response = RedirectResponse("/dashboard", status_code=303)
        security.login(request, response, credentials.username, credentials.password)
    except RequestError as error:
        return _form(
            request, "login", error, credentials.username if credentials else ""
        )
    return response


@router.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    """Guard every dashboard request; hiding its navigation is insufficient."""
    user = security.authenticate(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    cookie_response = Response()
    token = security.csrf_token(request, cookie_response)
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": PublicUser.model_validate(user), "csrf_token": token},
    )


@router.post("/logout", include_in_schema=False)
async def logout_submit(request: Request):
    """A protected POST ends the live session and returns to the login page."""
    fields = dict(await request.form(max_files=0, max_fields=1, max_part_size=4096))
    security.require_csrf(request, fields.get("csrf_token"))
    security.require_user(request)
    response = RedirectResponse("/login?logged_out=1", status_code=303)
    security.logout(request, response)
    return response
