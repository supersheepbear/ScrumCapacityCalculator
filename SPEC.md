# Scrum Capacity Calculator - Specification

## Overview

A local web application for calculating and visualizing Scrum team capacity. Helps Scrum Masters identify overloaded team members by comparing available capacity against planned work from Jira.

## Goals

1. Calculate individual team member capacity based on calendar, holidays, and PTO
2. Import planned work from Jira exports
3. Identify overloaded team members
4. Generate clear, shareable capacity reports

## Non-Goals (First Version)

- PI (6-sprint) view - deferred to future version
- Real-time Jira API integration - CSV import only
- Historical data tracking - manual save only
- Multi-team management - single team only

## User Workflow

1. Start local web server: `python app.py`
2. Open browser to `http://localhost:5000`
3. Input data via:
   - Upload `team_config.json` OR fill web form
   - Upload Jira CSV export
4. Click "Calculate Capacity"
5. View results in browser
6. Optionally save HTML report or download configuration

## Data Model

### Team Member
```json
{
  "name": "John Doe",
  "jira_name": "john.doe",
  "daily_hours": 8,
  "location": "Beijing"
}
```

### Sprint
```json
{
  "sprint_name": "2024-Q1-Sprint-1",
  "start_date": "2024-01-08",
  "end_date": "2024-01-19"
}
```

### PTO Entry
```json
{
  "name": "John Doe",
  "date": "2024-01-10",
  "hours": 8
}
```

### Holiday Configuration
```json
{
  "location": "Beijing",
  "country_code": "CN",
  "manual_holidays": ["2024-01-15"]
}
```

### Jira Task (from CSV)
```csv
Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-123,Feature A,john.doe,2024-Q1-Sprint-1,16
```

## Capacity Calculation Logic

### Step 1: Calculate Working Days
```
working_days = days_in_sprint_range 
               - weekends 
               - holidays_for_location 
               - pto_days
```

**Rules:**
- Weekend = Saturday (5) and Sunday (6) by default
- If a day is weekend AND holiday, count it only once
- If a day is holiday AND PTO, count it only once
- PTO can be partial days (e.g., 4 hours = 0.5 days for 8h/day person)

### Step 2: Convert to Hours
```
capacity_hours = working_days * member.daily_hours
```

### Step 3: Match Planned Work
```
planned_hours = SUM(jira_tasks.estimate WHERE assignee = member.jira_name)
```

### Step 4: Calculate Metrics
```
remaining_capacity = capacity_hours - planned_hours
load_rate = planned_hours / capacity_hours * 100%
```

## Validation Rules

### Configuration Validation
- All dates must be in `YYYY-MM-DD` format
- Sprint end_date must be after start_date
- Sprint duration should be 14 calendar days (warning if not)
- daily_hours must be > 0 and <= 24
- Member names must be unique
- Location names must be unique

### Jira CSV Validation
- Required columns: `Assignee`, `Sprint`, `Estimate`
- Estimate must be numeric or empty
- If Assignee is empty, task goes to "Unassigned" list
- If Estimate is 0 or empty, task goes to "Unestimated" list
- If task has multiple assignees, reject with error message

### Name Matching
- Match Jira Assignee to member.jira_name (if provided)
- Fall back to member.name if jira_name not configured
- Case-sensitive exact match
- Report unmatched assignees as warnings

## Output Specification

### Individual Capacity Table

| Member | Location | Capacity | Planned | Remaining | Load Rate | Status |
|--------|----------|----------|---------|-----------|-----------|--------|
| John Doe | Beijing | 80h (10d) | 88h | -8h | 110% | 🔴 Overload |
| Jane Smith | Shanghai | 60h (10d) | 48h | 12h | 80% | ⚠️ Warning |
| Bob Lee | Beijing | 80h (10d) | 40h | 40h | 50% | ✅ Normal |

**Status Indicators:**
- 🔴 Overload: load_rate > 100%
- ⚠️ Warning: 80% <= load_rate <= 100%
- ✅ Normal: load_rate < 80%

**Sort Order:**
- Default: by load_rate descending (overloaded first)
- User can click column headers to re-sort

### Team Summary

```
Team Capacity Summary
━━━━━━━━━━━━━━━━━━━━━━━
Total Capacity:     220h (27.5d)
Total Planned:      176h (22d)
Total Remaining:    44h (5.5d)
Average Load Rate:  80%
Overloaded Members: 1 / 3
```

### Warnings & Alerts

**Unassigned Tasks:**
```
⚠️ The following tasks have no assignee:
- PROJ-456: Feature B (16h)
- PROJ-789: Bug Fix (8h)
Total unassigned: 24h
```

**Unestimated Tasks:**
```
⚠️ The following tasks have no estimate:
- PROJ-999: Research task (Assignee: john.doe)
```

**Unmatched Assignees:**
```
⚠️ The following Jira assignees don't match any team member:
- external.contractor (24h planned work)
```

## Technical Architecture

### File Structure (All files < 250 lines)

