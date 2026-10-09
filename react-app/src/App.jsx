
import Navbar from "./components/Navbar";
import "./App.css";

const applications = [
  {
    name: "React Frontend",
    technology: "React + Vite + Nginx",
    description:
      "The main dashboard for accessing and managing your application workspace.",
    url: "http://localhost:3000",
    label: "Open Dashboard",
    color: "#61DAFB",
    icon: "⚛",
    port: "3000",
  },
  {
    name: "Python API",
    technology: "Python + FastAPI",
    description:
      "Explore the Python backend, interactive API documentation, and health endpoint.",
    url: "http://localhost:8000/docs",
    healthUrl: "http://localhost:8000/health",
    label: "Open API Docs",
    color: "#FFD43B",
    icon: "🐍",
    port: "8000",
  },
  {
    name: ".NET API",
    technology: "C# + ASP.NET Core 8",
    description:
      "Explore the .NET backend API and its health endpoint.",
    url: "http://localhost:5000",
    healthUrl: "http://localhost:5000/health",
    label: "Open .NET API",
    color: "#A78BFA",
    icon: "▣",
    port: "5000",
  },
];

function App() {
  return (
    <div className="app">
      <Navbar />

      <main className="dashboard">
        <section className="hero">
          <div className="hero-badge">
            <span className="status-dot" />
            Docker Workspace
          </div>

          <h1>
            DevOps <span>Control Center</span>
          </h1>

          <p className="hero-description">
            One workspace. Three applications. One unified experience.
            Navigate between your React frontend, Python API, and .NET API.
          </p>

          <div className="hero-stats">
            <div className="stat">
              <span className="stat-value">03</span>
              <span className="stat-label">Applications</span>
            </div>

            <div className="stat-divider" />

            <div className="stat">
              <span className="stat-value">Docker</span>
              <span className="stat-label">Containerized</span>
            </div>

            <div className="stat-divider" />

            <div className="stat">
              <span className="stat-value">Local</span>
              <span className="stat-label">Environment</span>
            </div>
          </div>
        </section>

        <section className="applications-section">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">YOUR WORKSPACE</p>
              <h2>Applications</h2>
            </div>

            <span className="application-count">03 SERVICES</span>
          </div>

          <div className="application-grid">
            {applications.map((app) => (
              <article className="application-card" key={app.name}>
                <div className="card-top">
                  <div
                    className="application-icon"
                    style={{
                      color: app.color,
                      backgroundColor: `${app.color}18`,
                    }}
                  >
                    {app.icon}
                  </div>

                  <span className="service-badge">
                    <span className="status-dot" />
                    Configured
                  </span>
                </div>

                <div className="card-content">
                  <p className="technology-label">{app.technology}</p>
                  <h3>{app.name}</h3>
                  <p className="card-description">{app.description}</p>
                </div>

                <div className="card-port">
                  <span>LOCAL PORT</span>
                  <code>:{app.port}</code>
                </div>

                <div className="card-actions">
                  <a
                    className="primary-link"
                    href={app.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {app.label}
                    <span aria-hidden="true">↗</span>
                  </a>

                  {app.healthUrl && (
                    <a
                      className="health-link"
                      href={app.healthUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Health
                    </a>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="architecture-section">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">INFRASTRUCTURE</p>
              <h2>Workspace Architecture</h2>
            </div>
          </div>

          <div className="architecture-card">
            <div className="architecture-node">
              <span className="architecture-icon">🌐</span>
              <div>
                <strong>React + Nginx</strong>
                <span>Frontend · Port 3000</span>
              </div>
            </div>

            <div className="architecture-connector">
              <span>Docker Compose Network</span>
              <div className="connector-line" />
            </div>

            <div className="architecture-backends">
              <div className="architecture-node">
                <span className="architecture-icon">🐍</span>
                <div>
                  <strong>FastAPI</strong>
                  <span>Backend · Port 8000</span>
                </div>
              </div>

              <div className="architecture-node">
                <span className="architecture-icon">▣</span>
                <div>
                  <strong>ASP.NET Core</strong>
                  <span>Backend · Port 5000</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="dashboard-footer">
          <span>DEVOPS HUB</span>
          <span>React · Python · .NET</span>
          <span>Built with Docker Compose</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
