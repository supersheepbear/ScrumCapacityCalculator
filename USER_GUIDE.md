# Scrum Capacity Calculator - User Guide

## Quick Start

### Option 1: Use the Visual Config Editor (Recommended)

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Click "⚙️ Open Config Editor"** button in the header

4. **Fill in the form**:
   - **Sprint Configuration**: Set sprint name, start date, and end date
   - **Team Members**: Add each team member with their Jira username, daily hours, and location
   - **Office Locations**: Add office locations with country codes (CN, US, IN, etc.)
   - **PTO**: Add time-off entries for team members

5. **Click "✨ Generate Configuration"** - This will:
   - Validate your input
   - Generate the JSON configuration
   - Automatically redirect you to the main page with the config pre-loaded

6. **Paste your Jira CSV export** into the second text area

7. **Click "✨ Calculate Capacity"** to see the results

### Option 2: Use JSON Files Directly

1. **Prepare configuration file** (`team_config.json`):
   ```json
   {
     "sprint": {
       "sprint_name": "2024-Q1-Sprint-1",
       "start_date": "2024-01-08",
       "end_date": "2024-01-19"
     },
     "team_members": [
       {
         "name": "张三",
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
         "name": "张三",
         "date": "2024-01-10",
         "hours": 8
       }
     ]
   }
   ```

2. **Export Jira tasks as CSV** with these columns:
   - Issue Key
   - Summary
   - Assignee
   - Sprint
   - Estimate (in hours)

3. **Open the calculator** at `http://localhost:5000`

4. **Upload or paste** your configuration and Jira CSV

5. **Click Calculate** to see results

## Features

### Visual Configuration Editor

The config editor provides a user-friendly interface to:

- ✅ Add/remove team members without editing JSON
- ✅ Configure sprint dates with date picker
- ✅ Manage office locations
- ✅ Track PTO entries
- ✅ Load example data
- ✅ Download generated configuration as JSON file
- ✅ Auto-fill main page with generated config

### Capacity Calculation

The calculator shows:

- **Individual Capacity**: Each member's capacity, planned work, and load rate
- **Status Indicators**:
  - 🟢 Normal: Load < 80%
  - 🟡 Warning: Load 80-100%
  - 🔴 Overload: Load > 100%
- **Team Summary**: Total capacity, planned work, and average load
- **Warnings**:
  - Unassigned tasks
  - Unestimated tasks
  - Unmatched assignees (tasks assigned to people not in team config)

## Understanding the Results

### Capacity Calculation Formula

```
Working Days = Sprint Days - Weekends - Public Holidays - PTO
Capacity (hours) = Working Days × Daily Hours
Load Rate = Planned Hours / Capacity Hours × 100%
```

### Example

**Team Member**: 张三
- **Sprint Duration**: Jan 8 - Jan 19 (12 calendar days)
- **Weekends**: 2 days (Jan 13-14)
- **Public Holidays**: 0 days
- **PTO**: 1 day (Jan 10)
- **Working Days**: 12 - 2 - 0 - 1 = 9 days
- **Daily Hours**: 8 hours
- **Capacity**: 9 × 8 = 72 hours
- **Planned Work**: 80 hours (from Jira)
- **Load Rate**: 80 / 72 = 111% ⚠️ **Overloaded!**

## Tips

### Using the Config Editor

1. **Load Example First**: Click "📋 Load Example" to see how the form works
2. **Add Members Before Locations**: The form validates that locations exist
3. **Use Jira Usernames**: The "Jira Username" must match exactly what's in your Jira export
4. **Country Codes**: Use 2-letter ISO codes (CN, US, IN, SG, etc.)
5. **Save Config**: Use "💾 Download as File" to save your configuration for future use

### Jira CSV Export

From Jira, export with these columns:
1. Go to your sprint board
2. Click "..." → Export → CSV
3. Ensure these columns are included:
   - Issue Key (e.g., PROJ-123)
   - Assignee (username, not display name)
   - Sprint (sprint name)
   - Estimate or Story Points (convert to hours if needed)

### Public Holidays

The system automatically fetches public holidays based on:
- Office location's country code
- Sprint date range
- Uses the `holidays` Python library

## Troubleshooting

### "Configuration validation failed"

- Check JSON syntax if pasting manually
- Ensure all required fields are present
- Verify date format: YYYY-MM-DD

### "Multi-assignee tasks detected"

- Some tasks have multiple assignees
- Split these tasks in Jira or assign to a single person

### "Unmatched assignees"

- Tasks are assigned to people not in your team config
- Add missing team members or reassign tasks

### Server won't start

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process if needed (Windows)
taskkill /PID <process_id> /F

# Or use a different port
# Edit app.py, line 190: app.run(debug=True, host='0.0.0.0', port=5001)
```

## Advanced Usage

### Custom Holiday Configuration

Add manual holidays to locations:

```json
{
  "name": "Beijing",
  "country_code": "CN",
  "manual_holidays": ["2024-01-15", "2024-01-16"]
}
```

### Half-day PTO

Set PTO hours to 4 for half-day leave:

```json
{
  "name": "张三",
  "date": "2024-01-10",
  "hours": 4
}
```

### Multiple PTOs for One Person

Add multiple entries:

```json
{
  "ptos": [
    {"name": "张三", "date": "2024-01-10", "hours": 8},
    {"name": "张三", "date": "2024-01-11", "hours": 8},
    {"name": "张三", "date": "2024-01-12", "hours": 8}
  ]
}
```

## API Endpoints

- `GET /` - Main calculator page
- `GET /config-editor` - Visual configuration editor
- `POST /calculate` - Calculate capacity (JSON response)
- `GET /health` - Health check endpoint
- `GET /download-template` - Download config template

## Support

For issues or questions:
1. Check this user guide
2. Review SPEC.md for technical details
3. Check test files in `tests/` for examples
4. Review demo files: `demo_team_config.json` and `demo_jira_export.csv`