```
ScrumBoardTool/
├── README.md
├── requirements.txt
├── app.py                          # Flask routes only
├── config/
│   ├── system_config.json          # Thresholds, defaults
│   └── team_config_template.json   # Example template
├── src/
│   ├── core/
│   │   ├── calculator.py           # Core capacity calculation
│   │   ├── calendar_service.py     # Working day calculation
│   │   └── jira_parser.py          # CSV parsing
│   ├── models/
│   │   ├── team_member.py          # Data classes
│   │   ├── sprint.py
│   │   ├── capacity_result.py
│   │   └── config.py
│   ├── validators/
│   │   ├── config_validator.py
│   │   └── csv_validator.py
│   └── utils/
│       ├── date_utils.py
│       └── report_generator.py
├── templates/
│   ├── index.html                  # Input form
│   └── results.html                # Results display
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── tests/
│   ├── test_calculator.py
│   ├── test_calendar_service.py
│   ├── test_jira_parser.py
│   └── fixtures/
│       ├── sample_team_config.json
│       └── sample_jira_export.csv
└── docs/
    ├── USER_GUIDE.md
    ├── MAINTENANCE.md
    └── EXTENSION_GUIDE.md
```

### Technology Stack

- **Backend:** Python 3.8+ with Flask
- **Dependencies:**
  - Flask (web framework)
  - pandas (CSV/data processing)
  - holidays (auto holiday detection)
  - python-dateutil (date calculations)
- **Frontend:** HTML5, CSS3, vanilla JavaScript (no heavy frameworks)
- **Testing:** pytest

### Extension Points

1. **Holiday Providers:** Abstract interface for holiday sources
   - `AutoHolidayProvider` (uses `holidays` library)
   - `ManualHolidayProvider` (reads from config)

2. **Data Importers:** Abstract interface for task data sources
   - `CSVImporter` (first version)
   - `JiraAPIImporter` (future)

3. **Report Formats:** Abstract interface for output formats
   - `HTMLReportGenerator` (first version)
   - `ExcelReportGenerator` (future)
   - `PDFReportGenerator` (future)

## Error Handling

### User-Facing Errors

All errors should have:
1. **Short message:** User-friendly description
2. **Details:** Technical specifics (expandable)
3. **Suggestion:** How to fix

Example:
```
❌ Date Format Error

The sprint start date format is incorrect.

Details:
  Expected format: YYYY-MM-DD
  Actual input: 01/08/2024
  
Suggestion:
  Please use ISO format: 2024-01-08
```

### Error Categories

1. **Validation Errors:** Bad input format (show on form)
2. **Business Logic Errors:** Invalid combinations (e.g., end before start)
3. **File Errors:** Missing columns, parse failures
4. **System Errors:** Unexpected failures (log + generic message)

## Configuration Management

### System Configuration (src/config/system_config.json)

```json
{
  "capacity_thresholds": {
    "normal_max": 0.8,
    "warning_max": 1.0
  },
  "date_format": "YYYY-MM-DD",
  "default_daily_hours": 8,
  "default_weekends": [5, 6],
  "supported_countries": ["CN", "US", "IN", "SG", "GB"],
  "report": {
    "show_day_equivalents": true,
    "hours_per_day_for_display": 8,
    "default_sort": "load_rate_desc"
  }
}
```

### Team Configuration (user-provided)

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
      "manual_holidays": ["2024-01-15"]
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

## Testing Strategy

### Unit Tests (Core Logic)

1. **Calendar Service:**
   - Working days with no holidays/PTO
   - Working days with holidays
   - Working days with PTO
   - Overlapping weekend + holiday (no double count)
   - Overlapping holiday + PTO (no double count)
   - Partial day PTO

2. **Calculator:**
   - Single member capacity calculation
   - Multiple members
   - Members with different daily hours
   - Members in different locations
   - Load rate calculations
   - Edge case: zero capacity (all days off)
   - Edge case: zero planned work

3. **Jira Parser:**
   - Valid CSV parsing
   - Missing required columns
   - Empty assignee
   - Zero/empty estimate
   - Invalid estimate format
   - Sprint name matching

### Integration Tests

1. End-to-end calculation with sample data
2. Config file upload and parsing
3. CSV upload and processing
4. Report generation

### Test Fixtures

- `sample_team_config.json`: Valid config with 3 members
- `sample_jira_export.csv`: Valid Jira export with 10 tasks
- `invalid_*.json/csv`: Various malformed inputs for error testing

## Documentation Requirements

### README.md
- Project overview
- Quick start (3 steps: install, configure, run)
- Screenshot of UI
- Link to detailed guides

### USER_GUIDE.md
- Detailed installation steps
- Configuration examples
- How to export from Jira
- Troubleshooting common issues
- FAQ

### MAINTENANCE.md
- How to add a new country/location
- How to adjust thresholds
- How to update dependencies
- Code organization explanation

### EXTENSION_GUIDE.md
- How to add PI support
- How to add Jira API integration
- How to add new report formats
- Extension point interfaces

## Success Criteria

The first version is complete when:

1. ✅ User can input team config via upload or web form
2. ✅ User can upload Jira CSV
3. ✅ System correctly calculates capacity for all members
4. ✅ System correctly handles holidays, PTO, weekends
5. ✅ System displays clear results with status indicators
6. ✅ System shows team summary
7. ✅ System reports unassigned/unestimated/unmatched items
8. ✅ All validation errors show helpful messages
9. ✅ Core logic has >80% test coverage
10. ✅ Documentation is complete and accurate
11. ✅ Code files are all <250 lines
12. ✅ System runs on fresh Python environment with just `pip install -r requirements.txt`

## Future Enhancements (Out of Scope for v1)

- PI view (6 sprints side-by-side)
- Jira API real-time integration
- Historical report storage and comparison
- Multi-team support
- Excel export
- Custom weekend configuration per location
- Capacity forecasting
- Velocity tracking
- Team member time allocation across multiple projects
