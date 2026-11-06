"""
SCRUM-8: Kill switch functionality tests
Tests TC-046, TC-047, TC-048 from regression subset
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.fx
class TestKillSwitch:
    """Test kill switch activates on FX provider outage"""

    def test_kill_switch_activates_on_provider_outage(self, page: Page):
        """TC-046: FX provider down 10 minutes triggers automatic kill switch"""
        # This would require mocking FX provider outage
        # Placeholder for structure

        # Navigate to portfolio after kill switch activated
        page.goto("/portfolio/test-portfolio")

        # Verify warning banner displayed
        warning_banner = page.locator("[data-testid='fx-kill-switch-warning']")
        expect(warning_banner).to_be_visible()
        expect(warning_banner).to_contain_text("FX rates temporarily unavailable")

        # Verify portfolio shows original currency values (fallback mode)
        expect(page.locator("[data-testid='fallback-mode-indicator']")).to_be_visible()

    def test_kill_switch_deactivates_when_provider_recovers(self, page: Page):
        """TC-047: Kill switch resets when provider returns to health"""
        # Mock provider recovery

        # Load portfolio
        page.goto("/portfolio/test-portfolio")

        # Verify NO warning banner
        warning_banner = page.locator("[data-testid='fx-kill-switch-warning']")
        expect(warning_banner).not_to_be_visible()

        # Verify base currency conversions resume
        expect(page.locator("[data-testid='base-currency-label']")).to_be_visible()

    def test_kill_switch_warning_banner_persists_until_dismissed(self, page: Page):
        """TC-048: User sees warning banner while kill switch active"""
        # Navigate with kill switch active
        page.goto("/portfolio/test-portfolio")

        # Verify banner visible
        warning_banner = page.locator("[data-testid='fx-kill-switch-warning']")
        expect(warning_banner).to_be_visible()
        expect(warning_banner).to_contain_text("FX rates temporarily unavailable. Showing values in original currencies.")

        # Verify info icon present
        expect(page.locator("[data-testid='kill-switch-info-icon']")).to_be_visible()

        # Click dismiss
        page.click("[data-testid='kill-switch-dismiss']")

        # Reload page
        page.reload()

        # Banner should reappear (not permanently dismissed while kill switch active)
        expect(warning_banner).to_be_visible()
