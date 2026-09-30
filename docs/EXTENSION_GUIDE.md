# Extension Guide

## Overview

This guide shows how to extend the Scrum Capacity Calculator with new features while maintaining code quality and structure.

## Table of Contents

1. [Adding PI (Program Increment) Support](#adding-pi-support)
2. [Adding Jira API Integration](#adding-jira-api-integration)
3. [Adding New Report Formats](#adding-new-report-formats)
4. [Adding Historical Tracking](#adding-historical-tracking)
5. [Adding Multi-Team Support](#adding-multi-team-support)
6. [Extension Points](#extension-points)

## Adding PI Support

### Goal

Display 6 sprints side-by-side with individual capacity calculations.

### Step 1: Extend Data Models

Edit `src/scrum_capacity_calculator/models/__init__.py`:

```python
from typing import List

@dataclass
class PI:
    """Represents a Program Increment (6 sprints)."""
    
    pi_name: str
    sprints: List[Sprint]
    
    def __post_init__(self):
        """Validate PI data."""
        if len(self.sprints) != 6:
            raise ValueError(f"PI must contain exactly 6 sprints, got {len(self.sprints)}")
        
        # Verify sprints are consecutive
        for i in range(len(self.sprints) - 1):
            if self.sprints[i].end_date >= self.sprints[i + 1].start_date:
                raise ValueError("Sprints must be consecutive without overlap")
    
    @property
    def start_date(self):
        """Get PI start date."""
        return self.sprints[0].start_date
    
    @property
    def end_date(self):
        """Get PI end date."""
        return self.sprints[-1].end_date


@dataclass
class PICapacityResult:
    """Represents capacity results for entire PI."""
    
    pi_name: str
    sprint_results: List[List[CapacityResult]]  # One list per sprint
    sprint_summaries: List[TeamSummary]
```

### Step 2: Extend Calculator

Add to `src/scrum_capacity_calculator/core/calculator.py`:

```python
def calculate_pi_capacity(
    self,
    pi: PI,
    members: List[TeamMember],
    locations: List[Location],
    ptos: List[PTOEntry],
    tasks: List[JiraTask]
) -> PICapacityResult:
    """
    Calculate capacity for entire PI (6 sprints).
    
    Parameters
    ----------
    pi : PI
        Program Increment containing 6 sprints
    members : List[TeamMember]
        Team members
    locations : List[Location]
        Office locations
    ptos : List[PTOEntry]
        PTO entries for entire PI
    tasks : List[JiraTask]
        All Jira tasks for PI
    
    Returns
    -------
    PICapacityResult
        Capacity results for all sprints in PI
    """
    sprint_results = []
    sprint_summaries = []
    
    for sprint in pi.sprints:
        # Calculate for each sprint individually
        results = self.calculate_capacity_results(
            members, sprint, locations, ptos, tasks
        )
        summary = self.calculate_team_summary(results)
        
        sprint_results.append(results)
        sprint_summaries.append(summary)
    
    return PICapacityResult(
        pi_name=pi.pi_name,
        sprint_results=sprint_results,
        sprint_summaries=sprint_summaries
    )
```

### Step 3: Add PI Configuration

Create `config/pi_config_template.json`:

```json
{
  "pi": {
    "pi_name": "2024-PI-1",
    "sprints": [
      {
        "sprint_name": "2024-Q1-Sprint-1",
        "start_date": "2024-01-08",
        "end_date": "2024-01-19"
      },
      {
        "sprint_name": "2024-Q1-Sprint-2",
        "start_date": "2024-01-22",
        "end_date": "2024-02-02"
      }
      // ... 4 more sprints
    ]
  },
  "team_members": [...],
  "locations": [...],
  "ptos": [...]
}
```

### Step 4: Add UI Route

Add to `app.py`:

```python
@app.route('/calculate-pi', methods=['POST'])
def calculate_pi():
    """Calculate capacity for entire PI."""
    # Parse PI configuration
    # Call calculator.calculate_pi_capacity()
    # Return PI results
    pass
```

### Step 5: Create PI Template

Create `templates/pi_results.html` with 6-column layout showing all sprints.

### Step 6: Write Tests

Create `tests/test_pi_calculator.py`:

```python
def test_calculate_pi_capacity():
    """Test PI capacity calculation."""
    # Create 6 sprints
    # Calculate PI capacity
    # Verify results for each sprint
    pass
```

## Adding Jira API Integration

### Goal

Fetch tasks directly from Jira API instead of CSV import.

### Step 1: Add Dependencies

```bash
uv add jira python-dotenv
```

### Step 2: Create Jira Client

Create `src/scrum_capacity_calculator/integrations/jira_client.py`:

```python
"""Jira API client for fetching sprint data."""

from jira import JIRA
from typing import List
import os
from dotenv import load_dotenv

from scrum_capacity_calculator.models import JiraTask


class JiraClient:
    """Client for Jira API integration."""
    
    def __init__(self, server: str = None, email: str = None, api_token: str = None):
        """
        Initialize Jira client.
        
        Parameters
        ----------
        server : str
            Jira server URL (e.g., 'https://your-domain.atlassian.net')
        email : str
            User email for authentication
        api_token : str
            API token (not password)
        """
        load_dotenv()
        
        self.server = server or os.getenv('JIRA_SERVER')
        self.email = email or os.getenv('JIRA_EMAIL')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        
        if not all([self.server, self.email, self.api_token]):
            raise ValueError("Jira credentials not configured")
        
        self.jira = JIRA(
            server=self.server,
            basic_auth=(self.email, self.api_token)
        )
    
    def fetch_sprint_tasks(self, sprint_name: str) -> List[JiraTask]:
        """
        Fetch all tasks for a sprint.
        
        Parameters
        ----------
        sprint_name : str
            Name of the sprint
        
        Returns
        -------
        List[JiraTask]
            List of tasks in the sprint
        """
        # JQL query
        jql = f'Sprint = "{sprint_name}"'
        
        issues = self.jira.search_issues(jql, maxResults=1000)
        
        tasks = []
        for issue in issues:
            task = JiraTask(
                issue_key=issue.key,
                summary=issue.fields.summary,
                assignee=issue.fields.assignee.name if issue.fields.assignee else None,
                sprint=sprint_name,
                estimate=float(issue.fields.timeoriginalestimate or 0) / 3600  # seconds to hours
            )
            tasks.append(task)
        
        return tasks
    
    def fetch_board_sprints(self, board_id: int, state: str = 'active') -> List[dict]:
        """
        Fetch sprints from a board.
        
        Parameters
        ----------
        board_id : int
            Jira board ID
        state : str
            Sprint state: 'active', 'future', 'closed'
        
        Returns
        -------
        List[dict]
            List of sprint information
        """
        sprints = self.jira.sprints(board_id, state=state)
        return [
            {
                'id': s.id,
                'name': s.name,
                'start_date': s.startDate,
                'end_date': s.endDate
            }
            for s in sprints
        ]
```

### Step 3: Add Configuration

Create `.env.template`:

```bash
# Jira API Configuration
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Get API token from: https://id.atlassian.com/manage-profile/security/api-tokens
```

### Step 4: Update UI

Add "Import from Jira" button with fields:
- Board ID or Sprint Name
- Credentials (or use .env)

### Step 5: Write Tests

Create `tests/test_jira_client.py` with mocked API calls:

```python
from unittest.mock import Mock, patch

def test_fetch_sprint_tasks():
    """Test fetching tasks from Jira API."""
    with patch('jira.JIRA') as mock_jira:
        # Mock API response
        # Test client.fetch_sprint_tasks()
        pass
```

## Adding New Report Formats

### Goal

Export reports as Excel, PDF, or other formats.

### Step 1: Add Dependencies

```bash
uv add openpyxl reportlab
```

### Step 2: Create Report Generators

Create `src/scrum_capacity_calculator/reports/excel_generator.py`:

```python
"""Excel report generator."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List
from io import BytesIO

from scrum_capacity_calculator.models import CapacityResult, TeamSummary


class ExcelReportGenerator:
    """Generates Excel reports from capacity results."""
    
    def generate(
        self,
        results: List[CapacityResult],
        summary: TeamSummary,
        sprint_name: str
    ) -> BytesIO:
        """
        Generate Excel report.
        
        Parameters
        ----------
        results : List[CapacityResult]
            Individual capacity results
        summary : TeamSummary
            Team summary
        sprint_name : str
            Sprint name
        
        Returns
        -------
        BytesIO
            Excel file as bytes
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Capacity Report"
        
        # Title
        ws['A1'] = f"Capacity Report: {sprint_name}"
        ws['A1'].font = Font(size=16, bold=True)
        
        # Summary section
        row = 3
        ws[f'A{row}'] = "Team Summary"
        ws[f'A{row}'].font = Font(bold=True)
        
        row += 1
        ws[f'A{row}'] = "Total Capacity"
        ws[f'B{row}'] = summary.total_capacity
        
        row += 1
        ws[f'A{row}'] = "Total Planned"
        ws[f'B{row}'] = summary.total_planned
        
        # ... more summary fields
        
        # Individual results table
        row += 3
        headers = ['Member', 'Location', 'Capacity', 'Planned', 'Remaining', 'Load Rate', 'Status']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
        
        # Data rows
        for result in results:
            row += 1
            ws.cell(row=row, column=1).value = result.member_name
            ws.cell(row=row, column=2).value = result.location
            ws.cell(row=row, column=3).value = result.capacity_hours
            ws.cell(row=row, column=4).value = result.planned_hours
            ws.cell(row=row, column=5).value = result.remaining_hours
            ws.cell(row=row, column=6).value = f"{result.load_rate * 100:.1f}%"
            ws.cell(row=row, column=7).value = result.status.upper()
            
            # Color code by status
            status_color = {
                'overload': 'FFCCCC',
                'warning': 'FFFFCC',
                'normal': 'CCFFCC'
            }
            fill = PatternFill(
                start_color=status_color.get(result.status, 'FFFFFF'),
                end_color=status_color.get(result.status, 'FFFFFF'),
                fill_type='solid'
            )
            for col in range(1, 8):
                ws.cell(row=row, column=col).fill = fill
        
        # Auto-size columns
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 2
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
```

### Step 3: Add Export Routes

```python
@app.route('/export/excel', methods=['POST'])
def export_excel():
    """Export report as Excel."""
    # Get results from session or request
    # Generate Excel
    # Return as download
    generator = ExcelReportGenerator()
    excel_file = generator.generate(results, summary, sprint_name)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'capacity_report_{sprint_name}.xlsx'
    )
```

## Adding Historical Tracking

### Goal

Store and compare capacity reports across sprints.

### Step 1: Add Database

```bash
uv add sqlalchemy alembic
```

### Step 2: Create Models

Create `src/scrum_capacity_calculator/db/models.py`:

```python
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship('Member', back_populates='team')
    sprints = relationship('Sprint', back_populates='team')


class Member(Base):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    name = Column(String(100), nullable=False)
    jira_name = Column(String(100))
    daily_hours = Column(Float, nullable=False)
    
    team = relationship('Team', back_populates='members')
    capacity_reports = relationship('CapacityReport', back_populates='member')


class Sprint(Base):
    __tablename__ = 'sprints'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    sprint_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    team = relationship('Team', back_populates='sprints')
    capacity_reports = relationship('CapacityReport', back_populates='sprint')


class CapacityReport(Base):
    __tablename__ = 'capacity_reports'
    
    id = Column(Integer, primary_key=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'))
    member_id = Column(Integer, ForeignKey('members.id'))
    capacity_hours = Column(Float)
    planned_hours = Column(Float)
    load_rate = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    sprint = relationship('Sprint', back_populates='capacity_reports')
    member = relationship('Member', back_populates='capacity_reports')
```

### Step 3: Initialize Database

```bash
# Initialize Alembic
uv run alembic init alembic

# Create migration
uv run alembic revision --autogenerate -m "Initial schema"

# Apply migration
uv run alembic upgrade head
```

### Step 4: Add History View

Create route to view historical data:

```python
@app.route('/history/<team_name>')
def view_history(team_name):
    """View historical capacity data."""
    # Query database for past sprints
    # Display trend charts
    pass
```

## Adding Multi-Team Support

### Goal

Manage multiple teams in one instance.

### Step 1: Add Team Selection

Update UI to allow team selection or switching.

### Step 2: Update Configuration

```json
{
  "teams": [
    {
      "team_name": "Platform Team",
      "sprint": {...},
      "team_members": [...],
      "locations": [...],
      "ptos": [...]
    },
    {
      "team_name": "Frontend Team",
      "sprint": {...},
      "team_members": [...],
      "locations": [...],
      "ptos": [...]
    }
  ]
}
```

### Step 3: Update Calculator

Add team context to all operations.

## Extension Points

### Abstract Interfaces for Easy Extension

#### Holiday Provider Interface

```python
from abc import ABC, abstractmethod

class HolidayProvider(ABC):
    """Abstract interface for holiday data sources."""
    
    @abstractmethod
    def get_holidays(self, location: str, year: int) -> Set[date]:
        """Get holidays for location and year."""
        pass


class AutoHolidayProvider(HolidayProvider):
    """Uses python-holidays library."""
    
    def get_holidays(self, location: str, year: int) -> Set[date]:
        # Implementation using holidays library
        pass


class CustomHolidayProvider(HolidayProvider):
    """Custom holiday calendar."""
    
    def get_holidays(self, location: str, year: int) -> Set[date]:
        # Read from custom API or database
        pass
```

#### Data Source Interface

```python
class TaskDataSource(ABC):
    """Abstract interface for task data sources."""
    
    @abstractmethod
    def fetch_tasks(self, sprint_name: str) -> List[JiraTask]:
        """Fetch tasks for a sprint."""
        pass


class CSVDataSource(TaskDataSource):
    """Current CSV implementation."""
    pass


class JiraAPIDataSource(TaskDataSource):
    """Jira API implementation."""
    pass


class DatabaseDataSource(TaskDataSource):
    """Database cached implementation."""
    pass
```

---

**Ready to extend?** Follow these guides and maintain test coverage above 80%. All new features should include tests before merging.
