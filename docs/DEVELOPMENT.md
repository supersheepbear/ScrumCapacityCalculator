# Scrum Capacity Calculator - Development Setup

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

## Installation

### 1. Install uv (if not already installed)

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Set up the project

```bash
# Clone the repository
git clone https://github.com/supersheepbear/ScrumBoardTool.git
cd ScrumBoardTool

# Install dependencies (creates virtual environment automatically)
uv sync --all-extras
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Install development dependencies (pytest, black, ruff, etc.)

## Running the Application

```bash
# Using uv (recommended)
uv run python app.py

# Or using make
make run
```

Then open http://localhost:5000 in your browser.

## Development Workflow

### Running Tests

```bash
# Run all tests in parallel
make test

# Run with coverage report
make test-coverage

# Run specific test file
uv run pytest tests/test_calculator.py -v
```

### Code Quality

```bash
# Format code
make format

# Check linting
make lint

# Auto-fix linting issues
uv run ruff check --fix src/ tests/
```

### Project Structure

```
ScrumBoardTool/
├── src/
│   └── scrum_capacity_calculator/    # Main package
│       ├── __init__.py
│       ├── core/                     # Core calculation logic
│       ├── models/                   # Data models
│       ├── validators/               # Input validation
│       └── utils/                    # Utilities
├── tests/                            # Test suite
├── app.py                            # Flask web application
├── pyproject.toml                    # Project configuration
└── Makefile                          # Development commands
```

## Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

This automatically updates `pyproject.toml`.

## Building for Distribution

```bash
# Build package
uv build

# This creates:
# - dist/scrum_capacity_calculator-1.0.0-py3-none-any.whl
# - dist/scrum_capacity_calculator-1.0.0.tar.gz
```

## Troubleshooting

### Issue: `uv: command not found`

**Solution:** Make sure uv is installed and in your PATH. Restart your terminal after installation.

### Issue: Import errors in tests

**Solution:** Always run commands through `uv run` to ensure the virtual environment is activated:
```bash
uv run pytest
```

### Issue: Tests fail with "No module named scrum_capacity_calculator"

**Solution:** Install the package in development mode:
```bash
uv pip install -e .
```

## IDE Configuration

### VS Code

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.formatting.provider": "black",
  "python.linting.ruffEnabled": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)

## Continuous Integration

The test suite is designed for CI/CD pipelines:

```bash
# Install dependencies
uv sync

# Run tests with coverage
uv run pytest --cov=src/scrum_capacity_calculator --cov-report=xml

# Check code quality
uv run ruff check src/ tests/
uv run black --check src/ tests/
```

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
