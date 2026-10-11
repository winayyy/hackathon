
import { useState } from "react";
import "./App.css";

const API_URL = "";

export default function App() {
  const [query, setQuery] = useState(
    "SELECT id, name, city, status\nFROM customers\nLIMIT 10;"
  );

  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [activeView, setActiveView] = useState("editor");
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [exportMessage, setExportMessage] = useState("");

  async function runQuery() {
    setLoading(true);
    setError("");
    setExportMessage("");
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Query execution failed.");
      }

      setResults(data);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot reach the backend. Check that FastAPI is running on port 8001."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  async function openHistory() {
    setActiveView("history");
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const response = await fetch(`${API_URL}/api/query-history`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not load query history.");
      }

      setHistory(data);
    } catch (err) {
      setHistoryError(
        err.message === "Failed to fetch"
          ? "Cannot reach the backend. Check that FastAPI is running."
          : err.message
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  function openEditor() {
    setActiveView("editor");
  }

  // Escape CSV values and protect against spreadsheet formula injection.
  function escapeCsvValue(value) {
    let text = value == null ? "" : String(value);

    // Prefix formula-like cells so spreadsheets don't execute them.
    if (/^[\t\r ]*[=+\-@]/.test(text)) {
      text = "'" + text;
    }

    // Double quotes inside a CSV field must be escaped.
    return `"${text.replace(/"/g, '""')}"`;
  }

  function exportCsv() {
    if (!results || !Array.isArray(results.columns)) {
      return;
    }

    const headers = results.columns.map(escapeCsvValue).join(",");

    const rows = results.rows.map((row) =>
      results.columns
        .map((column) => escapeCsvValue(row[column]))
        .join(",")
    );

    // UTF-8 BOM helps Excel detect the file's encoding.
    const csvContent = "\uFEFF" + [headers, ...rows].join("\r\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    const date = new Date().toISOString().slice(0, 10);

    link.href = url;
    link.download = `dataops-export-${date}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);

    setExportMessage(
      `CSV exported successfully (${results.row_count} rows).`
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">D</div>
          <div>
            <h2>DataOps</h2>
            <span>Database Console</span>
          </div>
        </div>

        <p className="nav-heading">WORKSPACE</p>

        <button
          className={`nav-item ${activeView === "editor" ? "active" : ""}`}
          onClick={openEditor}
        >
          ⌘ Query Editor
        </button>

        <button
          className={`nav-item ${activeView === "history" ? "active" : ""}`}
          onClick={openHistory}
        >
          ▤ Query History
        </button>

        <div className="sidebar-bottom">
          <span className="status-dot connected-dot" />
          Local Environment
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>
              {activeView === "editor"
                ? "Query Workspace"
                : "Query History"}
            </h1>

            <p>
              {activeView === "editor"
                ? "Connect, query, and explore your database."
                : "Review your recent database query activity."}
            </p>
          </div>

          <span className="environment-badge">LOCAL DEMO</span>
        </header>

        <section className="connection-card">
          <div className="connection-icon">DB</div>

          <div className="connection-details">
            <h3>MySQL Database</h3>
            <p>dataops_demo · Local development</p>
          </div>

          <span className="connection-status">
            <span className="status-dot connected-dot" />
            API connected
          </span>
        </section>

        {activeView === "editor" ? (
          <>
            <section className="editor-card">
              <div className="section-header">
                <div>
                  <h3>SQL Query Editor</h3>
                  <p>Only SELECT queries are accepted by the API.</p>
                </div>

                <span className="language-badge">SQL</span>
              </div>

              <label htmlFor="sql-query">Your query</label>

              <textarea
                id="sql-query"
                className="query-editor"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                spellCheck="false"
                disabled={loading}
              />

              <div className="editor-footer">
                <span>
                  Maximum 100 rows · Read-only database user
                </span>

                <button
                  className="run-button"
                  onClick={runQuery}
                  disabled={loading || !query.trim()}
                >
                  {loading ? "Running..." : "▶ Run Query"}
                </button>
              </div>
            </section>

            {error && (
              <section
                className="message-card error-message"
                role="alert"
              >
                <strong>Query failed</strong>
                <p>{error}</p>
              </section>
            )}

            {exportMessage && !error && (
              <section className="message-card" role="status">
                <p>{exportMessage}</p>
              </section>
            )}

            {results && (
              <section className="results-card">
                <div className="section-header">
                  <div>
                    <h3>Query Results</h3>
                    <p>{results.row_count} row(s) returned</p>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      flexWrap: "wrap",
                    }}
                  >
                    <span className="language-badge">SUCCESS</span>

                    <button
                      className="run-button"
                      onClick={exportCsv}
                    >
                      ↓ Export CSV
                    </button>
                  </div>
                </div>

                {results.rows.length === 0 ? (
                  <p className="empty-results">
                    The query returned no rows. You can still export the
                    column headers.
                  </p>
                ) : (
                  <div className="table-container">
                    <table className="results-table">
                      <thead>
                        <tr>
                          {results.columns.map((column) => (
                            <th key={column}>{column}</th>
                          ))}
                        </tr>
                      </thead>

                      <tbody>
                        {results.rows.map((row, index) => (
                          <tr key={index}>
                            {results.columns.map((column) => (
                              <td key={column}>
                                {row[column] == null
                                  ? "NULL"
                                  : String(row[column])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            )}

            {!results && !error && (
              <section className="results-card">
                <div className="section-header">
                  <div>
                    <h3>Query Results</h3>
                    <p>Execute a query to display its results.</p>
                  </div>
                </div>

                <div className="empty-state">
                  <div className="empty-icon">▦</div>
                  <h3>No results yet</h3>
                  <p>Your database records will appear here.</p>
                </div>
              </section>
            )}
          </>
        ) : (
          <section className="results-card">
            <div className="section-header">
              <div>
                <h3>Recent Queries</h3>
                <p>Last 50 queries · Query values are redacted.</p>
              </div>

              <button
                className="run-button"
                onClick={openHistory}
                disabled={historyLoading}
              >
                {historyLoading ? "Refreshing..." : "↻ Refresh"}
              </button>
            </div>

            {historyError && (
              <div
                className="message-card error-message"
                role="alert"
              >
                {historyError}
              </div>
            )}

            {historyLoading ? (
              <div className="empty-state">
                <p>Loading query history...</p>
              </div>
            ) : history.length === 0 && !historyError ? (
              <div className="empty-state">
                <div className="empty-icon">▤</div>
                <h3>No query history yet</h3>
                <p>
                  Run a query in the editor to see it recorded here.
                </p>

                <button className="run-button" onClick={openEditor}>
                  Open Query Editor
                </button>
              </div>
            ) : (
              <div className="table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Query Preview</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Duration</th>
                      <th>Rows</th>
                    </tr>
                  </thead>

                  <tbody>
                    {history.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <code>{item.query_preview}</code>
                        </td>

                        <td>
                          {new Date(
                            item.executed_at
                          ).toLocaleString()}
                        </td>

                        <td>
                          {item.status === "success"
                            ? "✓ Success"
                            : item.status === "rejected"
                              ? "⊘ Rejected"
                              : "✕ Failed"}
                        </td>

                        <td>{item.duration_ms} ms</td>
                        <td>{item.row_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        <footer>
          DataOps Console · Personal hackathon prototype
        </footer>
      </main>
    </div>
  );
}
