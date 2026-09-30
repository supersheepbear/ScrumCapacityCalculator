const fields = {
  locations: [
    ["name", "text", "Beijing"],
    ["country_code", "text", "CN"],
    ["manual_holidays", "text", "2026-10-02, 2026-10-03"]
  ],
  members: [
    ["name", "text", "Alice"],
    ["jira_name", "text", "alice"],
    ["group", "text", "Engineering"],
    ["location", "text", "Beijing"],
    ["daily_hours", "number", "8"]
  ],
  "group-holidays": [
    ["group", "text", "Engineering"],
    ["location", "text", "Beijing"],
    ["dates", "text", "2026-10-08, 2026-10-09"]
  ],
  ptos: [
    ["name", "text", "Alice"],
    ["date", "date", ""],
    ["hours", "number", "8"]
  ]
};

function addRow(section, data = {}) {
  const row = document.createElement("tr");
  for (const [name, type, placeholder] of fields[section]) {
    const cell = document.createElement("td");
    const input = document.createElement("input");
    input.type = type;
    input.dataset.field = name;
    input.placeholder = placeholder;
    input.setAttribute("aria-label", name);
    if (type === "number") {
      input.min = "0.1";
      input.step = "0.1";
    }
    const value = data[name] ?? (
      section === "members" && name === "group" ? "Team" :
      name === "daily_hours" || name === "hours" ? 8 : ""
    );
    input.value = Array.isArray(value) ? value.join(", ") : (value ?? "");
    cell.append(input);
    row.append(cell);
  }
  const action = document.createElement("td");
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "remove";
  remove.textContent = "Remove";
  remove.addEventListener("click", () => row.remove());
  action.append(remove);
  row.append(action);
  document.getElementById(section).append(row);
}

function rows(section) {
  return Array.from(document.querySelectorAll("#" + section + " tr")).map(row => {
    const data = {};
    row.querySelectorAll("input").forEach(input => { data[input.dataset.field] = input.value.trim(); });
    if (section === "locations") data.manual_holidays = dates(data.manual_holidays);
    if (section === "group-holidays") data.dates = dates(data.dates);
    if (section === "members") data.daily_hours = Number(data.daily_hours);
    if (section === "ptos") data.hours = Number(data.hours);
    return data;
  });
}

function dates(value) {
  return value.split(",").map(date => date.trim()).filter(Boolean);
}

function config() {
  return {
    sprint: {
      sprint_name: document.getElementById("sprint-name").value.trim(),
      start_date: document.getElementById("start-date").value,
      end_date: document.getElementById("end-date").value
    },
    locations: rows("locations"),
    team_members: rows("members"),
    group_holidays: rows("group-holidays"),
    ptos: rows("ptos")
  };
}

function loadConfig(data) {
  document.getElementById("sprint-name").value = data.sprint?.sprint_name || "";
  document.getElementById("start-date").value = data.sprint?.start_date || "";
  document.getElementById("end-date").value = data.sprint?.end_date || "";
  const sections = {
    locations: data.locations || [],
    members: data.team_members || [],
    "group-holidays": data.group_holidays || [],
    ptos: data.ptos || []
  };
  for (const [section, items] of Object.entries(sections)) {
    document.getElementById(section).replaceChildren();
    items.forEach(item => addRow(section, item));
  }
  hideError();
}

