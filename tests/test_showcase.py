"""Public showcase routes must serve static content without account access."""

import pytest

from app.branding import load_brand


@pytest.mark.parametrize("path", ["/builds", "/about"])
def test_public_showcase_pages(client, path):
    """Navigation destinations are real protected-by-default template responses."""
    response = client.get(path)
    assert response.status_code == 200
    assert load_brand()["name"] in response.text
    assert 'href="/builds"' in response.text
    assert 'href="/about"' in response.text
    assert response.headers["x-frame-options"] == "DENY"


@pytest.mark.parametrize("slug", ["skyline", "miata", "bmw"])
def test_direct_build_details(client, slug):
    """Direct URLs identify the right sample and retain every modification."""
    build = next(item for item in load_brand()["builds"] if item["slug"] == slug)
    response = client.get(f"/builds/{slug}")
    assert response.status_code == 200
    assert f"<h1>{build['model']}</h1>" in response.text
    assert "Illustrative sample build" in response.text
    assert "Example specifications" in response.text
    for category, detail in build["modifications"].items():
        assert f"<dt>{category}</dt>" in response.text
        assert detail in response.text
    assert f"/static/photos/{slug}.jpg" in response.text
    assert build["source"] in response.text
    assert client.get(f"/static/photos/{slug}.jpg").status_code == 200


def test_unknown_build_is_not_a_fallback_or_file_lookup(client):
    """Unknown slugs fail rather than silently showing the wrong car."""
    response = client.get("/builds/not-a-build")
    assert response.status_code == 404
    assert response.json() == {"detail": "Build not found"}
    assert client.get("/builds/brand.json").status_code == 404
