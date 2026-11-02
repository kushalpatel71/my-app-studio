"""Public static showcase pages for APP-001; no build database or account flow."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/builds", include_in_schema=False)
def builds(request: Request):
    """Browse the three illustrative projects from the existing brand data."""
    return request.app.state.templates.TemplateResponse(
        request=request, name="builds.html", context={}
    )


@router.get("/builds/{slug}", include_in_schema=False)
def build_detail(request: Request, slug: str):
    """Resolve only known sample slugs; never treat a URL as a file path."""
    build = next(
        (item for item in request.app.state.brand()["builds"] if item["slug"] == slug),
        None,
    )
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return request.app.state.templates.TemplateResponse(
        request=request, name="build_detail.html", context={"build": build}
    )


@router.get("/about", include_in_schema=False)
def about(request: Request):
    """Explain the purpose and honest limits of the static showcase."""
    return request.app.state.templates.TemplateResponse(
        request=request, name="about.html", context={}
    )
