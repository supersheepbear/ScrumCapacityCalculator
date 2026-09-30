# Maintenance Guide

## Overview

This guide covers how to maintain and update the Scrum Capacity Calculator over time.

## Table of Contents

1. [Adding New Countries](#adding-new-countries)
2. [Adjusting Thresholds](#adjusting-thresholds)
3. [Updating Dependencies](#updating-dependencies)
4. [Code Organization](#code-organization)
5. [Database Schema (Future)](#database-schema-future)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Adding New Countries

The application uses the `python-holidays` library for automatic holiday detection. Most countries are already supported.

### Check if a Country is Supported

```python
import holidays

# List all available countries
print(holidays.list_supported_countries())
```

### Add a New Supported Country

1. Find the country code from the list above
2. Users can add it directly in their team configuration:

```json
"locations": [
  {
    "name": "New Office",
    "country_code": "XX",
    "manual_holidays": []
  }
]
```

That's it! No code changes needed.

### Add Manual Holidays

For countries not supported or company-specific holidays:

```json
"locations": [
  {
    "name": "Office Name",
    "country_code": "XX",
    "manual_holidays": [
      "2024-03-15",
      "2024-07-04",
      "2024-12-25"
    ]
  }
]
```

### Update Supported Countries in System Config

Edit `config/system_config.json`:

```json
{
  "supported_countries": [
    "CN", "US", "IN", "SG", "GB", 
    "DE", "FR", "JP", "XX"
  ]
}
```

This is informational only - doesn't restrict usage, just guides users.

## Adjusting Thresholds

### Capacity Load Thresholds

Edit `config/system_config.json`:

```json
{
  "capacity_thresholds": {
    "normal_max": 0.8,     // Below 80% = Normal ✅
    "warning_max": 1.0     // 80-100% = Warning ⚠️, >100% = Overload 🔴
  }
}
```

**Common Adjustments:**

- More aggressive: `"normal_max": 0.7, "warning_max": 0.9`
- More relaxed: `"normal_max": 0.85, "warning_max": 1.1`

### Default Settings

```json
{
  "default_daily_hours": 8,
  "default_weekends": [5, 6],  // Saturday=5, Sunday=6
  "date_format": "YYYY-MM-DD"
}
```

### Report Display Settings

```json
{
  "report": {
    "show_day_equivalents": true,
    "hours_per_day_for_display": 8,
    "default_sort": "load_rate_desc"
  }
}
```

**Options:**
- `default_sort`: "load_rate_desc", "load_rate_asc", "name_asc"
- `hours_per_day_for_display`: Used for "(Xd)" display conversion

## Updating Dependencies

### Update All Dependencies

```bash
# Check for outdated packages
uv pip list --outdated

# Update all dependencies
uv sync --upgrade

# Run tests after updating
uv run pytest -n auto
```

### Update Specific Package

```bash
# Update single package
uv add package-name@latest

# Or specify version
uv add pandas@2.2.0

# Update dev dependency
uv add --dev pytest@latest
```

### Security Updates

```bash
# Check for security vulnerabilities (using pip-audit)
uv add --dev pip-audit
uv run pip-audit

# Update vulnerable packages immediately
uv add package-name@safe-version
```

### Python Version Update

When upgrading Python version:

1. Update `pyproject.toml`:
```toml
requires-python = ">=3.10"
```

2. Update classifiers:
```toml
"Programming Language :: Python :: 3.10",
```

3. Reinstall:
```bash
rm -rf .venv
uv sync --all-extras
```

4. Run full test suite:
```bash
uv run pytest -n auto
```

## Code Organization

### File Structure Overview

```
src/scrum_capacity_calculator/
├── __init__.py               # Package exports
├── core/                     # Core business logic
│   ├── calculator.py         # Main capacity calculations
│   ├── calendar_service.py   # Working day logic
│   └── jira_parser.py        # CSV parsing
├── models/                   # Data models
│   └── __init__.py           # All dataclasses
├── validators/               # Input validation
│   └── config_validator.py   # JSON validation
└── utils/                    # Utilities
    └── config_loader.py      # Config file loading
```

### Adding New Modules

1. Create file in appropriate directory
2. Add exports to `__init__.py`
3. Write tests in `tests/`
4. Update documentation

**Example:**

```bash
# Create new module
touch src/scrum_capacity_calculator/utils/report_exporter.py

# Add to utils/__init__.py
echo 'from scrum_capacity_calculator.utils.report_exporter import ReportExporter' >> src/scrum_capacity_calculator/utils/__init__.py

# Create tests
touch tests/test_report_exporter.py
```

### Code Style Guidelines

- Follow PEP 8
- Use type hints everywhere
- NumPy-style docstrings
- Maximum line length: 100 characters
- Keep files under 250 lines

Format code:
```bash
uv run black src/ tests/
uv run ruff check --fix src/ tests/
```

## Database Schema (Future)

Currently, the application is stateless. For future versions with data persistence:

### Proposed Schema

```sql
-- Users/Teams
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE team_members (
    id INTEGER PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    name TEXT NOT NULL,
    jira_name TEXT,
    daily_hours REAL,
    location TEXT
);

-- Sprints
CREATE TABLE sprints (
    id INTEGER PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    sprint_name TEXT NOT NULL,
    start_date DATE,
    end_date DATE
);

-- Capacity Reports
CREATE TABLE capacity_reports (
    id INTEGER PRIMARY KEY,
    sprint_id INTEGER REFERENCES sprints(id),
    member_id INTEGER REFERENCES team_members(id),
    capacity_hours REAL,
    planned_hours REAL,
    load_rate REAL,
    calculated_at TIMESTAMP
);
```

### Migration Path

1. Install database support: `uv add sqlalchemy alembic`
2. Create models in `src/scrum_capacity_calculator/db/models.py`
3. Add Alembic migrations
4. Update calculator to save results
5. Add history viewing UI

## Performance Optimization

### Current Performance

- Calculation time: < 100ms for typical team (10 members)
- Test suite: ~7 seconds (34 tests in parallel)
- Memory usage: < 50MB

### Optimization Opportunities

#### 1. Cache Holiday Data

Currently holidays are fetched every calculation:

```python
# Before (in calendar_service.py)
def get_holidays_for_location(self, country_code, year):
    country_holidays = holidays_lib.country_holidays(country_code, years=year)
    # ...

# After (add caching)
from functools import lru_cache

@lru_cache(maxsize=128)
def get_holidays_for_location(self, country_code, year):
    # Same implementation
```

#### 2. Batch Processing

For large teams (>50 members):

```python
# Use multiprocessing for parallel calculation
from concurrent.futures import ProcessPoolExecutor

def calculate_capacity_results_parallel(members, sprint, locations, ptos, tasks):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(
            lambda m: self.calculate_member_capacity(m, sprint, ...),
            members
        ))
    return results
```

#### 3. Optimize Pandas Operations

In `jira_parser.py`, avoid row-by-row iteration:

```python
# Current: Iterating rows
for idx, row in df.iterrows():
    task = self._parse_row(row)
    tasks.append(task)

# Optimized: Vectorized operations
df['parsed'] = df.apply(self._parse_row, axis=1)
tasks = df['parsed'].tolist()
```

### Monitoring Performance

Add timing decorators:

```python
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timeit
def calculate_capacity_results(...):
    # ...
```

## Troubleshooting Common Issues

### Issue: Tests Failing After Dependency Update

**Symptoms:**
- Pytest errors
- Import failures
- Type errors

**Solution:**
```bash
# Clear cache
rm -rf .pytest_cache __pycache__

# Reinstall
rm -rf .venv
uv sync --all-extras

# Rebuild package
uv pip install -e .

# Run tests
uv run pytest -n auto
```

### Issue: Slow Test Execution

**Symptoms:**
- Tests take > 30 seconds
- Single-threaded execution

**Solution:**
```bash
# Verify parallel execution
uv run pytest -n auto -v

# Check for I/O in tests
uv run pytest --durations=10

# Profile test suite
uv run pytest --profile
```

### Issue: Import Errors in Production

**Symptoms:**
- "No module named scrum_capacity_calculator"
- Import paths not found

**Solution:**
```bash
# Ensure package is installed
uv pip install -e .

# Or use uv run for all commands
uv run python app.py
```

### Issue: Memory Leak

**Symptoms:**
- Memory usage grows over time
- Server becomes unresponsive

**Solution:**
```bash
# Profile memory usage
uv add --dev memory-profiler
uv run mprof run python app.py

# Check for circular references
import gc
gc.collect()
```

### Issue: Inconsistent Holiday Detection

**Symptoms:**
- Holidays not matching expected
- Different results on different machines

**Solution:**
```bash
# Update holidays library
uv add holidays@latest

# Verify country code
python -c "import holidays; print(holidays.country_holidays('CN', years=2024))"

# Check manual_holidays in config
```

## Backup and Recovery

### Configuration Backups

```bash
# Backup all configs
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/

# Restore
tar -xzf config_backup_20240315.tar.gz
```

### Database Backups (Future)

```bash
# SQLite backup
cp database.db database_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump scrum_capacity > backup_$(date +%Y%m%d).sql
```

## Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('capacity_calculator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In code
logger.info("Calculating capacity for team of %d members", len(members))
logger.warning("Sprint duration %d days, expected 14", duration)
logger.error("Failed to parse Jira CSV: %s", error)
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'capacity_calculator.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Health Checks

Add health check endpoint in `app.py`:

```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'dependencies': {
            'pandas': pd.__version__,
            'flask': flask.__version__
        }
    })
```

Monitor:
```bash
curl http://localhost:5000/health
```

## Deployment

### Docker Deployment (Future)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN pip install uv
COPY . .
RUN uv sync

EXPOSE 5000
CMD ["uv", "run", "python", "app.py"]
```

Build and run:
```bash
docker build -t scrum-capacity .
docker run -p 5000:5000 scrum-capacity
```

---

**Questions?** Open an issue on GitHub or consult the development team.
