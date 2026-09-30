# Product scope and rules

## Current version

The local web app calculates one Sprint at a time. Users enter configuration on the page, import a Jira CSV, and see each member's capacity, planned work, remaining or overloaded hours, load rate, and clear overload status. A team summary is included. Team configuration can be imported and exported as JSON or CSV; results can be exported as CSV. No Jira API, database, account, or project management workflow is required.

Both Sprint dates are inclusive. Two working weeks may be represented by Monday through the second Friday (12 inclusive calendar dates) or by the full 14-day span. Other durations produce a warning; calculations still use the entered dates rather than silently changing the range.

## Calendar

- Each member has their own hours per day.
- Saturday and Sunday are weekends.
- A location uses its country code for national holidays and can add dates.
- A group and location combination can add days off. Location holidays still apply.
- PTO records member name, date, and hours. It only reduces capacity on working dates. Entries on the same date are capped at one personal workday. Weekends, holidays, and PTO never cause duplicate deductions.

## Jira and units

- Required Jira CSV fields: issue key, assignee, Sprint, and a numeric estimate in hours. The importer accepts common header aliases and comma, semicolon, or tab delimiters. Summary is optional.
- `Estimate` is in hours and must be confirmed before import. Story Points are not converted. Values in seconds must be converted to hours before import.
- Only tasks with the exact current Sprint name and a matching Jira assignee contribute to a member's planned hours. If no task matches the Sprint, show an error instead of a misleading zero plan.
- Unassigned, unestimated, and unmatched tasks are reported separately. Duplicate issue keys within one Sprint are rejected to prevent double counting.

## Configuration CSV

The full setup CSV uses one row per `sprint`, `location`, `member`, `group_holiday`, or `pto` record. Its `record_type` column identifies the row. Multiple dates in a cell are separated by `|`. The downloadable file is a round-trip format and opens in common spreadsheet software.

## Later

A PI view may be added, but must calculate and display each of its six Sprints separately. Real-time Jira integration and broader project management features are out of scope.
