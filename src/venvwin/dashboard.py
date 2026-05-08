from __future__ import annotations

import html
import json
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from .capsule import list_capsules
from .first_run import PUBLIC_PRODUCT_NAME, first_run_summary, write_first_run_files
from .health import health_report
from .paths import capsules_dir, default_root, ensure_runtime_dirs
from .persistence import persistence_report

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
TOKEN_FILE = ".winux-dashboard-token"


def dashboard_model(root: Path | None = None, home: Path | None = None) -> dict[str, Any]:
    runtime_root = (root or default_root()).expanduser().resolve()
    ensure_runtime_dirs(runtime_root)
    storage = persistence_report(home)
    first = first_run_summary(home)
    health = health_report(runtime_root)
    capsules = [capsule.to_dict() for capsule in list_capsules(capsules_dir(runtime_root))]
    return {
        "product_name": PUBLIC_PRODUCT_NAME,
        "runtime_root": str(runtime_root),
        "storage": storage,
        "first_run": first,
        "health": health,
        "capsules": capsules,
        "capsule_count": len(capsules),
    }


def get_or_create_token(home: Path | None = None) -> str:
    user_home = home or Path.home()
    token_path = user_home / TOKEN_FILE
    if token_path.exists():
        token = token_path.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(18)
    token_path.write_text(token, encoding="utf-8")
    try:
        token_path.chmod(0o600)
    except OSError:
        pass
    return token


def dashboard_url(host: str, port: int, token: str | None = None) -> str:
    shown_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    query = f"?{urlencode({'token': token})}" if token else ""
    return f"http://{shown_host}:{port}/{query}"


def status_badge(value: bool, good: str = "OK", warn: str = "WARNING") -> str:
    klass = "good" if value else "warn"
    text = good if value else warn
    return f'<span class="badge {klass}">{html.escape(text)}</span>'


def token_link(path: str, token: str | None) -> str:
    if not token:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}{urlencode({'token': token})}"


