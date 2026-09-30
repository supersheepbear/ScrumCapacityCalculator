# 🎯 Scrum Capacity Calculator

A simple web application to calculate Scrum team capacity and identify overloaded team members by comparing available working hours against planned work from Jira.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 📅 **Calendar-based capacity calculation** - Automatically accounts for weekends, holidays, and PTO
- 🌍 **Multi-location support** - Different holiday calendars for different office locations
- 📊 **Jira integration** - Import planned work from Jira CSV exports
- 🚨 **Overload detection** - Clearly highlights team members with too much work
- 📈 **Team summary** - Overview of total capacity, planned work, and load rates
- ⚠️ **Smart warnings** - Identifies unassigned tasks, unestimated work, and unmatched assignees
- 💾 **Report export** - Save results as HTML for sharing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/supersheepbear/ScrumBoardTool.git
   cd ScrumBoardTool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

That's it! 🎉

## 📖 Usage

### 1. Prepare Team Configuration

Create a JSON file with your team setup. You can download the template from the web interface or use this example:

```json
{
  "sprint": {
    "sprint_name": "2024-Q1-Sprint-1",
    "start_date": "2024-01-08",
    "end_date": "2024-01-19"
  },
  "team_members": [
    {
      "name": "John Doe",
      "jira_name": "john.doe",
      "daily_hours": 8,
      "location": "Beijing"
    }
  ],
  "locations": [
    {
      "name": "Beijing",
      "country_code": "CN",
      "manual_holidays": []
    }
  ],
  "ptos": [
    {
      "name": "John Doe",
      "date": "2024-01-10",
      "hours": 8
    }
  ]
}
```

### 2. Export Data from Jira

Export your sprint tasks as CSV with these required columns:
- **Issue Key** (e.g., PROJ-123)
- **Assignee** (must match `jira_name` in config)
- **Sprint** (must match `sprint_name` in config)
- **Estimate** (in hours)

### 3. Calculate Capacity

1. Upload or paste your team configuration
2. Upload or paste your Jira CSV export
3. Click "Calculate Capacity"
4. Review results and save the report

## 📊 How It Works

### Capacity Calculation

For each team member:
```
Working Days = Sprint Days - Weekends - Holidays - PTO Days
Capacity (hours) = Working Days × Daily Hours - Partial PTO Hours
```

### Load Rate

```
Load Rate = Planned Work (hours) ÷ Capacity (hours) × 100%
```

**Status Indicators:**
- 🔴 **Overload**: > 100% (more work than capacity)
- ⚠️ **Warning**: 80-100% (approaching full capacity)
- ✅ **Normal**: < 80% (healthy load)

### Rules

- Weekends are Saturday and Sunday by default
- Holidays apply per office location
- If a day is both a holiday and PTO, it's only counted once
- PTO can be partial days (e.g., 4 hours for a half day)
- Each task must have exactly one assignee

## 🗂️ Project Structure

```
ScrumBoardTool/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── config/
│   ├── system_config.json      # System settings
│   └── team_config_template.json
├── src/
│   ├── core/
│   │   ├── calculator.py       # Core capacity logic
│   │   ├── calendar_service.py # Working day calculations
│   │   └── jira_parser.py      # CSV parsing
│   ├── models/
│   │   └── __init__.py         # Data models
│   ├── validators/
│   │   └── config_validator.py # Input validation
│   └── utils/
│       └── config_loader.py    # Configuration loader
├── templates/
│   └── index.html              # Web UI
├── static/
│   └── js/
│       └── main.js             # Frontend logic
├── tests/                      # Unit tests
└── docs/                       # Documentation
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_calculator.py
```

## 🛠️ Configuration

### System Configuration

Edit `config/system_config.json` to customize:

```json
{
  "capacity_thresholds": {
    "normal_max": 0.8,
    "warning_max": 1.0
  },
  "default_daily_hours": 8,
  "default_weekends": [5, 6],
  "supported_countries": ["CN", "US", "IN", "SG", "GB"]
}
```

### Supported Countries

The application uses the [python-holidays](https://github.com/dr-prodigy/python-holidays) library for automatic holiday detection. Supported countries include:
- 🇨🇳 CN (China)
- 🇺🇸 US (United States)
- 🇮🇳 IN (India)
- 🇸🇬 SG (Singapore)
- 🇬🇧 GB (United Kingdom)
- And 100+ more

## 📝 Documentation

- [User Guide](docs/USER_GUIDE.md) - Detailed usage instructions
- [Maintenance Guide](docs/MAINTENANCE.md) - How to maintain and update
- [Extension Guide](docs/EXTENSION_GUIDE.md) - How to add new features
- [Domain Context](CONTEXT.md) - Domain terminology and concepts

## ❓ Troubleshooting

### Issue: "Missing required columns" error

**Solution:** Ensure your Jira CSV has columns named exactly: `Issue Key`, `Assignee`, `Sprint`, `Estimate`. If your Jira uses different names, you can manually rename them in the CSV.

### Issue: Tasks not matching team members

**Solution:** Check that the `Assignee` in Jira matches the `jira_name` in your team configuration. Names are case-sensitive.

### Issue: Wrong number of working days

**Solution:** Verify that:
- Sprint dates are correct (start and end inclusive)
- Correct country code is set for each location
- Manual holidays are in YYYY-MM-DD format

## 🔮 Future Enhancements

- [ ] PI (Program Increment) view with 6 sprints
- [ ] Direct Jira API integration
- [ ] Historical capacity tracking
- [ ] Multi-team support
- [ ] Excel report export
- [ ] Capacity forecasting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Holiday data from [python-holidays](https://github.com/dr-prodigy/python-holidays)
- Data processing with [pandas](https://pandas.pydata.org/)

## 📧 Support

If you have questions or need help, please open an issue on GitHub.

---

Made with ❤️ for Scrum teams
