"""
SCRUM-8: Performance constraint validation tests
Tests TC-038, TC-039 from regression subset
"""
import pytest
import time
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.portfolio
class TestPerformanceConstraints:
    """Test portfolio valuation meets <1s performance constraint"""

    def test_portfolio_with_500_transactions_responds_under_1_second(self, page: Page):
        """TC-038: Large portfolio valuation meets performance constraint"""
        # Create 500 transactions across 50 holdings
        for i in range(50):
            for j in range(10):
                page.goto("/portfolio/test-portfolio/transaction/create")
                page.fill("input[name='symbol']", f"STOCK{i}")
                page.fill("input[name='quantity']", "10")
                page.fill("input[name='date']", f"2024-01-{(j % 28) + 1:02d}")
                page.fill("input[name='currency']", "EUR" if i % 2 == 0 else "USD")
                page.click("button[type='submit']")

        # Set base currency
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        # Measure page load time
        start = time.time()
        page.goto("/portfolio/test-portfolio")
        page.wait_for_selector("[data-testid='total-value']", state="visible")
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Portfolio valuation took {elapsed:.2f}s (expected <1s)"

        # Verify all holdings displayed
        holdings = page.locator("[data-testid='holding-row']").count()
        assert holdings == 50

    def test_portfolio_with_1000_transactions_under_2_seconds_stress(self, page: Page):
        """TC-039: Portfolio with 1000 transactions under 2 seconds (stress test)"""
        # Create 1000 transactions
        for i in range(100):
            for j in range(10):
                page.goto("/portfolio/test-portfolio/transaction/create")
                page.fill("input[name='symbol']", f"STOCK{i}")
                page.fill("input[name='quantity']", "10")
                page.fill("input[name='date']", f"2024-{(j % 12) + 1:02d}-15")
                page.fill("input[name='currency']", ["USD", "EUR", "GBP"][i % 3])
                page.click("button[type='submit']")

        # Set base currency
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        # Measure page load time
        start = time.time()
        page.goto("/portfolio/test-portfolio")
        page.wait_for_selector("[data-testid='total-value']", state="visible")
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Portfolio valuation took {elapsed:.2f}s (expected <2s)"