def render_locked_page() -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{PUBLIC_PRODUCT_NAME} Dashboard Locked</title>
<style>body{{margin:0;font-family:system-ui;background:#070b10;color:#eef6ff;display:grid;place-items:center;min-height:100vh}}.card{{background:#111827;border:1px solid #263449;border-radius:18px;padding:28px;max-width:560px}}.muted{{color:#a7b4c0}}.token{{background:#070b10;color:#38bdf8;border-radius:10px;padding:10px;overflow-wrap:anywhere}}</style></head>
<body><div class="card"><h1>{PUBLIC_PRODUCT_NAME} Dashboard Locked</h1><p class="muted">LAN dashboard access requires the session token from the venvWin Portable desktop. This keeps the control panel from being open to every device on the network.</p><p class="muted">Open the dashboard from the desktop launcher or use the printed LAN URL.</p></div></body></html>"""


def render_dashboard(model: dict[str, Any], token: str | None = None) -> str:
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

    status_href = html.escape(token_link("/api/status", token))
    doctor_href = html.escape(token_link("/api/doctor", token))
    init_href = html.escape(token_link("/api/initialize", token))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PUBLIC_PRODUCT_NAME} Dashboard</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background: #05080d; color: #eef6ff; min-height: 100vh; padding-bottom: 54px; }}
    header {{ padding: 24px 28px 18px; background: linear-gradient(135deg, #07111f, #101827 55%, #0b2638); border-bottom: 1px solid #203040; }}
    h1 {{ margin: 0; font-size: 32px; letter-spacing: -0.04em; }}
    .sub {{ color: #a7b4c0; margin-top: 8px; }}
    main {{ padding: 18px; display: grid; grid-template-columns: 230px 1.1fr 0.9fr; gap: 14px; }}
    .start-panel {{ background:#0d1522; border:1px solid #263449; border-radius:18px; padding:14px; min-height: 460px; box-shadow: 0 20px 45px rgba(0,0,0,.25); }}
    .start-title {{ font-weight:900; margin: 4px 0 12px; color:#eef6ff; }}
    .start-item {{ display:block; text-decoration:none; color:#eef6ff; background:#1b2638; padding:11px 12px; border-radius:12px; margin-bottom:9px; font-weight:750; }}
    .start-item span {{ display:block; color:#a7b4c0; font-weight:500; font-size:12px; margin-top:2px; }}
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
    .taskbar {{ position:fixed; left:0; right:0; bottom:0; height:54px; background:#0a1019; border-top:1px solid #263449; display:flex; align-items:center; gap:12px; padding:0 14px; box-shadow:0 -10px 30px rgba(0,0,0,.35); }}
    .start-button {{ background:#1f6feb; color:white; border-radius:12px; padding:10px 14px; font-weight:900; }}
    .task-pill {{ background:#1b2638; color:#a7b4c0; border-radius:999px; padding:8px 12px; font-size:13px; }}
    .task-spacer {{ flex:1; }}
    @media (max-width: 1000px) {{ main {{ grid-template-columns: 1fr; padding: 14px; }} .start-panel {{ min-height:auto; }} header {{ padding: 22px; }} h1 {{ font-size: 28px; }} .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{PUBLIC_PRODUCT_NAME}</h1>
    <div class="sub">Portable compatibility capsules with a familiar desktop-control flow.</div>
  </header>
  <main>
    <nav class="start-panel">
      <div class="start-title">Start</div>
      <a class="start-item" href="{status_href}">System Status<span>Storage, capsules, runtime JSON</span></a>
      <a class="start-item" href="{doctor_href}">Doctor<span>Health checks and repairs</span></a>
      <a class="start-item" href="{init_href}">Initialize Storage<span>Write first-boot proof files</span></a>
      <a class="start-item" href="#capsules">Capsules<span>Installed app environments</span></a>
    </nav>

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
        <a class="button" href="{status_href}">Status JSON</a>
        <a class="button" href="{doctor_href}">Doctor JSON</a>
        <a class="button" href="{init_href}">Initialize storage</a>
      </div>
    </section>

    <section class="card">
      <h2>Control Panel</h2>
      <p class="muted">Overall: <strong>{html.escape(health['overall'])}</strong></p>
      {checks}
    </section>

    <section id="capsules" class="card" style="grid-column: 2 / -1;">
      <h2>Capsules</h2>
      <table>
        <thead><tr><th>ID</th><th>App</th><th>Profile</th></tr></thead>
        <tbody>{capsule_rows}</tbody>
      </table>
    </section>
  </main>
  <div class="taskbar">
    <div class="start-button">venvWin</div>
    <div class="task-pill">Dashboard</div>
    <div class="task-pill">Capsules: {model['capsule_count']}</div>
    <div class="task-spacer"></div>
    <div class="task-pill">Leave no trace: {'ON' if leave_no_trace else 'CHECK'}</div>
  </div>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    runtime_root: Path = default_root()
    user_home: Path | None = None
    access_token: str | None = None

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_text(self, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def authorized(self) -> bool:
        if not self.access_token:
            return True
        parsed = urlparse(self.path)
        supplied = parse_qs(parsed.query).get("token", [""])[0]
        return secrets.compare_digest(supplied, self.access_token)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if not self.authorized():
            self.send_response(403)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            encoded = render_locked_page().encode("utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return

        model = dashboard_model(self.runtime_root, self.user_home)
        if path == "/":
            self.send_text(render_dashboard(model, self.access_token))
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


def run_dashboard(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    root: Path | None = None,
    home: Path | None = None,
    token: str | None = None,
) -> None:
    handler = type("ConfiguredDashboardHandler", (DashboardHandler,), {})
    handler.runtime_root = (root or default_root()).expanduser().resolve()
    handler.user_home = home
    handler.access_token = token
    server = ThreadingHTTPServer((host, port), handler)
    print(f"{PUBLIC_PRODUCT_NAME} dashboard: {dashboard_url(host, port, token)}")
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    root = None
    home = None
    token = None
    if "--host" in args:
        host = args[args.index("--host") + 1]
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    if "--root" in args:
        root = Path(args[args.index("--root") + 1]).expanduser().resolve()
    if "--home" in args:
        home = Path(args[args.index("--home") + 1]).expanduser().resolve()
    if "--token" in args:
        token = args[args.index("--token") + 1]
    if "--token-file" in args:
        token_home = Path(args[args.index("--token-file") + 1]).expanduser().resolve().parent
        token = get_or_create_token(token_home)
    if "--lan-token" in args:
        token = get_or_create_token(home)
    run_dashboard(host=host, port=port, root=root, home=home, token=token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