function download(name, content, type) {
  const link = document.createElement("a");
  const url = URL.createObjectURL(new Blob([content], {type}));
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function csvRow(values) {
  return values.map(value => {
    const text = String(value ?? "");
    return '"' + text.replaceAll('"', '""') + '"';
  }).join(",");
}

function resultsCsv(data) {
  const rows = [[
    "record_type", "sprint_name", "member", "location", "capacity_hours", "planned_hours",
    "remaining_hours", "load_rate_percent", "status"
  ]];
  rows.push([
    "team", data.sprint.name, "Team", "",
    data.summary.total_capacity, data.summary.total_planned, data.summary.total_remaining,
    data.summary.total_capacity ? (data.summary.average_load_rate * 100).toFixed(1) : "",
    data.summary.overloaded_count + " overloaded / " + data.summary.total_members + " members"
  ]);
  for (const result of data.results) {
    rows.push([
      "member", data.sprint.name, result.member_name, result.location,
      result.capacity_hours, result.planned_hours, result.remaining_hours,
      result.load_rate === null ? "" : (result.load_rate * 100).toFixed(1),
      result.status === "overload" ? "Overloaded" : result.status === "warning" ? "Near capacity" : "Available"
    ]);
  }
  return "\ufeff" + rows.map(csvRow).join("\r\n") + "\r\n";
}

function showError(message, details = []) {
  const box = document.getElementById("error");
  box.textContent = [message, ...details].filter(Boolean).join("\n");
  box.hidden = false;
  box.scrollIntoView({behavior: "smooth", block: "center"});
}

function hideError() {
  const box = document.getElementById("error");
  box.hidden = true;
  box.textContent = "";
}

function hours(value) {
  return Number(value).toFixed(1) + " h";
}

function cell(row, value, className = "") {
  const td = document.createElement("td");
  td.textContent = value;
  td.className = className;
  row.append(td);
}

function renderResults(data) {
  const target = document.getElementById("results");
  target.replaceChildren();
  const title = document.createElement("h2");
  title.textContent = data.sprint.name + ": " + data.sprint.start_date + " to " + data.sprint.end_date;
  target.append(title);
  const summary = document.createElement("div");
  summary.className = "summary";
  const totals = [
    ["Team capacity", hours(data.summary.total_capacity)],
    ["Planned", hours(data.summary.total_planned)],
    ["Remaining", hours(data.summary.total_remaining)],
    ["Team load", data.summary.total_capacity ? (data.summary.average_load_rate * 100).toFixed(1) + "%" : "N/A"],
    ["Overloaded", data.summary.overloaded_count + " / " + data.summary.total_members]
  ];
  for (const [label, value] of totals) {
    const span = document.createElement("span");
    const strong = document.createElement("strong");
    strong.textContent = value;
    span.append(label + ": ", document.createElement("br"), strong);
    summary.append(span);
  }
  target.append(summary);
  const scroll = document.createElement("div");
  scroll.className = "scroll";
  const table = document.createElement("table");
  const head = document.createElement("thead");
  const header = document.createElement("tr");
  ["Member", "Location", "Capacity", "Planned", "Remaining / overload", "Load rate", "Status"].forEach(label => cell(header, label));
  head.append(header);
  table.append(head);
  const body = document.createElement("tbody");
  for (const result of data.results) {
    const row = document.createElement("tr");
    if (result.status === "overload") row.className = "overload";
    cell(row, result.member_name);
    cell(row, result.location);
    cell(row, hours(result.capacity_hours), "number");
    cell(row, hours(result.planned_hours), "number");
    cell(row, hours(result.remaining_hours), "number");
    cell(row, result.load_rate === null ? "N/A" : (result.load_rate * 100).toFixed(1) + "%", "number");
    cell(row, result.status === "overload" ? "Overloaded" : result.status === "warning" ? "Near capacity" : "Available");
    body.append(row);
  }
  table.append(body);
  scroll.append(table);
  target.append(scroll);
  const warnings = data.warnings;
  const notes = [
    ["Unassigned tasks", warnings.unassigned_tasks.map(task => task.issue_key)],
    ["Unestimated tasks", warnings.unestimated_tasks.map(task => task.issue_key)],
    ["Unmatched assignees", warnings.unmatched_assignees.map(item => item.assignee + " (" + hours(item.total_hours) + ")")]
  ];
  for (const [label, items] of notes) {
    if (!items.length) continue;
    const note = document.createElement("p");
    note.textContent = label + ": " + items.join(", ");
    target.append(note);
  }
  for (const warning of data.config_warnings || []) {
    const note = document.createElement("p");
    note.textContent = warning;
    target.append(note);
  }
  const actions = document.createElement("div");
  actions.className = "toolbar no-print";
  const back = document.createElement("button");
  back.textContent = "Edit inputs";
  back.onclick = () => {
    document.getElementById("input-area").hidden = false;
    target.hidden = true;
    document.body.classList.remove("show-results");
  };
  const print = document.createElement("button");
  print.textContent = "Print / Save PDF";
  print.onclick = () => window.print();
  const exportCsv = document.createElement("button");
  exportCsv.textContent = "Export results CSV";
  exportCsv.onclick = () => download("capacity_results.csv", resultsCsv(data), "text/csv;charset=utf-8");
  actions.append(back, exportCsv, print);
  target.append(actions);
  document.getElementById("input-area").hidden = true;
  target.hidden = false;
  document.body.classList.add("show-results");
  target.scrollIntoView({behavior: "smooth"});
}

async function calculate() {
  hideError();
  if (!document.getElementById("hours-confirm").checked) {
    showError("Confirm that Jira Estimate values are in hours.");
    return;
  }
  const csv = document.getElementById("jira-csv").value.trim();
  if (!csv) {
    showError("Import or paste a Jira CSV.");
    return;
  }
  const button = document.getElementById("calculate");
  button.disabled = true;
  button.textContent = "Calculating...";
  try {
    const response = await fetch("/calculate", {
      method: "POST",
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: new URLSearchParams({
        config_json: JSON.stringify(config()),
        jira_csv: csv,
        estimate_unit: "hours"
      })
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      showError(data.error || "Calculation failed", data.details || []);
      return;
    }
    renderResults(data);
  } catch (error) {
    showError("Could not connect to the local service: " + error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Calculate capacity";
  }
}

document.querySelectorAll("[data-add]").forEach(button => {
  button.addEventListener("click", () => addRow(button.dataset.add));
});
document.getElementById("calculate").addEventListener("click", calculate);
document.getElementById("save-config-json").addEventListener("click", () => {
  download("team_config.json", JSON.stringify(config(), null, 2), "application/json");
});
document.getElementById("save-config-csv").addEventListener("click", async () => {
  try {
    const response = await fetch("/config/to-csv", {
      method: "POST",
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: new URLSearchParams({config_json: JSON.stringify(config())})
    });
    if (!response.ok) {
      const data = await response.json();
      showError(data.error || "Could not export configuration CSV", data.details || []);
      return;
    }
    download("team_config.csv", await response.text(), "text/csv;charset=utf-8");
  } catch (error) {
    showError("Could not export configuration CSV: " + error.message);
  }
});
document.getElementById("config-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (/\.(csv|tsv)$/i.test(file.name) || file.type === "text/csv" || file.type === "text/tab-separated-values") {
      const response = await fetch("/config/from-csv", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({config_csv: await file.text()})
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        showError(data.error || "Could not import configuration CSV", data.details || []);
      } else {
        loadConfig(data.config);
      }
    } else {
      const parsed = JSON.parse(await file.text());
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed) ||
          !parsed.sprint || !Array.isArray(parsed.locations) || !Array.isArray(parsed.team_members)) {
        throw new Error("JSON must include sprint, locations, and team_members sections.");
      }
      loadConfig(parsed);
    }
  } catch (error) {
    showError("Could not import the configuration file: " + error.message);
  }
  event.target.value = "";
});
document.getElementById("jira-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (file) document.getElementById("jira-csv").value = await file.text();
});
document.getElementById("example").addEventListener("click", () => {
  loadConfig({
    sprint: {sprint_name: "Sprint 1", start_date: "2024-01-08", end_date: "2024-01-19"},
    locations: [{name: "Beijing", country_code: "CN", manual_holidays: []}],
    team_members: [
      {name: "Alice", jira_name: "alice", group: "Engineering", location: "Beijing", daily_hours: 8},
      {name: "Bob", jira_name: "bob", group: "QA", location: "Beijing", daily_hours: 6}
    ],
    group_holidays: [{group: "QA", location: "Beijing", dates: ["2024-01-18"]}],
    ptos: [{name: "Alice", date: "2024-01-10", hours: 4}]
  });
  document.getElementById("jira-csv").value =
    "Issue Key,Summary,Assignee,Sprint,Estimate\n" +
    "DEMO-1,Build feature,alice,Sprint 1,80\n" +
    "DEMO-2,Test feature,bob,Sprint 1,24\n";
  document.getElementById("hours-confirm").checked = true;
});
addRow("locations");
addRow("members");
