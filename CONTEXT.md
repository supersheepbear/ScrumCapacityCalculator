# Context: Scrum Capacity Calculator

## Core Concepts

**Capacity**
: The amount of work time a team member has available during a Sprint, measured in hours. Calculated by taking working days in the Sprint period and subtracting PTO, then converting to hours based on the member's daily work hours.

**Sprint**
: A fixed time period of 2 weeks (10 working days by default) during which a Scrum team works on planned tasks. Defined by a name, start date, and end date.

**PI (Program Increment)**
: A larger planning period spanning 12 weeks, containing 6 consecutive Sprints. Capacity must be calculated and displayed per Sprint, not aggregated across the entire PI.

**Working Day**
: Any day that is not a weekend, public holiday, or PTO day. Weekends are Saturday and Sunday by default, but configurable.

**PTO (Paid Time Off)**
: Personal time off taken by an individual team member. Recorded per person with date and duration (hours or days). Deducted from that person's capacity only.

**Holiday (Public Holiday)**
: A non-working day that applies to all team members in a specific location. Defined per office location (e.g., Beijing, Shanghai, Seattle). Can be automatically loaded from country holiday calendars or manually specified.

**Planned Work**
: The estimated work effort for tasks assigned to team members in a Sprint, imported from Jira. Measured in the same unit as Capacity (hours) to enable direct comparison.

**Assignee**
: The team member responsible for completing a task in Jira. Each task must have exactly one Assignee for capacity calculation purposes.

**Load Rate**
: The ratio of Planned Work to Capacity for a team member, expressed as a percentage. Used to identify overloaded members.
- Normal: < 80%
- Warning: 80-100%
- Overload: > 100%

**Team Member**
: A person working on the Scrum team. Has properties:
- Name (used in reports)
- Jira name (for matching with Jira data, may differ from display name)
- Daily work hours (may vary per person, e.g., 8h full-time, 6h part-time)
- Office location (determines which holidays apply)

**Office Location**
: A geographic location that determines which public holidays apply to team members. Examples: Beijing, Shanghai, Seattle, Bangalore.

**Unassigned Task**
: A Jira task with no Assignee. Not counted toward any individual's capacity. Reported separately to alert Scrum Master.

**Unestimated Task**
: A Jira task with missing or zero effort estimate. Not counted in planned work. Reported separately to alert need for estimation.

## Relationships

- A Sprint contains multiple Team Members, each with their own Capacity
- Each Team Member belongs to one Office Location
- Each Office Location has a set of Holidays
- Each Team Member may have multiple PTO entries within a Sprint
- A Holiday, PTO, and Weekend on the same date are counted only once (no double deduction)
- Planned Work is distributed across Team Members based on Jira Assignee
- Load Rate is calculated per Team Member per Sprint

## Invariants

- Sprint duration is always 2 weeks (14 calendar days)
- Each task has at most one Assignee (multi-assignee tasks must be split)
- Capacity and Planned Work must use the same unit (hours)
- Dates are in ISO 8601 format (YYYY-MM-DD), local time, timezone-agnostic
- A day cannot contribute negatively to capacity (minimum 0)

## Future Extensions

- **PI View**: Display 6 Sprints side-by-side with individual capacity calculations
- **Jira API Integration**: Real-time data pull instead of CSV import
- **Historical Tracking**: Save and compare capacity reports across Sprints
- **Multi-team Support**: Manage multiple team configurations
