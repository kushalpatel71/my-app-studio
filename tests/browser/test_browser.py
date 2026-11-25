"""Real Chromium checks; each run names its actual implemented lesson scope."""

from dataclasses import dataclass, field
import json
import os
import re
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

import pytest
from playwright.sync_api import expect

ROOT = Path(__file__).resolve().parents[2]
LEVEL = int(os.getenv("APP_TEST_LESSON", "0"))
pytestmark = pytest.mark.e2e


@dataclass
class BrowserServer:
    """Keep inherited process configuration out of assertion reports."""

    url: str
    environment: dict = field(repr=False)


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    """Start only an isolated loopback fixture with temporary account data."""
    directory = tmp_path_factory.mktemp("app-browser")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    environment = dict(
        os.environ,
        APP_MODE="development",
        APP_ORIGIN=url,
        APP_DATABASE=str(directory / "browser.sqlite3"),
        APP_SECRET="disposable-browser-test-key-" + uuid.uuid4().hex,
        STUDIO_LIVE_RELOAD="0",
    )
    with (directory / "server.log").open("w") as output:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(url + "/health", timeout=1) as response:
                        assert json.load(response)["status"] == "ok"
                    break
                except (OSError, urllib.error.URLError):
                    if process.poll() is not None:
                        raise RuntimeError(
                            "Isolated browser app failed to start"
                        ) from None
                    time.sleep(0.1)
            else:
                raise RuntimeError("Isolated browser app did not become ready")
            yield BrowserServer(url=url, environment=environment)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def test_homepage_keyboard_and_mobile_layout(page, server):
    """Check real rendering/navigation, including a narrow viewport and keyboard."""
    page.goto(server.url)
    expect(page.get_by_role("heading", level=1)).to_be_visible()
    page.keyboard.press("Tab")
    expect(page.get_by_role("link", name="Skip to content")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#main")).to_be_focused()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert (
        page.locator(".button").evaluate(
            "element => element.getBoundingClientRect().height"
        )
        >= 44
    )
    assert page.get_by_role("navigation", name="Main navigation").is_visible()
    if LEVEL >= 1:
        expect(page.get_by_text("Your Project", exact=True)).to_have_count(0)


def test_current_lesson_browser_journey(page, server):
    """Only implemented scope is claimed; stage zero is explicitly foundation only."""
    page.goto(server.url)
    if LEVEL < 2:
        primary = page.locator(".hero .button")
        destination = primary.get_attribute("href")
        assert destination and destination.startswith("#") and len(destination) > 1
        primary.click()
        expect(page.locator(destination)).to_be_in_viewport()
        assert page.request.get(server.url + "/signup").status == 404
        assert page.request.get(server.url + "/not-a-feature").status == 404
        return
    username = "browser_" + uuid.uuid4().hex[:10]
    password = "a disposable browser passphrase"
    page.goto(server.url + "/signup")
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Create account", exact=True).click()
    expect(page.get_by_role("heading", name="Log in", exact=True)).to_be_visible()
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill("the wrong disposable passphrase")
    page.get_by_role("button", name="Log in", exact=True).click()
    expect(page.get_by_role("alert")).to_be_visible()
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Log in", exact=True).click()
    expect(
        page.get_by_role("heading", name="Your member space", exact=True)
    ).to_be_visible()
    cookies = page.context.cookies()
    session = next(cookie for cookie in cookies if cookie["name"] == "studio-session")
    assert session["httpOnly"] and session["sameSite"] == "Lax"
    if LEVEL >= 3:
        _check_role_boundary(page, server, username)
    page.goto(server.url + "/dashboard")
    page.get_by_role("button", name="Log out", exact=True).click()
    assert page.request.get(server.url + "/api/me").status == 401
    replay = page.request.get(
        server.url + "/api/me",
        headers={"Cookie": session["name"] + "=" + session["value"]},
    )
    assert replay.status == 401
    page.goto(server.url + "/dashboard")
    expect(page.get_by_role("heading", name="Log in", exact=True)).to_be_visible()


def _check_role_boundary(page, server, username):
    """The trusted CLI changes DB roles; an existing JWT never overrides the DB."""
    assert page.request.get(server.url + "/api/admin").status == 403
    page.goto(server.url + "/admin")
    expect(
        page.get_by_role("heading", name="Admin access required", exact=True)
    ).to_be_visible()
    for role, status in (("admin", 200), ("member", 403)):
        subprocess.run(
            [sys.executable, "studio.py", "user", "role", username, "--role", role],
            cwd=ROOT,
            env=server.environment,
            check=True,
            capture_output=True,
            text=True,
        )
        assert page.request.get(server.url + "/api/admin").status == status
        if role == "admin":
            page.goto(server.url + "/admin")
            expect(
                page.get_by_role("heading", name="Administration", exact=True)
            ).to_be_visible()


