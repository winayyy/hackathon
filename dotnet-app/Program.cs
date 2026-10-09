
using Microsoft.AspNetCore.Http;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

app.UseCors();

app.MapGet("/", () => Results.Content("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>.NET | DevOps Hub</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0b1120;
            color: #f9fafb;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            padding: 18px 28px;
            background: #111827;
            border-bottom: 1px solid #273449;
            flex-wrap: wrap;
        }
        .brand {
            color: #f9fafb;
            text-decoration: none;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        .brand span { color: #60a5fa; }
        .links { display: flex; gap: 8px; flex-wrap: wrap; }
        .links a {
            padding: 10px 14px;
            border-radius: 8px;
            color: #cbd5e1;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
        }
        .links a:hover, .links a.active {
            background: #1e3a5f;
            color: white;
        }
        main {
            max-width: 1000px;
            margin: 0 auto;
            padding: 60px 24px;
        }
        .badge {
            display: inline-block;
            padding: 8px 12px;
            border: 1px solid #374151;
            border-radius: 20px;
            color: #86efac;
            font-size: 13px;
        }
        h1 { font-size: clamp(34px, 6vw, 54px); margin: 24px 0 12px; }
        h1 span { color: #a78bfa; }
        .description {
            max-width: 650px;
            color: #9ca3af;
            line-height: 1.8;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-top: 36px;
        }
        .card {
            padding: 24px;
            background: #111827;
            border: 1px solid #273449;
            border-radius: 14px;
        }
        .card h2 { font-size: 18px; }
        .card p { color: #9ca3af; line-height: 1.6; }
        .button {
            display: inline-block;
            margin-top: 12px;
            padding: 11px 14px;
            border-radius: 8px;
            background: #1e3a5f;
            color: white;
            text-decoration: none;
            font-size: 14px;
        }
        .button:hover { background: #2563eb; }
        code { color: #86efac; }
        footer {
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid #273449;
            color: #6b7280;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <nav>
        <a class="brand" href="http://localhost:3000">
            <span>◆</span> DEVOPS HUB
        </a>
        <div class="links">
            <a href="http://localhost:3000">React</a>
            <a href="http://localhost:8000/">Python</a>
            <a class="active" href="http://localhost:5000/">.NET</a>
        </div>
    </nav>

    <main>
        <span class="badge">● .NET Service</span>
        <h1>.NET <span>API Center</span></h1>
        <p class="description">
            Welcome to the ASP.NET Core backend of DevOps Hub.
            Explore the service health endpoint and navigate
            between all applications from this unified workspace.
        </p>

        <section class="grid">
            <article class="card">
                <h2>Service Health</h2>
                <p>Check whether the .NET API is responding correctly.</p>
                <a class="button" href="/health">Check Health ↗</a>
            </article>

            <article class="card">
                <h2>Application Details</h2>
                <p>
                    Framework: ASP.NET Core<br>
                    Runtime: .NET 8<br>
                    Container port: <code>5000</code>
                </p>
                <a class="button" href="http://localhost:8000/">Visit Python ↗</a>
            </article>

            <article class="card">
                <h2>Main Dashboard</h2>
                <p>Return to the central dashboard to access all workspace applications.</p>
                <a class="button" href="http://localhost:3000/">Open Dashboard ↗</a>
            </article>
        </section>

        <footer>DEVOPS HUB · ASP.NET Core 8 · Docker Compose</footer>
    </main>
</body>
</html>
""", "text/html"));

app.MapGet("/health", () => Results.Ok(new
{
    status = "healthy",
    service = "dotnet-api"
}));

app.Run();
