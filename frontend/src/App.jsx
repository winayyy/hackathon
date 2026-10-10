
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

export default function App() {
  const [query, setQuery] = useState(
    "SELECT id, name, city, status\nFROM customers\nLIMIT 10;"
  );
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function runQuery() {
    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        <button className="nav-item active">⌘ Query Editor</button>
        <button className="nav-item" disabled>▤ Query History</button>

        <div className="sidebar-bottom">
          <span className="status-dot connected-dot" />
          Local Environment
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Query Workspace</h1>
            <p>Connect, query, and explore your database.</p>
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
            <span>Maximum 100 rows · Read-only database user</span>
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
          <section className="message-card error-message" role="alert">
            <strong>Query failed</strong>
            <p>{error}</p>
          </section>
        )}

        {results && (
          <section className="results-card">
            <div className="section-header">
              <div>
                <h3>Query Results</h3>
                <p>{results.row_count} row(s) returned</p>
              </div>
              <span className="language-badge">SUCCESS</span>
            </div>

            {results.rows.length === 0 ? (
              <p className="empty-results">The query returned no rows.</p>
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

        <footer>DataOps Console · Personal hackathon prototype</footer>
      </main>
    </div>
  );
}
