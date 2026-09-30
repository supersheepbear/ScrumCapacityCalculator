# User Guide - Scrum Capacity Calculator

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration Guide](#configuration-guide)
3. [Using the Application](#using-the-application)
4. [Understanding Results](#understanding-results)
5. [Common Scenarios](#common-scenarios)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Getting Started

### Installation

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed installation instructions.

Quick start:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Run application
uv run python app.py
```

Open http://localhost:5000 in your browser.

### First Time Setup

1. Download the configuration template from the web interface
2. Edit it with your team information
3. Export your Jira sprint data as CSV
4. Upload both files and calculate

## Configuration Guide

### Team Configuration Structure

```json
{
  "sprint": { /* Sprint details */ },
  "team_members": [ /* List of team members */ ],
  "locations": [ /* Office locations */ ],
  "ptos": [ /* PTO entries */ ]
}
```

### Sprint Configuration

```json
"sprint": {
  "sprint_name": "2024-Q1-Sprint-1",
  "start_date": "2024-01-08",
  "end_date": "2024-01-19"
}
```

**Fields:**
- `sprint_name`: Must match the Sprint field in your Jira export
- `start_date`: Sprint start date (YYYY-MM-DD format)
- `end_date`: Sprint end date (YYYY-MM-DD format, inclusive)

**Notes:**
- Sprints should be 14 calendar days (2 weeks)
- If duration is different, you'll get a warning but calculation continues

### Team Members Configuration

```json
"team_members": [
  {
    "name": "John Doe",
    "jira_name": "john.doe",
    "daily_hours": 8,
    "location": "Beijing"
  },
  {
    "name": "Jane Smith",
    "jira_name": "jane.smith",
    "daily_hours": 6,
    "location": "Shanghai"
  }
]
```

**Fields:**
- `name`: Display name in reports
- `jira_name`: Username in Jira (must match Assignee field exactly)
- `daily_hours`: Working hours per day (can vary for part-time members)
- `location`: Office location (must match a location in locations array)

**Tips:**
- Use `jira_name` when Jira username differs from display name
- Support for part-time members (e.g., 6 hours/day, 4 hours/day)
- Names are case-sensitive

### Locations Configuration

```json
"locations": [
  {
    "name": "Beijing",
    "country_code": "CN",
    "manual_holidays": ["2024-02-10"]
  }
]
```

**Fields:**
- `name`: Location name (referenced by team members)
- `country_code`: ISO country code for automatic holidays
- `manual_holidays`: Additional company-specific holidays

**Supported Country Codes:**
- CN (China)
- US (United States)
- IN (India)
- SG (Singapore)
- GB (United Kingdom)
- DE (Germany)
- FR (France)
- JP (Japan)
- And 100+ more via python-holidays library

### PTO Configuration

```json
"ptos": [
  {
    "name": "John Doe",
    "date": "2024-01-10",
    "hours": 8
  },
  {
    "name": "Jane Smith",
    "date": "2024-01-15",
    "hours": 4
  }
]
```

**Fields:**
- `name`: Team member name (must match team_members.name exactly)
- `date`: PTO date (YYYY-MM-DD format)
- `hours`: PTO duration in hours

**PTO Types:**
- **Full day**: Set hours equal to member's daily_hours
- **Half day**: Set hours to half of daily_hours
- **Custom**: Any value between 0 and daily_hours

**Important:**
- PTO on weekends has no effect (already non-working)
- PTO on holidays doesn't double-deduct
- Multiple PTO entries for the same person are supported

## Using the Application

### Step 1: Prepare Team Configuration

Option A - Upload existing file:
1. Click "Click to upload configuration file"
2. Select your JSON file

Option B - Paste JSON:
1. Paste JSON content into the text area

Option C - Download template:
1. Click "Download Template"
2. Edit with your team data
3. Upload or paste

### Step 2: Export Jira Data

1. In Jira, navigate to your board
2. Go to Reports → Sprint Report (or your preferred export)
3. Export as CSV with these required columns:
   - **Issue Key** (e.g., PROJ-123)
   - **Assignee** (must match jira_name in config)
   - **Sprint** (must match sprint_name in config)
   - **Estimate** (in hours)

**Jira Export Tips:**
- Include all tasks in the sprint (Done, In Progress, To Do)
- Ensure estimate is in hours (not story points, unless converted)
- Check that assignee names match your configuration

### Step 3: Upload Jira Data

Option A - Upload CSV file:
1. Click "Click to upload Jira CSV file"
2. Select your exported CSV

Option B - Paste CSV:
1. Copy CSV content
2. Paste into the text area

### Step 4: Calculate

1. Click "Calculate Capacity"
2. Wait for results (usually instant)
3. Review the capacity report

### Step 5: Save Report

1. Review results
2. Click "Save Report" to download HTML file
3. Share with your team or Scrum Master

## Understanding Results

### Team Summary

Shows aggregate team metrics:
- **Total Capacity**: Sum of all team members' available hours
- **Total Planned**: Sum of all planned work from Jira
- **Remaining**: Capacity minus planned work
- **Average Load**: Team's average load percentage
- **Overloaded**: Number of members over 100% capacity

### Individual Capacity Table

For each team member:
- **Capacity**: Available working hours in the sprint
- **Planned**: Total hours of assigned tasks
- **Remaining**: Capacity minus planned (negative if overloaded)
- **Load Rate**: Planned ÷ Capacity as percentage
- **Status**: Visual indicator of load level

### Status Indicators

- 🔴 **Overload** (>100%): Member has more work than capacity
- ⚠️ **Warning** (80-100%): Member is near full capacity
- ✅ **Normal** (<80%): Member has reasonable buffer

### Warnings Section

**Unassigned Tasks:**
- Tasks with no assignee in Jira
- Not counted in any member's capacity
- Action: Assign these tasks to team members

**Unestimated Tasks:**
- Tasks with 0 or empty estimate
- Not counted in planned work
- Action: Add estimates in Jira

**Unmatched Assignees:**
- Jira assignees not found in team configuration
- Could be external contractors or old members
- Action: Add to team config or reassign tasks

## Common Scenarios

### Scenario 1: Team Member on Vacation

**Setup:**
```json
"ptos": [
  {
    "name": "John Doe",
    "date": "2024-01-10",
    "hours": 8
  },
  {
    "name": "John Doe",
    "date": "2024-01-11",
    "hours": 8
  },
  {
    "name": "John Doe",
    "date": "2024-01-12",
    "hours": 8
  }
]
```

**Result:**
- John's capacity reduced by 24 hours (3 days × 8 hours)

### Scenario 2: Part-Time Team Member

**Setup:**
```json
"team_members": [
  {
    "name": "Jane Smith",
    "jira_name": "jane.smith",
    "daily_hours": 4,
    "location": "Beijing"
  }
]
```

**Result:**
- Jane's capacity calculated based on 4 hours/day
- 10 working days × 4 hours = 40 hours total capacity

### Scenario 3: Mid-Sprint Joiner

**Workaround:**
Add PTO for days before they joined:
```json
"ptos": [
  {
    "name": "New Member",
    "date": "2024-01-08",
    "hours": 8
  },
  {
    "name": "New Member",
    "date": "2024-01-09",
    "hours": 8
  }
  // ... for all days before joining
]
```

### Scenario 4: Multiple Locations with Different Holidays

**Setup:**
```json
"locations": [
  {
    "name": "Beijing",
    "country_code": "CN",
    "manual_holidays": []
  },
  {
    "name": "Seattle",
    "country_code": "US",
    "manual_holidays": []
  }
]
```

**Result:**
- Beijing members get Chinese holidays
- Seattle members get US holidays
- Each calculated independently

### Scenario 5: Converting Story Points to Hours

**Option 1** - In Jira:
- Export with Story Points column
- Manually convert (e.g., 1 SP = 4 hours)
- Update CSV before upload

**Option 2** - In Configuration:
- Document your conversion rate
- Apply consistently across all tasks

## Troubleshooting

### Error: "Missing required columns"

**Cause:** Jira CSV doesn't have required columns

**Solution:**
1. Check CSV has these columns: Issue Key, Assignee, Sprint, Estimate
2. Column names must match exactly (case-sensitive)
3. Rename columns in CSV if needed

### Error: "Multiple assignees detected"

**Cause:** Task has multiple assignees (e.g., "john.doe,jane.smith")

**Solution:**
1. Split task in Jira into separate tasks
2. Or assign to primary person responsible

### Warning: "Sprint duration is X days, expected 14"

**Cause:** Sprint length is not standard 2 weeks

**Impact:** Calculation continues but you may want to verify dates

**Solution:**
- Check start and end dates are correct
- If intentional (short sprint), ignore warning

### Issue: Capacity seems wrong

**Checklist:**
1. Verify sprint dates are correct
2. Check daily_hours for each member
3. Confirm PTO entries are accurate
4. Verify location holidays are correct
5. Check if weekends are Saturday/Sunday

### Issue: Tasks not matching team members

**Checklist:**
1. Verify jira_name matches Jira assignee exactly
2. Check for case sensitivity
3. Look for extra spaces in names
4. Check "Unmatched Assignees" warning for details

## FAQ

### Q: Can I use Story Points instead of hours?

**A:** Not directly. You need to convert Story Points to hours before importing. Establish a conversion rate (e.g., 1 SP = 4 hours) and apply it consistently.

### Q: What if my team has different weekend days?

**A:** This is configured in system_config.json. Default is Saturday-Sunday. You can customize per location if needed (requires code modification in future version).

### Q: How do I handle carryover tasks from previous sprint?

**A:** Include them in your Jira export with the current sprint name. They'll be counted in the current sprint's planned work.

### Q: Can I track multiple sprints at once?

**A:** Not in v1.0. Run the calculator separately for each sprint. Future versions will support PI (6-sprint) view.

### Q: How accurate is the holiday detection?

**A:** Very accurate for major holidays in supported countries. Add company-specific holidays manually via manual_holidays.

### Q: What about ceremonial time (meetings, etc.)?

**A:** Reduce daily_hours to account for this. For example, if team has 2 hours of daily meetings, set daily_hours to 6 instead of 8.

### Q: Can I save my configuration for reuse?

**A:** Yes! After uploading, the browser holds it. You can also click the download template button anytime to save it locally.

### Q: How do I share results with my team?

**A:** Click "Save Report" to download an HTML file. Email it or post to your team's communication channel.

### Q: What if someone works across multiple sprints?

**A:** Each sprint is calculated independently. Run the calculator for each sprint separately.

### Q: Can this integrate directly with Jira API?

**A:** Not yet. v1.0 uses CSV import for simplicity. Direct API integration is planned for future versions.

---

**Need more help?** Open an issue on GitHub or consult the [DEVELOPMENT.md](DEVELOPMENT.md) for technical details.
