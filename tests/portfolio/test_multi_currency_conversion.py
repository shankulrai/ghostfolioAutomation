"""
SCRUM-8: Multi-currency portfolio conversion tests
Tests TC-013, TC-014, TC-015, TC-016 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.portfolio
class TestMultiCurrencyConversion:
    """Test multi-currency portfolio conversion to base currency"""

    def test_multi_currency_holdings_converted_to_base_currency(self, page: Page):
        """TC-013: Holdings in USD, EUR, GBP all converted to EUR"""
        # Create holdings in different currencies
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "AAPL")
        page.fill("input[name='quantity']", "100")
        page.fill("input[name='currency']", "USD")
        page.click("button[type='submit']")

        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "SAP")
        page.fill("input[name='quantity']", "50")
        page.fill("input[name='currency']", "EUR")
        page.click("button[type='submit']")

        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "HSBC")
        page.fill("input[name='quantity']", "30")
        page.fill("input[name='currency']", "GBP")
        page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # Verify all holdings displayed in EUR
        page.goto("/portfolio/test-portfolio")
        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("EUR")

        # AAPL should show converted from USD
        expect(page.locator("[data-testid='holding-currency'][data-symbol='AAPL']")).to_contain_text("EUR")

        # SAP should show in EUR (no conversion)
        expect(page.locator("[data-testid='holding-currency'][data-symbol='SAP']")).to_contain_text("EUR")

        # HSBC should show converted from GBP
        expect(page.locator("[data-testid='holding-currency'][data-symbol='HSBC']")).to_contain_text("EUR")

    def test_base_currency_change_triggers_recalculation(self, page: Page):
        """TC-014: Changing base currency from USD to GBP recalculates all values"""
        # Setup portfolio with USD base
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        page.goto("/portfolio/test-portfolio")
        usd_total = page.locator("[data-testid='total-value']").text_content()

        # Change to GBP
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "GBP")
        page.click("button[type='submit']")

        # Verify immediate recalculation
        page.goto("/portfolio/test-portfolio")
        gbp_total = page.locator("[data-testid='total-value']").text_content()

        expect(page.locator("[data-testid='base-currency-label']")).to_have_text("GBP")
        assert gbp_total != usd_total
        assert "£" in gbp_total or "GBP" in gbp_total

    def test_portfolio_total_displayed_in_single_base_currency(self, page: Page):
        """TC-015: Mixed-currency portfolio shows single EUR total"""
        # Create mixed-currency holdings
        currencies = ["USD", "EUR", "GBP", "CHF"]
        for i, currency in enumerate(currencies):
            page.goto("/portfolio/test-portfolio/transaction/create")
            page.fill("input[name='symbol']", f"STOCK{i}")
            page.fill("input[name='quantity']", "10")
            page.fill("input[name='currency']", currency)
            page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # Verify single total
        page.goto("/portfolio/test-portfolio")
        total_element = page.locator("[data-testid='total-value']")
        total_text = total_element.text_content()

        # Should contain only EUR symbol/code
        assert "€" in total_text or "EUR" in total_text
        # Should NOT contain mixed symbols
        assert "$" not in total_text
        assert "£" not in total_text
        assert "CHF" not in total_text

    @pytest.mark.priority_high
    def test_base_currency_label_visible_in_ui(self, page: Page):
        """TC-016: Base currency clearly indicated in portfolio header"""
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        page.goto("/portfolio/test-portfolio")

        # Verify label presence and content
        base_currency_label = page.locator("[data-testid='base-currency-label']")
        expect(base_currency_label).to_be_visible()
        expect(base_currency_label).to_contain_text("EUR")
