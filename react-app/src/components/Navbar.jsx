
import "./Navbar.css";

const applications = [
  { name: "React", url: "http://localhost:3000", color: "#61DAFB" },
  { name: "Python", url: "http://localhost:8000", color: "#FFD43B" },
  { name: ".NET", url: "http://localhost:5000", color: "#A78BFA" },
];

export default function Navbar() {
  const currentUrl = window.location.origin;

  return (
    <nav className="app-navbar">
      <a className="navbar-brand" href="http://localhost:3000">
        <span className="brand-icon">◆</span>
        <span>DEVOPS HUB</span>
      </a>

      <div className="navbar-links">
        {applications.map((app) => (
          <a
            key={app.name}
            href={app.url}
            className={`navbar-link ${
              currentUrl === app.url ? "active" : ""
            }`}
          >
            <span
              className="nav-dot"
              style={{ backgroundColor: app.color }}
            />
            {app.name}
          </a>
        ))}
      </div>
    </nav>
  );
}
