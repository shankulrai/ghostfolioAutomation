"""
SCRUM-8: FX rate fallback for weekends/holidays
Tests TC-029, TC-030, TC-031 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.fx
class TestFXFallbackRates:
    """Test forward-fill logic for missing FX rates on weekends/holidays"""

    def test_weekend_transaction_uses_friday_fx_rate(self, page: Page):
        """TC-029: Saturday 2024-01-20 transaction uses Friday 2024-01-19 rate"""
        # Create transaction on Saturday
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "STOCK1")
        page.fill("input[name='quantity']", "100")
        page.fill("input[name='date']", "2024-01-20")  # Saturday
        page.fill("input[name='currency']", "USD")
        page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # View portfolio
        page.goto("/portfolio/test-portfolio")

        # Verify forward-fill from Friday
        expect(page.locator("[data-testid='fx-rate-date'][data-symbol='STOCK1']")).to_contain_text("2024-01-19")

        # Verify fallback indicator displayed
        expect(page.locator("[data-testid='fallback-rate-indicator'][data-symbol='STOCK1']")).to_be_visible()

    def test_holiday_transaction_uses_previous_business_day_rate(self, page: Page):
        """TC-030: Transaction on Christmas Day uses previous business day rate"""
        # Create transaction on holiday
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "STOCK2")
        page.fill("input[name='quantity']", "50")
        page.fill("input[name='date']", "2024-12-25")  # Christmas
        page.fill("input[name='currency']", "USD")
        page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # View portfolio
        page.goto("/portfolio/test-portfolio")

        # Verify previous business day rate used
        expect(page.locator("[data-testid='fx-rate-date'][data-symbol='STOCK2']")).to_contain_text("2024-12-24")

    def test_multi_day_weekend_gap_uses_friday_rate(self, page: Page):
        """TC-031: Monday 2024-01-22 with no data uses Friday 2024-01-19 rate"""
        # Create transaction on Monday after weekend gap
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "STOCK3")
        page.fill("input[name='quantity']", "75")
        page.fill("input[name='date']", "2024-01-22")  # Monday
        page.fill("input[name='currency']", "USD")
        page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # View portfolio
        page.goto("/portfolio/test-portfolio")

        # Verify forward-fill from Friday
        expect(page.locator("[data-testid='fx-rate-date'][data-symbol='STOCK3']")).to_contain_text("2024-01-19")

        # Verify warning indicator
        fallback_tooltip = page.locator("[data-testid='fallback-rate-tooltip'][data-symbol='STOCK3']")
        fallback_tooltip.hover()
        expect(page.locator("[data-testid='tooltip-text']")).to_contain_text("Rate from 2024-01-19 (previous business day)")
