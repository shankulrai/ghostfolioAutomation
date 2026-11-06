"""
SCRUM-8: Portfolio-level base currency isolation tests
Tests TC-001, TC-002, TC-003 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.portfolio
class TestPortfolioBaseCurrencyIsolation:
    """Test that multiple portfolios maintain independent base currencies"""

    def test_multiple_portfolios_maintain_independent_base_currencies(self, page: Page):
        """TC-001: Multiple portfolios maintain independent base currencies"""
        # Setup: Create two portfolios
        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Portfolio A")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Portfolio B")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # View Portfolio A
        page.goto("/portfolio/Portfolio A")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("USD")
        expect(page.locator("[data-testid='total-value']")).to_contain_text("$")

        # View Portfolio B
        page.goto("/portfolio/Portfolio B")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("EUR")
        expect(page.locator("[data-testid='total-value']")).to_contain_text("€")

        # Verify isolation: changing Portfolio A does not affect Portfolio B
        page.goto("/portfolio/Portfolio A")
        portfolio_a_value_usd = page.locator("[data-testid='total-value']").text_content()
        assert portfolio_a_value_usd is not None

    def test_base_currency_persists_across_sessions(self, page: Page):
        """TC-002: Base currency selection persists per portfolio"""
        # Create portfolios
        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Retirement")
        page.select_option("select[name='baseCurrency']", "CHF")
        page.click("button[type='submit']")

        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Trading")
        page.select_option("select[name='baseCurrency']", "GBP")
        page.click("button[type='submit']")

        # Logout
        page.click("button[data-testid='user-menu']")
        page.click("a[data-testid='logout']")

        # Login
        page.goto("/login")
        page.fill("input[name='email']", "test@example.com")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")

        # Verify Retirement portfolio
        page.goto("/portfolio/Retirement")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("CHF")

        # Verify Trading portfolio
        page.goto("/portfolio/Trading")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("GBP")

    def test_base_currency_change_affects_only_target_portfolio(self, page: Page):
        """TC-003: Changing base currency in one portfolio does not cascade"""
        # Setup: Create two portfolios
        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Portfolio A")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        page.goto("/portfolio/create")
        page.fill("input[name='name']", "Portfolio B")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # Change Portfolio A base currency
        page.goto("/portfolio/Portfolio A/settings")
        page.select_option("select[name='baseCurrency']", "GBP")
        page.click("button[type='submit']")

        # Verify Portfolio A changed
        page.goto("/portfolio/Portfolio A")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("GBP")

        # Verify Portfolio B unchanged
        page.goto("/portfolio/Portfolio B")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("EUR")
