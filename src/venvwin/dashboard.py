from __future__ import annotations

import html
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .capsule import list_capsules
from .first_run import first_run_summary, write_first_run_files
from .health import health_report
from .paths import capsules_dir, default_root, ensure_runtime_dirs
from .persistence import persistence_report

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


def dashboard_model(root: Path | None = None, home: Path | None = None) -> dict[str, Any]:
    runtime_root = (root or default_root()).expanduser().resolve()
    ensure_runtime_dirs(runtime_root)
    storage = persistence_report(home)
    first = first_run_summary(home)
    health = health_report(runtime_root)
    capsules = [capsule.to_dict() for capsule in list_capsules(capsules_dir(runtime_root))]
    return {
        "runtime_root": str(runtime_root),
        "storage": storage,
        "first_run": first,
        "health": health,
        "capsules": capsules,
        "capsule_count": len(capsules),
    }


def status_badge(value: bool, good: str = "OK", warn: str = "WARNING") -> str:
    klass = "good" if value else "warn"
    text = good if value else warn
    return f'<span class="badge {klass}">{html.escape(text)}</span>'


def render_dashboard(model: dict[str, Any]) -> str:
    chosen = model["storage"]["chosen"]
    leave_no_trace = bool(model["storage"].get("leave_no_trace"))
    host_risk = bool(model["storage"].get("host_write_warning"))
    health = model["health"]
    capsules = model["capsules"]

    capsule_rows = "".join(
        f"<tr><td>{html.escape(c['capsule_id'])}</td><td>{html.escape(c['app_name'])}</td><td>{html.escape(c['profile']['name'])}</td></tr>"
        for c in capsules
    ) or '<tr><td colspan="3" class="muted">No capsules yet. Double-click an EXE/MSI or create one with venvWin.</td></tr>'

    checks = "".join(
        f"<div class='check {html.escape(check['status'])}'><strong>{html.escape(check['name'])}</strong><span>{html.escape(check['message'])}</span></div>"
        for check in health["checks"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WinUx Dashboard</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background: #070b10; color: #eef6ff; }}
    header {{ padding: 28px; background: linear-gradient(135deg, #0b1220, #111827 55%, #0f2535); border-bottom: 1px solid #203040; }}
    h1 {{ margin: 0; font-size: 34px; letter-spacing: -0.04em; }}
    .sub {{ color: #a7b4c0; margin-top: 8px; }}
    main {{ padding: 22px; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; }}
    .card {{ background: #111827; border: 1px solid #263449; border-radius: 18px; padding: 20px; box-shadow: 0 20px 45px rgba(0,0,0,.28); }}
    .card h2 {{ margin: 0 0 14px; font-size: 18px; }}
    .path {{ background: #070b10; color: #38bdf8; border-radius: 12px; padding: 12px; overflow-wrap: anywhere; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .stat {{ background: #1f2937; border-radius: 14px; padding: 14px; }}
    .stat .label {{ color: #a7b4c0; font-size: 13px; }}
    .stat .value {{ font-size: 22px; font-weight: 800; margin-top: 4px; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 7px 11px; font-weight: 800; font-size: 12px; }}
    .good {{ background: rgba(34,197,94,.14); color: #22c55e; }}
    .warn {{ background: rgba(245,158,11,.16); color: #f59e0b; }}
    .bad {{ background: rgba(239,68,68,.16); color: #ef4444; }}
    .muted {{ color: #a7b4c0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #263449; font-size: 14px; }}
    th {{ color: #a7b4c0; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .check {{ padding: 12px; border-radius: 12px; background: #1f2937; margin-bottom: 10px; }}
    .check strong {{ display: block; margin-bottom: 4px; }}
    .check span {{ color: #a7b4c0; }}
    .check.ok {{ border-left: 4px solid #22c55e; }}
    .check.warn {{ border-left: 4px solid #f59e0b; }}
    .check.error {{ border-left: 4px solid #ef4444; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    a.button {{ text-decoration: none; color: #eef6ff; background: #263449; padding: 10px 14px; border-radius: 12px; font-weight: 800; }}
    @media (max-width: 850px) {{ main {{ grid-template-columns: 1fr; padding: 14px; }} header {{ padding: 22px; }} h1 {{ font-size: 28px; }} .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>WinUx Dashboard</h1>
    <div class="sub">Portable Windows-app capsules, storage visibility, and leave-no-trace control.</div>
  </header>
  <main>
    <section class="card">
      <h2>Storage destination</h2>
      <p class="muted">{html.escape(model['first_run']['storage_message'])}</p>
      <div class="path">{html.escape(chosen['path'])}</div>
      <div class="grid" style="margin-top:14px">
        <div class="stat"><div class="label">Leave no trace</div><div class="value">{status_badge(leave_no_trace, 'ON', 'CHECK')}</div></div>
        <div class="stat"><div class="label">Host write risk</div><div class="value">{status_badge(not host_risk, 'NO', 'YES')}</div></div>
        <div class="stat"><div class="label">Capsules</div><div class="value">{model['capsule_count']}</div></div>
      </div>
      <div class="actions">
        <a class="button" href="/api/status">Status JSON</a>
        <a class="button" href="/api/doctor">Doctor JSON</a>
        <a class="button" href="/api/initialize">Initialize storage</a>
      </div>
    </section>

    <section class="card">
      <h2>Health</h2>
      <p class="muted">Overall: <strong>{html.escape(health['overall'])}</strong></p>
      {checks}
    </section>

    <section class="card" style="grid-column: 1 / -1;">
      <h2>Capsules</h2>
      <table>
        <thead><tr><th>ID</th><th>App</th><th>Profile</th></tr></thead>
        <tbody>{capsule_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    runtime_root: Path = default_root()
    user_home: Path | None = None

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_text(self, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        model = dashboard_model(self.runtime_root, self.user_home)
        if path == "/":
            self.send_text(render_dashboard(model))
            return
        if path == "/api/status":
            self.send_text(json.dumps(model, indent=2), "application/json; charset=utf-8")
            return
        if path == "/api/doctor":
            self.send_text(json.dumps(model["health"], indent=2), "application/json; charset=utf-8")
            return
        if path == "/api/initialize":
            summary = write_first_run_files(self.user_home)
            self.send_text(json.dumps({"initialized": True, "summary": summary}, indent=2), "application/json; charset=utf-8")
            return
        self.send_response(404)
        self.end_headers()


def run_dashboard(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None, home: Path | None = None) -> None:
    handler = type("ConfiguredDashboardHandler", (DashboardHandler,), {})
    handler.runtime_root = (root or default_root()).expanduser().resolve()
    handler.user_home = home
    server = ThreadingHTTPServer((host, port), handler)
    print(f"WinUx dashboard: http://{host}:{port}")
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    root = None
    home = None
    if "--host" in args:
        host = args[args.index("--host") + 1]
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    if "--root" in args:
        root = Path(args[args.index("--root") + 1]).expanduser().resolve()
    if "--home" in args:
        home = Path(args[args.index("--home") + 1]).expanduser().resolve()
    run_dashboard(host=host, port=port, root=root, home=home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