@pytest.mark.parametrize("width", [1440, 768, 390])
def test_car_gallery_and_next_step(page, server, width):
    """The gallery CTA reaches usable, credited build details on each layout."""
    if LEVEL < 1:
        pytest.skip("Car showcase belongs to APP-001, not the neutral foundation")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server.url)
    page.get_by_role("link", name="Next Step", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page).to_have_url(server.url + "/#builds")
    gallery = page.locator("#builds")
    expect(gallery).to_be_focused()
    expect(
        page.get_by_role("heading", name="Different cars. One shared obsession.")
    ).to_be_in_viewport()
    assert page.evaluate("window.scrollY > 0")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    cards = gallery.locator("article")
    expect(cards).to_have_count(3)
    for card in cards.all():
        for label in ("Wheels", "Suspension", "Engine", "Performance"):
            expect(card.locator("dt", has_text=label)).to_have_count(1)
        expect(card.get_by_text("Sample build /", exact=False)).to_be_visible()
        credit = card.locator("figcaption a")
        assert credit.get_attribute("href").startswith("https://unsplash.com/photos/")
        photo = card.locator("img")
        photo.scroll_into_view_if_needed()
        expect(photo).to_be_visible()
        expect(photo).to_have_attribute("alt", re.compile(r".+"))
        page.wait_for_function(
            "image => image.complete && image.naturalWidth > 0",
            arg=photo.element_handle(),
        )
    assert page.request.get(server.url + "/signup").status == (
        200 if LEVEL >= 2 else 404
    )
    assert page.request.get(server.url + "/upload").status == 404


@pytest.mark.parametrize("width", [1440, 390])
def test_separate_showcase_page_navigation(page, server, width):
    """Real links lead to each page and car without replacing the home anchor."""
    if LEVEL < 1:
        pytest.skip("Static showcase belongs to APP-001")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server.url)
    nav = page.get_by_role("navigation", name="Main navigation", exact=True)
    for name, path in (("Home", "/"), ("Car Builds", "/builds"), ("About", "/about")):
        expect(nav.get_by_role("link", name=name, exact=True)).to_have_attribute(
            "href", path
        )
    page.get_by_role("link", name="View All Builds", exact=True).first.click()
    expect(page).to_have_url(server.url + "/builds")
    expect(page.get_by_role("heading", level=1)).to_have_text("Car builds.")
    for slug, model in (
        ("skyline", "Nissan Skyline R34"),
        ("miata", "Mazda MX-5 Miata"),
        ("bmw", "BMW M3 G80"),
    ):
        card = page.locator(
            "article", has=page.get_by_role("heading", name=model, exact=True)
        )
        expect(
            card.get_by_role("link", name="Explore " + model, exact=True)
        ).to_have_attribute("href", "/builds/" + slug)
        card.get_by_role("link", name="View Details for " + model, exact=True).focus()
        page.keyboard.press("Enter")
        expect(page).to_have_url(server.url + "/builds/" + slug)
        expect(page.get_by_role("heading", level=1)).to_have_text(model)
        expect(
            page.get_by_role("heading", name="Example specifications", exact=True)
        ).to_be_visible()
        for label in ("Wheels", "Suspension", "Engine", "Performance"):
            expect(page.locator(".mod-panel dt", has_text=label)).to_be_visible()
        photo = page.locator(".detail-photo")
        page.wait_for_function(
            "image => image.complete && image.naturalWidth > 0",
            arg=photo.element_handle(),
        )
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.request.get(server.url + "/builds/" + slug).status == 200
        page.get_by_role("link", name="Back to Car Builds", exact=True).click()
        expect(page).to_have_url(server.url + "/builds")
    nav.get_by_role("link", name="About", exact=True).click()
    expect(page).to_have_url(server.url + "/about")
    expect(page.get_by_role("heading", level=1)).to_have_text(
        "A place for the details."
    )
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    nav.get_by_role("link", name="Home", exact=True).click()
    expect(page).to_have_url(server.url + "/")
    page.get_by_role("link", name="Next Step", exact=True).click()
    expect(page).to_have_url(server.url + "/#builds")
    expect(page.locator("#builds")).to_be_focused()
    assert page.request.get(server.url + "/builds/unknown").status == 404


