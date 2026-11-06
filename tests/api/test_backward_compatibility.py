"""
SCRUM-8: API backward compatibility tests
Tests TC-040 from regression subset
"""
import pytest
import requests


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.api
class TestBackwardCompatibility:
    """Test API remains backward compatible with existing clients"""

    def test_old_client_continues_working_with_new_api_response(self):
        """TC-040: Existing mobile app continues working with new API response"""
        base_url = "http://localhost:3000/api"

        # Call portfolio details API
        response = requests.get(f"{base_url}/portfolio/test-portfolio")

        assert response.status_code == 200
        data = response.json()

        # Verify old field still present
        assert "valueInOriginalCurrency" in data

        # Verify new field also present (additive change)
        assert "valueInBaseCurrency" in data

        # Old clients can extract old field
        original_value = data["valueInOriginalCurrency"]
        assert original_value is not None

        # New field does not break parsing (ignored by old clients)
        assert isinstance(data["valueInBaseCurrency"], (int, float, type(None)))
