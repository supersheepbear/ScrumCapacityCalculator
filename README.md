# Scrum Team Capacity

A local tool for planning one Sprint. Enter team members, locations, group days off, and PTO; import a Jira CSV export; then see each person's available hours, planned hours, remaining hours, and load rate.

## Start

**Windows:** Double-click [start.bat](start.bat). On the first run it creates a virtual environment and installs the dependencies. It then opens the browser. Use the same file on later runs; close the command window to stop the service.

On other systems, or to start manually:

```sh
python -m venv .venv
# Activate .venv, then:
python -m pip install -e .
python app.py
```

Open <http://127.0.0.1:5000>. Python 3.10 or newer is required.

## Use

1. Enter the Sprint name and start and end dates. The end date is inclusive.
2. Add office locations and country codes. Add extra public holiday dates if needed.
3. Add each member's name, exact Jira assignee, group, location, and hours per day.
4. Optionally add days off for a specific group and location, plus personal PTO.
5. Import a Jira CSV, confirm that `Estimate` values are in **hours**, and click **Calculate capacity**.

Click **Load example** to try a calculation immediately. Download the team setup as JSON or CSV and import it for the next Sprint, then update the dates and PTO. Both files include the Sprint, locations, members, group days off, and PTO. The server does not save the configuration. Results can be exported as CSV or printed / saved as PDF.

The setup CSV is designed to open and edit in a spreadsheet. It has one `record_type` column and one row per item. The app exports the complete current setup in this format, so it can be imported again without losing data. Use `|` between multiple dates in `manual_holidays` and `dates` cells.

```csv
record_type,sprint_name,start_date,end_date,name,jira_name,group,location,country_code,daily_hours,manual_holidays,date,hours,dates
sprint,Sprint 1,2026-10-05,2026-10-16,,,,,,,,,,
location,,,,Beijing,,,,CN,,2026-10-02|2026-10-03,,,
member,,,,Alice,alice,Engineering,Beijing,,8,,,,
group_holiday,,,,,,Engineering,Beijing,,,,,,2026-10-08|2026-10-09
pto,,,,Alice,,,,,,,2026-10-12,4,
```

Use these `record_type` values: `sprint`, `location`, `member`, `group_holiday`, and `pto`. CSV import accepts comma, semicolon, and tab delimiters. JSON remains available if you prefer it.

Required CSV columns:

```csv
Issue Key,Summary,Assignee,Sprint,Estimate
TASK-1,Build feature,alice,Sprint 1,16
```

`Summary` is optional. The importer also recognizes common alternatives such as `Key`, `Owner`, `Iteration`, and `Estimate (hours)`. Jira files may use comma, semicolon, or tab delimiters. `Sprint` must match the name on the page. Estimates must be numeric hours; Story Points cannot be compared directly with hours, and values in seconds must be converted before import. Unassigned tasks, unestimated tasks, and unmatched assignees appear below the results.

## Calculation rules

- Saturday and Sunday are excluded. National holidays, extra location holidays, and extra group days off apply to the relevant members.
- PTO is deducted only on a day when the member would otherwise work. Multiple PTO entries on the same date are capped at that member's daily hours. Overlap with weekends or holidays is not deducted twice.
- Capacity = working days * personal hours per day - applicable PTO hours.
- Remaining = capacity - planned hours. Load rate = planned hours / capacity. If capacity is zero, the load rate is shown as N/A; planned work still marks the member as overloaded.
- Team load rate = total planned hours / total capacity. Above 100% is overloaded; 80% to 100% is near capacity.

This version calculates one Sprint. A future PI view must calculate and display all six Sprints separately. See [SPEC.md](SPEC.md) for scope and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for maintenance.
