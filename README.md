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

## Excel workbook

Managers who prefer Excel can use the [Scrum Team Capacity workbook](outputs/excel-capacity-20260929-01/Scrum_Team_Capacity.xlsx). It is a macro-free template for one two-week Sprint, with space for 25 team members and 2,000 Jira issues. Enter data in the yellow cells; gray cells contain checks or calculations.

1. In **Team Setup**, enter the Sprint name and dates, then add each member's exact Jira assignee, group, office location, and daily hours. Add each office location and each unique group/location calendar. Country codes are a reference only. Public holiday dates must be entered on **Time Off**; mark an office or group calendar **Yes** only after checking that all relevant dates are listed.
2. On **Time Off**, enter office-wide holidays with `All` in **Group or All**, or enter the exact group for a group-specific holiday. Add PTO with the member's name, date, and hours. Duplicate holiday dates count once, PTO is capped at the person's daily hours, and weekends or holidays do not also deduct PTO.
3. To import Jira CSV data, open the export in Excel (use **Data > From Text/CSV** if you need to choose comma, semicolon, or tab), map its rows to **Issue Key**, **Summary**, **Assignee**, **Sprint**, and **Estimate (hours)**, then paste the data rows into columns A:E below the headers on **Jira Tasks**. Keep one assignee per issue and use numeric estimates in hours. The checks in columns F:G flag data that needs attention.
4. On **Capacity**, review the Sprint, Team setup, Holiday / PTO, and Jira data checks. Share the results only when they all show **Ready**. **Daily Capacity** shows the date-by-date calculation behind each member's total.

To export results as CSV, first finish the Ready checks, select **Capacity**, then use **File > Save As > CSV UTF-8** and choose a new filename. Excel exports only the active sheet to CSV; keep the original `.xlsx` to retain the setup, audit details, and formulas. The web app above separately supports setup CSV/JSON import and export.

## Calculation rules

- Saturday and Sunday are excluded. National holidays, extra location holidays, and extra group days off apply to the relevant members.
- PTO is deducted only on a day when the member would otherwise work. Multiple PTO entries on the same date are capped at that member's daily hours. Overlap with weekends or holidays is not deducted twice.
- Capacity = working days * personal hours per day - applicable PTO hours.
- Remaining = capacity - planned hours. Load rate = planned hours / capacity. If capacity is zero, the load rate is shown as N/A; planned work still marks the member as overloaded.
- Team load rate = total planned hours / total capacity. Above 100% is overloaded; 80% to 100% is near capacity.

This version calculates one Sprint. A future PI view must calculate and display all six Sprints separately. See [SPEC.md](SPEC.md) for scope and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for maintenance.
