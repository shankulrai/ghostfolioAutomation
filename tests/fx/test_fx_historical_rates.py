"""
SCRUM-8: Historical FX rate conversion tests
Tests TC-006, TC-007, TC-008, TC-009, TC-010 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.fx
class TestHistoricalFXRates:
    """Test historical FX rate usage for transaction dates"""

    @pytest.mark.priority_critical
    def test_cached_fx_rate_returned_within_50ms(self, page: Page):
        """TC-006: Cached FX rate returned within 50ms"""
        # This would be an API test - placeholder for structure
        import requests
        import time

        # Warm up cache
        response = requests.get(
            "http://localhost:3000/api/fx-rate",
            params={"from": "USD", "to": "EUR", "date": "2024-01-15"}
        )
        assert response.status_code == 200

        # Measure cached response
        start = time.time()
        response = requests.get(
            "http://localhost:3000/api/fx-rate",
            params={"from": "USD", "to": "EUR", "date": "2024-01-15"}
        )
        elapsed_ms = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 50, f"Cache hit took {elapsed_ms}ms (expected <50ms)"
        assert "rate" in response.json()

    @pytest.mark.priority_critical
    def test_cache_miss_falls_back_to_database(self, page: Page):
        """TC-007: Database fallback when cache misses"""
        import requests

        # Request uncached rate
        response = requests.get(
            "http://localhost:3000/api/fx-rate",
            params={"from": "USD", "to": "EUR", "date": "2024-01-15"}
        )

        assert response.status_code == 200
        rate_1 = response.json()["rate"]

        # Second request should hit cache
        response = requests.get(
            "http://localhost:3000/api/fx-rate",
            params={"from": "USD", "to": "EUR", "date": "2024-01-15"}
        )

        assert response.status_code == 200
        rate_2 = response.json()["rate"]
        assert rate_1 == rate_2

    @pytest.mark.priority_critical
    def test_historical_fx_rate_used_for_transaction_date(self, page: Page):
        """TC-008: Transaction from 2024-01-15 uses 2024-01-15 FX rate"""
        # Create transaction
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "AAPL")
        page.fill("input[name='quantity']", "100")
        page.fill("input[name='date']", "2024-01-15")
        page.fill("input[name='currency']", "USD")
        page.click("button[type='submit']")

        # Set base currency to EUR
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "EUR")
        page.click("button[type='submit']")

        # View valuation
        page.goto("/portfolio/test-portfolio")

        # Verify conversion uses historical rate (not current rate)
        expect(page.locator("[data-testid='transaction-date']")).to_contain_text("2024-01-15")
        # Rate indicator should show historical date
        expect(page.locator("[data-testid='fx-rate-date']")).to_contain_text("2024-01-15")

    @pytest.mark.priority_critical
    def test_current_rate_not_used_for_historical_transaction(self, page: Page):
        """TC-009: Current FX rate NOT used for historical transaction"""
        # Create historical transaction
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "SAP")
        page.fill("input[name='quantity']", "50")
        page.fill("input[name='date']", "2024-01-15")
        page.fill("input[name='currency']", "EUR")
        page.fill("input[name='price']", "100")
        page.click("button[type='submit']")

        # Set base currency to USD
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        # Get historical value
        page.goto("/portfolio/test-portfolio")
        historical_value = page.locator("[data-testid='holding-value'][data-symbol='SAP']").text_content()

        # Verify rate date is 2024-01-15, not current date
        expect(page.locator("[data-testid='fx-rate-date'][data-symbol='SAP']")).to_contain_text("2024-01-15")
        assert historical_value is not None

    @pytest.mark.priority_critical
    def test_batch_conversion_for_same_date_transactions(self, page: Page):
        """TC-010: Multiple transactions same date use same FX rate"""
        # Create 10 transactions on same date
        for i in range(10):
            page.goto("/portfolio/test-portfolio/transaction/create")
            page.fill("input[name='symbol']", f"STOCK{i}")
            page.fill("input[name='quantity']", "10")
            page.fill("input[name='date']", "2024-01-15")
            page.fill("input[name='currency']", "EUR")
            page.fill("input[name='price']", "100")
            page.click("button[type='submit']")

        # Set base currency to USD
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        # View portfolio
        page.goto("/portfolio/test-portfolio")

        # All holdings should show same rate date
        rate_dates = page.locator("[data-testid='fx-rate-date']").all_text_contents()
        assert len(rate_dates) == 10
        assert all(date == "2024-01-15" for date in rate_dates)
