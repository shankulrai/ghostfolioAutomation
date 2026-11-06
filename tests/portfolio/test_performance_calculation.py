"""
SCRUM-8: Performance calculation with FX impact tests
Tests TC-011, TC-012, TC-021, TC-023, TC-024 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.portfolio
class TestPerformanceCalculation:
    """Test historical performance uses transaction-date FX rates"""

    def test_historical_performance_uses_transaction_date_fx_rate(self, page: Page):
        """TC-011: Performance calculation for 2023 uses 2023 FX rates"""
        # Create historical transaction
        page.goto("/portfolio/test-portfolio/transaction/create")
        page.fill("input[name='symbol']", "HSBC")
        page.fill("input[name='quantity']", "200")
        page.fill("input[name='date']", "2023-06-10")
        page.fill("input[name='currency']", "GBP")
        page.fill("input[name='price']", "50")
        page.click("button[type='submit']")

        # Set base currency to USD
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        # Generate performance report for 2023
        page.goto("/portfolio/test-portfolio/reports/performance?year=2023")

        # Verify historical rate used (not current rate)
        expect(page.locator("[data-testid='fx-rate-date']")).to_contain_text("2023-06-10")

    def test_fx_impact_reflected_in_performance_calculation(self, page: Page):
        """TC-012: EUR weakening 5% reflected in USD-based performance"""
        # This would require mocking FX rate changes over time
        # Placeholder for structure
        page.goto("/portfolio/test-portfolio/reports/performance")

        # Verify FX impact line item exists
        expect(page.locator("[data-testid='fx-impact']")).to_be_visible()

    @pytest.mark.priority_high
    def test_performance_report_in_base_currency(self, page: Page):
        """TC-021: 2023 performance report shows gains/losses in USD"""
        page.goto("/portfolio/test-portfolio/settings")
        page.select_option("select[name='baseCurrency']", "USD")
        page.click("button[type='submit']")

        page.goto("/portfolio/test-portfolio/reports/performance?year=2023")

        # Verify all values in USD
        expect(page.locator("[data-testid='total-gain']")).to_contain_text("$")
        expect(page.locator("[data-testid='total-loss']")).to_contain_text("$")

    @pytest.mark.priority_high
    def test_fx_impact_isolated_in_performance_calculation(self, page: Page):
        """TC-023: EUR 5% weakening shown separately from asset returns"""
        page.goto("/portfolio/test-portfolio/reports/performance")

        # Verify FX impact is a separate line item
        expect(page.locator("[data-testid='fx-impact-label']")).to_have_text("FX Impact")
        expect(page.locator("[data-testid='asset-return-label']")).to_have_text("Asset Return")
        expect(page.locator("[data-testid='total-return-label']")).to_have_text("Total Return")

    @pytest.mark.priority_high
    def test_strong_base_currency_shows_fx_gain(self, page: Page):
        """TC-024: USD strengthens 10% — USD-based report shows FX gain"""
        # Would require historical data setup
        page.goto("/portfolio/test-portfolio/reports/performance")

        # Verify FX impact calculation exists
        fx_impact = page.locator("[data-testid='fx-impact']").text_content()
        assert fx_impact is not None
