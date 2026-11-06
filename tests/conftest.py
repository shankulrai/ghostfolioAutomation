"""
Pytest configuration and fixtures for SCRUM-8 test automation
"""
import pytest
from playwright.sync_api import Page, Browser


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """Fixture providing an authenticated page"""
    # Login
    page.goto("http://localhost:3000/login")
    page.fill("input[name='email']", "test@example.com")
    page.fill("input[name='password']", "password123")
    page.click("button[type='submit']")
    page.wait_for_url("**/portfolio")

    return page


@pytest.fixture
def clean_portfolio(authenticated_page: Page) -> Page:
    """Fixture providing a clean test portfolio"""
    page = authenticated_page

    # Delete existing test portfolio if present
    page.goto("http://localhost:3000/portfolio/test-portfolio")
    if page.locator("[data-testid='delete-portfolio']").is_visible():
        page.click("[data-testid='delete-portfolio']")
        page.click("[data-testid='confirm-delete']")

    # Create fresh test portfolio
    page.goto("http://localhost:3000/portfolio/create")
    page.fill("input[name='name']", "test-portfolio")
    page.select_option("select[name='baseCurrency']", "USD")
    page.click("button[type='submit']")

    yield page

    # Cleanup after test
    page.goto("http://localhost:3000/portfolio/test-portfolio")
    if page.locator("[data-testid='delete-portfolio']").is_visible():
        page.click("[data-testid='delete-portfolio']")
        page.click("[data-testid='confirm-delete']")


@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request):
    """Automatically capture screenshot on test failure"""
    yield

    if request.node.rep_call.failed:
        screenshot_path = f"screenshots/{request.node.name}.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test result for screenshot fixture"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
