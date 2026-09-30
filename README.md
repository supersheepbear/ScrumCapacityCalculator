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

Click **Load example** to try a calculation immediately. Download the team configuration as JSON and import it for the next Sprint, then update the dates and PTO. The server does not save the configuration. Results can be printed or saved as PDF.

Required CSV columns:

```csv
Issue Key,Summary,Assignee,Sprint,Estimate
TASK-1,Build feature,alice,Sprint 1,16
```

`Summary` is optional. `Sprint` must match the name on the page. `Estimate` must be hours. Story Points cannot be compared directly with hours; convert Jira exports measured in seconds before import. Unassigned tasks, unestimated tasks, and unmatched assignees appear below the results.

## Calculation rules

- Saturday and Sunday are excluded. National holidays, extra location holidays, and extra group days off apply to the relevant members.
- PTO is deducted only on a day when the member would otherwise work. Multiple PTO entries on the same date are capped at that member's daily hours. Overlap with weekends or holidays is not deducted twice.
- Capacity = working days * personal hours per day - applicable PTO hours.
- Remaining = capacity - planned hours. Load rate = planned hours / capacity. If capacity is zero, the load rate is shown as N/A; planned work still marks the member as overloaded.
- Team load rate = total planned hours / total capacity. Above 100% is overloaded; 80% to 100% is near capacity.

This version calculates one Sprint. A future PI view must calculate and display all six Sprints separately. See [SPEC.md](SPEC.md) for scope and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for maintenance.
