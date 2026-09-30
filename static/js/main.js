// Main JavaScript for Scrum Capacity Calculator

// File upload handlers
document.getElementById('config-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('config-json').value = event.target.result;
            showSuccess('Configuration file loaded successfully');
        };
        reader.readAsText(file);
    }
});

document.getElementById('jira-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('jira-csv').value = event.target.result;
            showSuccess('Jira CSV file loaded successfully');
        };
        reader.readAsText(file);
    }
});

// Calculate capacity
async function calculate() {
    const configJson = document.getElementById('config-json').value.trim();
    const jiraCsv = document.getElementById('jira-csv').value.trim();

    // Clear previous errors
    clearErrors();

    // Validate inputs
    if (!configJson) {
        showError('Please provide team configuration');
        return;
    }

    if (!jiraCsv) {
        showError('Please provide Jira CSV export');
        return;
    }

    // Show loading
    document.getElementById('input-form').style.display = 'none';
    document.getElementById('loading').classList.add('active');

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                config_json: configJson,
                jira_csv: jiraCsv
            })
        });

        const data = await response.json();

        // Hide loading
        document.getElementById('loading').classList.remove('active');

        if (data.success) {
            displayResults(data);
        } else {
            // Show errors
            document.getElementById('input-form').style.display = 'block';
            showError(data.error, data.details);
        }
    } catch (error) {
        document.getElementById('loading').classList.remove('active');
        document.getElementById('input-form').style.display = 'block';
        showError('Failed to calculate capacity', [error.message]);
    }
}

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');

    let html = `
        <div class="section">
            <h2 class="section-title">Sprint: ${data.sprint.name}</h2>
            <p style="color: #666; margin-bottom: 20px;">
                ${data.sprint.start_date} to ${data.sprint.end_date}
                (${data.sprint.duration_days} calendar days)
            </p>

            <!-- Team Summary -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px;">
                <h3 style="margin-bottom: 15px; font-size: 1.3em;">Team Capacity Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <div style="opacity: 0.8; font-size: 0.9em;">Total Capacity</div>
                        <div style="font-size: 1.5em; font-weight: bold;">
                            ${formatHours(data.summary.total_capacity)}
                        </div>
                    </div>
                    <div>
                        <div style="opacity: 0.8; font-size: 0.9em;">Total Planned</div>
                        <div style="font-size: 1.5em; font-weight: bold;">
                            ${formatHours(data.summary.total_planned)}
                        </div>
                    </div>
                    <div>
                        <div style="opacity: 0.8; font-size: 0.9em;">Remaining</div>
                        <div style="font-size: 1.5em; font-weight: bold;">
                            ${formatHours(data.summary.total_remaining)}
                        </div>
                    </div>
                    <div>
                        <div style="opacity: 0.8; font-size: 0.9em;">Average Load</div>
                        <div style="font-size: 1.5em; font-weight: bold;">
                            ${(data.summary.average_load_rate * 100).toFixed(1)}%
                        </div>
                    </div>
                    <div>
                        <div style="opacity: 0.8; font-size: 0.9em;">Overloaded</div>
                        <div style="font-size: 1.5em; font-weight: bold;">
                            ${data.summary.overloaded_count} / ${data.summary.total_members}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Individual Results Table -->
            <h3 style="margin-bottom: 15px; font-size: 1.2em; color: #333;">Individual Capacity</h3>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; background: white;
                              box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 15px; text-align: left; font-weight: 600; color: #555;">Member</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600; color: #555;">Location</th>
                            <th style="padding: 15px; text-align: right; font-weight: 600; color: #555;">Capacity</th>
                            <th style="padding: 15px; text-align: right; font-weight: 600; color: #555;">Planned</th>
                            <th style="padding: 15px; text-align: right; font-weight: 600; color: #555;">Remaining</th>
                            <th style="padding: 15px; text-align: right; font-weight: 600; color: #555;">Load Rate</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; color: #555;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.results.forEach((result, index) => {
        const rowBg = index % 2 === 0 ? 'white' : '#f8f9fa';
        const statusColor = getStatusColor(result.status);

        html += `
            <tr style="background: ${rowBg}; border-top: 1px solid #e0e0e0;">
                <td style="padding: 15px; font-weight: 500;">${result.member_name}</td>
                <td style="padding: 15px; color: #666;">${result.location}</td>
                <td style="padding: 15px; text-align: right; font-family: monospace;">
                    ${formatHours(result.capacity_hours)}
                </td>
                <td style="padding: 15px; text-align: right; font-family: monospace;">
                    ${formatHours(result.planned_hours)}
                </td>
                <td style="padding: 15px; text-align: right; font-family: monospace;
                           color: ${result.remaining_hours < 0 ? '#c33' : '#3c3'};">
                    ${formatHours(result.remaining_hours)}
                </td>
                <td style="padding: 15px; text-align: right; font-weight: 600; color: ${statusColor};">
                    ${(result.load_rate * 100).toFixed(1)}%
                </td>
                <td style="padding: 15px; text-align: center; font-size: 1.5em;">
                    ${result.status_icon}
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    // Add warnings section
    if (hasWarnings(data.warnings)) {
        html += generateWarningsSection(data.warnings);
    }

    // Add config warnings if any
    if (data.config_warnings && data.config_warnings.length > 0) {
        html += `
            <div class="alert" style="background: #fff3cd; border: 1px solid #ffc107; color: #856404; margin-top: 20px;">
                <strong>⚠️ Configuration Warnings:</strong>
                <ul style="margin: 10px 0 0 20px;">
                    ${data.config_warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Add action buttons
    html += `
        <div class="button-group" style="margin-top: 30px;">
            <button class="btn btn-primary" onclick="saveReport()">
                💾 Save Report
            </button>
            <button class="btn btn-secondary" onclick="startOver()">
                ← Back to Input
            </button>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Helper functions
function formatHours(hours) {
    const days = (hours / 8).toFixed(1);
    return `${hours.toFixed(1)}h (${days}d)`;
}

function getStatusColor(status) {
    const colors = {
        'overload': '#dc3545',
        'warning': '#ffc107',
        'normal': '#28a745'
    };
    return colors[status] || '#666';
}

function hasWarnings(warnings) {
    return warnings.unassigned_tasks.length > 0 ||
           warnings.unestimated_tasks.length > 0 ||
           warnings.unmatched_assignees.length > 0;
}

function generateWarningsSection(warnings) {
    let html = '<div class="section"><h3 style="color: #856404; margin-bottom: 15px;">⚠️ Warnings</h3>';

    if (warnings.unassigned_tasks.length > 0) {
        html += `
            <div class="alert" style="background: #fff3cd; border: 1px solid #ffc107; margin-bottom: 15px;">
                <strong>Unassigned Tasks (${warnings.unassigned_tasks.length}):</strong>
                <ul style="margin: 10px 0 0 20px;">
                    ${warnings.unassigned_tasks.map(t =>
                        `<li>${t.issue_key}: ${t.summary} (${t.estimate}h)</li>`
                    ).join('')}
                </ul>
                <p style="margin-top: 10px; font-style: italic;">
                    Total unassigned: ${warnings.unassigned_tasks.reduce((sum, t) => sum + t.estimate, 0)}h
                </p>
            </div>
        `;
    }

    if (warnings.unestimated_tasks.length > 0) {
        html += `
            <div class="alert" style="background: #fff3cd; border: 1px solid #ffc107; margin-bottom: 15px;">
                <strong>Unestimated Tasks (${warnings.unestimated_tasks.length}):</strong>
                <ul style="margin: 10px 0 0 20px;">
                    ${warnings.unestimated_tasks.map(t =>
                        `<li>${t.issue_key}: ${t.summary} (Assignee: ${t.assignee})</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    if (warnings.unmatched_assignees.length > 0) {
        html += `
            <div class="alert" style="background: #fff3cd; border: 1px solid #ffc107;">
                <strong>Unmatched Assignees (${warnings.unmatched_assignees.length}):</strong>
                <ul style="margin: 10px 0 0 20px;">
                    ${warnings.unmatched_assignees.map(a =>
                        `<li>${a.assignee} (${a.total_hours}h planned work)</li>`
                    ).join('')}
                </ul>
                <p style="margin-top: 10px; font-style: italic;">
                    These assignees don't match any team member in the configuration.
                </p>
            </div>
        `;
    }

    html += '</div>';
    return html;
}

function showError(message, details = []) {
    const errorContainer = document.getElementById('error-container');
    let html = `
        <div class="alert alert-error">
            <strong>❌ ${message}</strong>
    `;

    if (details && details.length > 0) {
        html += '<ul style="margin: 10px 0 0 20px;">';
        details.forEach(detail => {
            html += `<li>${detail}</li>`;
        });
        html += '</ul>';
    }

    html += '</div>';
    errorContainer.innerHTML = html;
}

function showSuccess(message) {
    const errorContainer = document.getElementById('error-container');
    errorContainer.innerHTML = `
        <div class="alert alert-success">
            <strong>✅ ${message}</strong>
        </div>
    `;
    setTimeout(() => {
        errorContainer.innerHTML = '';
    }, 3000);
}

function clearErrors() {
    document.getElementById('error-container').innerHTML = '';
}

function clearForm() {
    document.getElementById('config-json').value = '';
    document.getElementById('jira-csv').value = '';
    document.getElementById('config-file').value = '';
    document.getElementById('jira-file').value = '';
    clearErrors();
}

function startOver() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('input-form').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function saveReport() {
    const resultsHtml = document.getElementById('results').innerHTML;
    const fullHtml = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Capacity Report</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 1200px; margin: 0 auto; }
        .section { margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Scrum Capacity Report</h1>
    <p>Generated: ${new Date().toLocaleString()}</p>
    ${resultsHtml}
</body>
</html>
    `;

    const blob = new Blob([fullHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `capacity_report_${new Date().toISOString().split('T')[0]}.html`;
    a.click();
    URL.revokeObjectURL(url);
}

async function downloadTemplate() {
    try {
        const response = await fetch('/download-template');
        const content = await response.text();

        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'team_config_template.json';
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        showError('Failed to download template', [error.message]);
    }
}
