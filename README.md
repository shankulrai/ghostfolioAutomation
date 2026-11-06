# Ghostfolio Automation

QA test automation for Ghostfolio using Playwright (Python).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Running Tests

**All tests:**
```bash
pytest tests/
```

**Regression subset:**
```bash
pytest -m regression
```

**By ticket:**
```bash
pytest -m "ticket('SCRUM-8')"
```

**By priority:**
```bash
pytest -m priority_critical
```

## Test Organization

```
tests/
├── portfolio/    # Portfolio management tests
├── fx/           # FX rate and currency conversion tests
├── user/         # User settings and onboarding tests
├── api/          # API contract tests
├── ui/           # UI component tests
├── fixtures/     # Test data and fixtures
└── conftest.py   # Pytest configuration
```

## Test Markers

- `@pytest.mark.regression` - Regression test cases
- `@pytest.mark.ticket("<ID>")` - Link to Jira ticket
- `@pytest.mark.priority_<level>` - Test priority (critical, high, medium, low)
- `@pytest.mark.<area>` - Test area (portfolio, fx, api, ui)

## Reporting

HTML reports generated at `reports/test_report.html` after each run.

## CI Integration

Configure in CI/CD pipeline:
```yaml
- name: Run Regression Tests
  run: |
    source venv/bin/activate
    pytest -m regression --html=reports/regression.html
```
