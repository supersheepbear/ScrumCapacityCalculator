# Maintenance

## Run tests

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

The root `app.py` receives the form, calls the calculation code, and returns JSON. The page is `templates/index.html`; browser interactions are in `static/js/main.js`. Python code lives in `src/scrum_capacity_calculator/`:

- `validators/config_validator.py`: configuration and reference validation.
- `utils/config_loader.py`: JSON to domain objects.
- `core/config_csv.py`: full team setup CSV import and export.
- `core/calendar_service.py`: working days and national holidays.
- `core/calculator.py`: member and team hours, task summaries.
- `core/jira_parser.py`: Jira CSV parsing with common header and delimiter variants.

`tests/test_app.py` covers the key calculations through the user-facing HTTP endpoint. When changing holiday or PTO logic, add a worked example there. The **Load example** button provides sample input.

For the configuration formats, download JSON or CSV from the page and refer to [SPEC.md](../SPEC.md). Older JSON configurations without `group` place members in `Team`; missing `group_holidays` means no additional group dates.
