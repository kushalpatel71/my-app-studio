"""APP-003 authorization uses current server-side roles on every request."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import security
from app.schemas import PublicUser

router = APIRouter()


@router.get("/api/admin")
def admin_api(request: Request):
    """Return a minimal confirmation only after the prepared admin check passes."""
    user = security.require_admin(request)
    return {
        "detail": "Admin access confirmed.",
        "user": PublicUser.model_validate(user),
    }


@router.get("/admin", include_in_schema=False)
def admin_page(request: Request):
    """Separate anonymous login redirects from authenticated member denial."""
    try:
        user = security.require_admin(request)
    except HTTPException as error:
        if error.status_code == 401:
            return RedirectResponse("/login", status_code=303)
        if error.status_code == 403:
            return request.app.state.templates.TemplateResponse(
                request=request, name="admin_denied.html", context={}, status_code=403
            )
        raise
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"user": PublicUser.model_validate(user)},
    )