@pytest.mark.parametrize("width", [1440, 390])
def test_branded_account_layout_and_keyboard_flow(page, server, width):
    """Member pages stay responsive and usable through keyboard form submission."""
    if LEVEL < 2:
        pytest.skip("Account UI belongs to APP-002")
    page.set_viewport_size({"width": width, "height": 900})
    username = "layout_" + uuid.uuid4().hex[:10]
    page.goto(server.url + "/dashboard")
    expect(page).to_have_url(server.url + "/login")
    page.get_by_role("link", name="Sign up", exact=True).click()
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill("a disposable layout passphrase")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.get_by_role("button", name="Create account", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("status")).to_have_text(
        "Account created. Log in to enter your member space."
    )
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill("a disposable layout passphrase")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.get_by_role("button", name="Log in", exact=True).focus()
    page.keyboard.press("Enter")
    expect(
        page.get_by_role("heading", name="Your member space", exact=True)
    ).to_be_visible()
    expect(page.locator(".account-details")).to_contain_text(username)
    expect(page.locator(".account-details")).to_contain_text("member")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    for name in ("Home", "Car Builds", "About"):
        expect(
            page.get_by_role("navigation", name="Main navigation").get_by_role(
                "link", name=name, exact=True
            )
        ).to_be_visible()
    page.get_by_role("button", name="Log out", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("status")).to_have_text(
        "You are logged out. Log in again to access your dashboard."
    )
    page.goto(server.url + "/dashboard")
    expect(page).to_have_url(server.url + "/login")


@pytest.mark.parametrize("width", [1440, 390])
def test_admin_page_cli_changes_and_existing_session(page, server, width):
    """A live browser session follows trusted CLI role changes on each request."""
    if LEVEL < 3:
        pytest.skip("Admin boundary belongs to APP-003")
    page.set_viewport_size({"width": width, "height": 900})
    response = page.goto(server.url + "/admin")
    expect(page).to_have_url(server.url + "/login")
    assert page.request.get(server.url + "/api/admin").status == 401
    username = "roles_" + uuid.uuid4().hex[:10]
    page.goto(server.url + "/signup")
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(
        "a disposable role browser passphrase"
    )
    page.get_by_role("button", name="Create account", exact=True).click()
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(
        "a disposable role browser passphrase"
    )
    page.get_by_role("button", name="Log in", exact=True).click()
    original_cookie = next(
        cookie["value"]
        for cookie in page.context.cookies()
        if cookie["name"] == "studio-session"
    )
    response = page.goto(server.url + "/admin")
    assert response.status == 403
    expect(
        page.get_by_role("heading", name="Admin access required", exact=True)
    ).to_be_visible()
    expect(
        page.get_by_role("navigation", name="Main navigation").get_by_role(
            "link", name="Admin", exact=True
        )
    ).to_have_count(0)
    for role, expected in (("admin", 200), ("member", 403)):
        subprocess.run(
            [sys.executable, "studio.py", "user", "role", username, "--role", role],
            cwd=ROOT,
            env=server.environment,
            check=True,
            capture_output=True,
            text=True,
        )
        response = page.goto(server.url + "/admin")
        assert response.status == expected
        assert page.request.get(server.url + "/api/admin").status == expected
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        current_cookie = next(
            cookie["value"]
            for cookie in page.context.cookies()
            if cookie["name"] == "studio-session"
        )
        assert current_cookie == original_cookie
        if role == "admin":
            expect(
                page.get_by_role("heading", name="Administration", exact=True)
            ).to_be_visible()
            expect(
                page.get_by_role("navigation", name="Main navigation").get_by_role(
                    "link", name="Admin", exact=True
                )
            ).to_be_visible()
        else:
            expect(
                page.get_by_role("heading", name="Admin access required", exact=True)
            ).to_be_visible()
    page.get_by_role("link", name="Your dashboard", exact=True).click()
    expect(
        page.get_by_role("heading", name="Your member space", exact=True)
    ).to_be_visible()
    expect(page.locator(".account-details")).to_contain_text("member")


