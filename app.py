"""Flask web application for Scrum Capacity Calculator."""

from flask import Flask, render_template, request, jsonify
import traceback
import threading
import webbrowser

from scrum_capacity_calculator.core.calculator import CapacityCalculator
from scrum_capacity_calculator.core.jira_parser import JiraParser
from scrum_capacity_calculator.utils.config_loader import ConfigLoader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/')
def index():
    """Render main input form."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate capacity and return results."""
    try:
        # Get form data
        config_data = request.form.get('config_json')
        jira_csv = request.form.get('jira_csv')

        if not config_data:
            return jsonify({
                'success': False,
                'error': 'Configuration data is required'
            }), 400

        if request.form.get('estimate_unit') != 'hours':
            return jsonify({
                'success': False,
                'error': 'Confirm that Jira Estimate values are hours. Story Points and seconds cannot be compared with capacity hours.'
            }), 400

        if not jira_csv:
            return jsonify({
                'success': False,
                'error': 'Jira CSV data is required'
            }), 400

        # Load configuration
        config_loader = ConfigLoader()
        success, parsed_config, config_errors = config_loader.load_from_string(config_data)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Configuration validation failed',
                'details': config_errors
            }), 400

        # Parse Jira CSV
        jira_parser = JiraParser()
        try:
            tasks = jira_parser.parse_csv(jira_csv)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Jira CSV parsing failed',
                'details': [str(e)]
            }), 400

        # Check for multi-assignee tasks
        multi_assignee_errors = jira_parser.validate_single_assignee(tasks)
        if multi_assignee_errors:
            return jsonify({
                'success': False,
                'error': 'Multi-assignee tasks detected',
                'details': multi_assignee_errors
            }), 400

        sprint_name = parsed_config['sprint'].sprint_name
        if not any(task.sprint == sprint_name for task in tasks):
            return jsonify({
                'success': False,
                'error': f"No Jira tasks match Sprint '{sprint_name}'. Check the Sprint name and CSV."
            }), 400

        # Calculate capacity
        calculator = CapacityCalculator()
        sprint = parsed_config['sprint']
        members = parsed_config['members']
        locations = parsed_config['locations']
        ptos = parsed_config['ptos']

        results = calculator.calculate_capacity_results(
            members, sprint, locations, ptos, tasks, parsed_config['group_holidays']
        )
        summary = calculator.calculate_team_summary(results)
        unassigned = calculator.get_unassigned_tasks(sprint, tasks)
        unestimated = calculator.get_unestimated_tasks(sprint, tasks)
        unmatched = calculator.get_unmatched_assignees(members, sprint, tasks)

        # Prepare response
        response_data = {
            'success': True,
            'sprint': {
                'name': sprint.sprint_name,
                'start_date': sprint.start_date.isoformat(),
                'end_date': sprint.end_date.isoformat(),
                'duration_days': sprint.duration_days
            },
            'results': [
                {
                    'member_name': r.member_name,
                    'location': r.location,
                    'capacity_hours': r.capacity_hours,
                    'planned_hours': r.planned_hours,
                    'remaining_hours': r.remaining_hours,
                    'load_rate': r.load_rate,
                    'status': r.status
                }
                for r in results
            ],
            'summary': {
                'total_capacity': summary.total_capacity,
                'total_planned': summary.total_planned,
                'total_remaining': summary.total_remaining,
                'average_load_rate': summary.average_load_rate,
                'overloaded_count': summary.overloaded_count,
                'total_members': summary.total_members
            },
            'warnings': {
                'unassigned_tasks': [
                    {
                        'issue_key': t.issue_key,
                        'summary': t.summary,
                        'estimate': t.estimate
                    }
                    for t in unassigned
                ],
                'unestimated_tasks': [
                    {
                        'issue_key': t.issue_key,
                        'summary': t.summary,
                        'assignee': t.assignee
                    }
                    for t in unestimated
                ],
                'unmatched_assignees': [
                    {
                        'assignee': assignee,
                        'total_hours': hours
                    }
                    for assignee, hours in unmatched.items()
                ]
            },
            'config_warnings': [w for w in config_errors if w]
        }

        return jsonify(response_data)

    except Exception as e:
        # Log the full traceback for debugging
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': [str(e)]
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Scrum Capacity Calculator")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=False, host='127.0.0.1', port=5000)
