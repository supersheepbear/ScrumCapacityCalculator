# ScrumBoardTool

## Project Status

✅ **Core implementation complete** - All fundamental features implemented and tested

### Completed Features

- ✅ Calendar-based capacity calculation with holiday/PTO support
- ✅ Multi-location team support with country-specific holidays
- ✅ Jira CSV import and parsing
- ✅ Overload detection and visual indicators
- ✅ Web UI with modern design
- ✅ Team summary and individual results
- ✅ Warning system (unassigned, unestimated, unmatched tasks)
- ✅ HTML report export
- ✅ Comprehensive test suite (34 tests, 100% passing)
- ✅ Full documentation (User Guide, Maintenance, Extensions)

### Test Results

```
34 passed, 12 warnings in 6.82s
Coverage: 49% overall (core logic 94-97%)
```

### Next Steps

Potential future enhancements (see EXTENSION_GUIDE.md):
- PI (6-sprint) view
- Direct Jira API integration
- Historical capacity tracking
- Excel/PDF export
- Multi-team management

## Quick Links

- [README.md](README.md) - Getting started
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - How to use
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Development setup
- [docs/MAINTENANCE.md](docs/MAINTENANCE.md) - Maintenance guide
- [docs/EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md) - Adding features
- [SPEC.md](SPEC.md) - Technical specification
- [CONTEXT.md](CONTEXT.md) - Domain concepts

## Architecture

```
src/scrum_capacity_calculator/
├── core/           # Business logic (calculator, calendar, parser)
├── models/         # Data models and validation
├── validators/     # Input validation
└── utils/          # Configuration loading

tests/              # Comprehensive test suite
app.py              # Flask web application
```

## Technology Stack

- **Backend:** Python 3.9+, Flask
- **Data:** pandas, python-dateutil, holidays
- **Testing:** pytest, pytest-xdist, pytest-cov
- **Packaging:** uv, pyproject.toml
- **Frontend:** HTML5, vanilla JavaScript

## Project Philosophy

1. **Simple by default** - Web UI, local running, no complex deployment
2. **Maintainable** - Clear code, comprehensive tests, thorough documentation
3. **Extensible** - Well-defined extension points for future features
4. **Military-grade quality** - Every feature tested, documented, validated

---

For detailed information, see the documentation in the `docs/` directory.