@pytest.mark.parametrize("width", [1440, 390, 320])
def test_review2_public_portfolio_keyboard_and_layout(page, server, width):
    """Additive portfolio links work without an account at narrow widths."""
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server.url + "/portfolio")
    expect(page.get_by_role("heading", name="Kushal Patel", exact=True)).to_be_visible()
    expect(
        page.get_by_text("Verified Plan review · private team project", exact=True)
    ).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.get_by_role("link", name="Projects", exact=True).focus()
    page.keyboard.press("Enter")
    assert page.url.endswith("#projects")
    page.get_by_role("link", name="Read RAG case study", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Evidence before answers.")).to_be_visible()
    page.get_by_role("link", name="Open the assistant", exact=True).click()
    expect(
        page.get_by_role("heading", name="Knowledge Assistant", exact=True)
    ).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.get_by_label("Your question").fill("Where does View Details take me?")
    page.get_by_role("button", name="Ask the assistant", exact=True).click()
    expect(page.locator("#rag-answer")).to_have_text(
        "Insufficient evidence in the approved corpus."
    )
    expect(
        page.get_by_role("button", name="Ask the assistant", exact=True)
    ).to_be_enabled()


def test_review2_chat_error_state(page, server):
    """UI-only failed-network fixture; not a provider or RAG success claim."""
    page.goto(server.url + "/rag")
    page.route("**/api/rag/ask", lambda route: route.abort())
    page.get_by_label("Your question").fill("Where are the builds?")
    page.get_by_role("button", name="Ask the assistant", exact=True).click()
    expect(page.locator("#rag-status")).to_have_text(
        "Connection failed. Please try again later."
    )
    expect(
        page.get_by_role("button", name="Ask the assistant", exact=True)
    ).to_be_enabled()


@pytest.mark.parametrize("width", [1440, 768, 390, 320])
def test_review3_accessibility_and_links(page, server, width):
    """Keyboard, headings, contrast samples and real links across four widths."""
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: (
            errors.append(message.text) if message.type == "error" else None
        ),
    )
    page.set_viewport_size({"width": width, "height": 900})
    for path in ["/portfolio", "/portfolio/projects/rag", "/rag"]:
        assert page.goto(server.url + path).status == 200
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.locator("main h1").count() == 1
        levels = page.locator("main h1,main h2,main h3").evaluate_all(
            "els => els.map(e => Number(e.tagName[1]))"
        )
        assert all(b <= a + 1 for a, b in zip(levels, levels[1:]))
        assert page.locator("img:not([alt])").count() == 0
        assert page.locator("img").evaluate_all(
            "els => els.every(e => e.complete && e.naturalWidth > 0)"
        )
        # Sample actual rendered text against its nearest opaque ancestor.
        contrast = page.locator("main p,main h1,main h2,main h3,main a").evaluate_all(
            """els => {
          const rgb = c => (c.match(/[\\d.]+/g)||[]).map(Number);
          const lum = c => { const v=c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return .2126*v[0]+.7152*v[1]+.0722*v[2] };
          return els.filter(e=>e.getClientRects().length).map(e=>{
            let b=e,bg;while(b){bg=rgb(getComputedStyle(b).backgroundColor);if(bg.length===3||bg[3]===1)break;b=b.parentElement}
            if(!b)bg=[255,255,255];
            const s=getComputedStyle(e),fg=rgb(s.color),l1=lum(fg),l2=lum(bg),ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
            const large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&parseInt(s.fontWeight)>=700);
            return {text:e.innerText.slice(0,50),ratio,minimum:large?3:4.5};
          });
        }"""
        )
        assert contrast and all(c["ratio"] >= c["minimum"] for c in contrast), contrast
        if path == "/portfolio":
            # Tab through actual focus order, not programmatic focus alone.
            page.goto(server.url + path)
            focus_count = page.locator("a:visible,button:visible").count()
            for _ in range(focus_count):
                page.keyboard.press("Tab")
                state = page.evaluate(
                    """() => { const e=document.activeElement,s=getComputedStyle(e); return {tag:e.tagName,outline:s.outlineStyle,width:parseFloat(s.outlineWidth)} }"""
                )
                assert state["tag"] in ["A", "BUTTON"]
                assert state["outline"] != "none" and state["width"] >= 2, state
            for link in page.locator("main a[href^='#']").all():
                assert page.locator(link.get_attribute("href")).count() == 1
            paths = set(
                page.locator("a[href^='/']").evaluate_all(
                    "els=>els.map(e=>e.getAttribute('href'))"
                )
            )
            assert all(
                page.request.get(server.url + url).status == 200 for url in paths
            )
        if path == "/rag":
            expect(page.get_by_label("Your question")).to_have_attribute(
                "maxlength", "1000"
            )
            assert (
                page.get_by_role("button", name="Ask the assistant").bounding_box()[
                    "height"
                ]
                >= 44
            )
        evidence = os.getenv("RAG_BROWSER_EVIDENCE_DIR")
        if evidence:
            target = Path(evidence)
            target.mkdir(parents=True, exist_ok=True)
            page.screenshot(
                path=str(target / f"{path.strip('/').replace('/','-')}-{width}.png"),
                full_page=True,
            )
    assert errors == []
