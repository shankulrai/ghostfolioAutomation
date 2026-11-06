"""
SCRUM-8: Batch FX conversion tests
Tests TC-036, TC-037 from regression subset
"""
import pytest
import requests


@pytest.mark.regression
@pytest.mark.ticket("SCRUM-8")
@pytest.mark.priority_critical
@pytest.mark.api
class TestBatchConversion:
    """Test batch FX conversion groups by currency pair and date"""

    def test_batch_conversion_single_query_per_tuple(self):
        """TC-036: 100 USDEUR conversions on 2024-01-15 execute as single query"""
        base_url = "http://localhost:3000/api"

        # Create 100 transactions with same currency/date
        conversions = [
            {"from": "USD", "to": "EUR", "date": "2024-01-15", "amount": 100}
            for _ in range(100)
        ]

        # Call batch conversion endpoint
        response = requests.post(
            f"{base_url}/fx-rate/batch",
            json={"conversions": conversions}
        )

        assert response.status_code == 200
        results = response.json()["results"]

        assert len(results) == 100
        # Verify query count header (implementation should add this)
        assert int(response.headers.get("X-Query-Count", "0")) == 1

    def test_batch_conversion_maintains_input_order(self):
        """TC-037: Batch conversion output matches input order"""
        base_url = "http://localhost:3000/api"

        # Create 50 conversions with mixed currencies/dates
        conversions = [
            {"from": "USD", "to": "EUR", "date": f"2024-01-{i:02d}", "amount": 100 * i}
            for i in range(1, 51)
        ]

        response = requests.post(
            f"{base_url}/fx-rate/batch",
            json={"conversions": conversions}
        )

        assert response.status_code == 200
        results = response.json()["results"]

        # Verify output length matches input
        assert len(results) == 50

        # Verify order preserved (check dates match input order)
        for i, result in enumerate(results):
            expected_date = f"2024-01-{i+1:02d}"
            assert result["date"] == expected_date
