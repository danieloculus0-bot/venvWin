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
TOKEN_FILE = ".venvwin-dashboard-token"


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


def token_link(path: str, token: str | None) -> str:
    if not token:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}{urlencode({'token': token})}"


def badge(value: bool, good: str, bad: str) -> str:
    klass = "good" if value else "bad"
    text = good if value else bad
    return f'<span class="badge {klass}">{html.escape(text)}</span>'


def render_locked_page() -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{PUBLIC_PRODUCT_NAME} Dashboard Locked</title><style>{BASE_CSS}</style></head><body><main class="locked window"><div class="titlebar">{PUBLIC_PRODUCT_NAME} Dashboard Locked</div><section class="pad"><h1>Access token required</h1><p class="muted">LAN dashboard access requires the session token from the venvWin Portable desktop.</p><p class="accent-text">Open the dashboard from the desktop launcher or use the printed LAN URL.</p></section></main></body></html>"""


BASE_CSS = """
:root{color-scheme:dark;--bg:#050505;--desktop:#090909;--window:#121212;--panel:#181818;--panel2:#202020;--title:#242424;--border:#4a4a4a;--dark:#000;--text:#f4f1ea;--muted:#aaa39a;--accent:#ff8a00;--accent2:#b65300;--good:#68b957;--bad:#e04436}*{box-sizing:border-box}body{margin:0;min-height:100vh;padding:24px 24px 64px;background:radial-gradient(circle at 18% 0%,#191919,#050505 52%);color:var(--text);font-family:'Segoe UI',Liberation Sans,DejaVu Sans,sans-serif;font-size:15px}a{color:inherit}.desktop{max-width:1380px;margin:0 auto;display:grid;grid-template-columns:390px 1fr;gap:20px}.splash,.window{background:linear-gradient(#1b1b1b,#101010);border:1px solid var(--border);box-shadow:0 0 0 1px #000,0 22px 50px rgba(0,0,0,.62)}.splash{min-height:610px;padding:40px 34px}.brand-row{display:flex;gap:22px;align-items:center;margin-bottom:28px}.logo{width:126px;height:120px;position:relative;flex:0 0 auto}.penguin{position:absolute;left:0;bottom:0;width:50px;height:88px;border:3px solid #d8d8d8;border-right:none;border-radius:40px 0 0 40px;background:#eee}.penguin:before{content:'';position:absolute;left:13px;top:-32px;width:52px;height:52px;border-radius:50%;background:#222;border:1px solid #555}.penguin:after{content:'';position:absolute;left:-10px;top:13px;border-top:11px solid transparent;border-bottom:11px solid transparent;border-right:30px solid var(--accent)}.pane{position:absolute;width:38px;height:38px;background:linear-gradient(#ff9d26,#d96f00);border:1px solid #7c3b00;left:64px;top:32px}.p2{left:106px;background:linear-gradient(#4a4a4a,#272727);border-color:#5b5b5b}.p3{top:74px;background:linear-gradient(#4a4a4a,#272727);border-color:#5b5b5b}.p4{left:106px;top:74px;background:linear-gradient(#4a4a4a,#272727);border-color:#5b5b5b}.brand h1{margin:0;font-size:42px;line-height:1;font-weight:700;letter-spacing:-.04em;text-shadow:0 1px 0 #000}.brand h1 span,.accent-text{color:var(--accent)}.brand h2{margin:8px 0 0;font-size:31px;font-weight:300;color:#d8d8d8}.tagline{color:var(--muted);font-size:17px;border-top:1px solid #333;padding-top:24px;margin:18px 0 34px}.feature{display:grid;grid-template-columns:50px 1fr;gap:14px;align-items:center;border:1px solid #333;background:#111;padding:14px;margin-bottom:16px}.feature strong{display:block;color:var(--accent);font-size:18px}.feature span span{color:var(--muted)}.icon{width:38px;height:38px;border:2px solid #bdbdbd;display:grid;place-items:center;color:#ddd;background:#1a1a1a;font-weight:800}.icon.accent{border-color:var(--accent);color:var(--accent)}.titlebar{height:38px;display:flex;align-items:center;gap:10px;padding:0 10px;background:linear-gradient(#303030,#171717);border-bottom:1px solid #050505;font-weight:700;text-shadow:0 1px 0 #000}.app-mini{width:18px;height:18px;display:grid;grid-template-columns:1fr 1fr;gap:2px}.app-mini i{background:#555;border:1px solid #222}.app-mini i:first-child{background:var(--accent)}.win-buttons{margin-left:auto;display:flex;gap:6px}.win-btn{width:27px;height:24px;display:grid;place-items:center;border:1px solid #575757;background:linear-gradient(#3c3c3c,#1a1a1a);color:#ddd;font-weight:900}.close{background:linear-gradient(#e67725,#8e2d10);color:#fff}.body{padding:14px;display:grid;grid-template-columns:230px 1fr 310px;gap:12px;background:#0d0d0d}.menu,.card{background:linear-gradient(#1b1b1b,#121212);border:1px solid var(--border);box-shadow:inset 0 0 0 1px #000}.menu{padding:10px}.menu a{display:flex;align-items:center;gap:12px;min-height:56px;margin-bottom:10px;padding:10px 12px;border:1px solid #3e3e3e;background:linear-gradient(#242424,#151515);text-decoration:none;font-weight:700}.menu a.primary,.button{background:linear-gradient(#ff9c24,#bf5c00);border:1px solid #ffb45b;color:#111;text-shadow:none}.card{padding:18px;min-height:220px}.card h2{margin:2px 0 16px;text-align:center;font-size:20px}.drive{width:118px;height:86px;margin:8px auto 20px;border:1px solid #777;background:linear-gradient(#777,#272727);box-shadow:0 12px 18px rgba(0,0,0,.45);position:relative}.drive:before{content:'';position:absolute;left:28px;top:24px;width:62px;height:36px;border:3px solid #222;background:#3a3a3a}.path{border:1px solid #555;background:#080808;color:var(--accent);padding:9px 10px;overflow-wrap:anywhere;font-family:Consolas,'Liberation Mono',monospace}.center-note{color:var(--muted);text-align:center;line-height:1.45;margin:16px 10px}.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;text-decoration:none;padding:10px 14px;min-height:38px;font-weight:800}.actions{text-align:center;margin-top:14px}.status-row{display:grid;grid-template-columns:48px 1fr 70px;gap:10px;align-items:center;border-top:1px solid #383838;padding:16px 0}.status-row:first-of-type{border-top:0}.status-title{font-weight:800;font-size:16px}.status-sub{color:var(--muted);font-size:13px;line-height:1.35;margin-top:3px}.badge{display:inline-grid;place-items:center;min-width:60px;min-height:34px;border:1px solid #1d5818;background:linear-gradient(#2d751f,#123c0f);color:#f4fff4;font-weight:900}.badge.bad{border-color:#811d14;background:linear-gradient(#d94a36,#70170f);color:#fff}.info{grid-column:2/4;border:1px solid var(--border);background:#1b1b1b;padding:13px 16px}.capsules{grid-column:1/4;min-height:150px}table{width:100%;border-collapse:collapse}th,td{padding:9px 10px;border-bottom:1px solid #333;text-align:left}th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.muted{color:var(--muted)}code{color:var(--accent);background:#0b0b0b;padding:1px 4px;border:1px solid #333}.check{display:grid;grid-template-columns:12px 1fr;gap:10px;padding:10px 0;border-top:1px solid #383838}.check:first-of-type{border-top:0}.check-dot{width:10px;height:10px;margin-top:5px;background:var(--good);border:1px solid #a6e39c}.check.warn .check-dot,.check.error .check-dot{background:var(--bad);border-color:#ff9a91}.check span{display:block;color:var(--muted);margin-top:2px}.taskbar{position:fixed;left:0;right:0;bottom:0;height:52px;background:linear-gradient(#242424,#0b0b0b);border-top:1px solid #555;display:flex;align-items:center;gap:10px;padding:0 10px;box-shadow:0 -10px 32px rgba(0,0,0,.55)}.start-button{height:40px;min-width:150px;display:flex;align-items:center;gap:10px;padding:0 16px;background:linear-gradient(#ff9d26,#b65300);color:#111;border:1px solid #ffb45b;font-weight:900;font-size:18px}.task-button{height:36px;min-width:190px;display:flex;align-items:center;padding:0 14px;border:1px solid #444;background:linear-gradient(#242424,#141414);color:#ddd}.tray{margin-left:auto;display:flex;gap:14px;align-items:center;color:#ddd}.pad{padding:28px}.locked{max-width:620px;margin:14vh auto 0}@media(max-width:1120px){.desktop{grid-template-columns:1fr}.body{grid-template-columns:1fr}.info,.capsules{grid-column:auto}.splash{min-height:auto}}
"""


def render_dashboard(model: dict[str, Any], token: str | None = None) -> str:
    chosen = model["storage"]["chosen"]
    leave_no_trace = bool(model["storage"].get("leave_no_trace"))
    host_risk = bool(model["storage"].get("host_write_warning"))
    health = model["health"]
    capsules = model["capsules"]

    capsule_rows = "".join(
        f"<tr><td>{html.escape(c['capsule_id'])}</td><td>{html.escape(c['app_name'])}</td><td>{html.escape(c['profile']['name'])}</td></tr>"
        for c in capsules
    ) or '<tr><td colspan="3" class="muted">No capsules yet. Use <strong>Run Windows App</strong> from the first-boot Control Center, or run <code>venvwin open app.exe</code>.</td></tr>'

    checks = "".join(
        f"<div class='check {html.escape(check['status'])}'><div class='check-dot'></div><div><strong>{html.escape(check['name'])}</strong><span>{html.escape(check['message'])}</span></div></div>"
        for check in health["checks"]
    )

    status_href = html.escape(token_link("/api/status", token))
    doctor_href = html.escape(token_link("/api/doctor", token))
    init_href = html.escape(token_link("/api/initialize", token))

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{PUBLIC_PRODUCT_NAME} Dashboard</title><style>{BASE_CSS}</style></head><body>
<main class="desktop">
<section class="splash"><div class="brand-row"><div class="logo" aria-hidden="true"><div class="penguin"></div><div class="pane"></div><div class="pane p2"></div><div class="pane p3"></div><div class="pane p4"></div></div><div class="brand"><h1>venv<span>Win</span></h1><h2>Portable</h2></div></div><div class="tagline">Windows app environments for Linux</div><div class="feature"><span class="icon accent">▦</span><span><strong>Per-app</strong><span>Launch Windows apps individually.</span></span></div><div class="feature"><span class="icon">▣</span><span><strong>Isolated</strong><span>Each app runs in its own capsule.</span></span></div><div class="feature"><span class="icon">◌</span><span><strong>Lightweight</strong><span>Simple Python, Wine, and desktop shortcuts. No heavy shell.</span></span></div></section>
<section class="window"><div class="titlebar"><span class="app-mini"><i></i><i></i><i></i><i></i></span>{PUBLIC_PRODUCT_NAME} Control Center<span class="win-buttons"><span class="win-btn">_</span><span class="win-btn">□</span><span class="win-btn close">×</span></span></div><div class="body">
<nav class="menu"><a class="primary" href="#"><span class="icon">▶</span>Run Windows App</a><a href="{init_href}"><span class="icon">▤</span>Initialize Storage</a><a href="{status_href}"><span class="icon">◷</span>Open Dashboard</a><a href="#capsules"><span class="icon">▧</span>Open Capsules</a><a href="{doctor_href}"><span class="icon">+</span>Run Doctor</a></nav>
<section class="card"><h2>Capsule Storage</h2><div class="drive" aria-hidden="true"></div><div class="path">{html.escape(chosen['path'])}</div><p class="center-note">All Windows app environments are stored in isolated capsules in the location above.</p><div class="actions"><a class="button" href="{init_href}">▣ Initialize / Repair</a></div></section>
<section class="card"><h2>System Status</h2><div class="status-row"><span class="icon">✓</span><div><div class="status-title">Leave no trace</div><div class="status-sub">No changes to host system.</div></div>{badge(leave_no_trace, 'ON', 'CHECK')}</div><div class="status-row"><span class="icon">▤</span><div><div class="status-title">Portable storage</div><div class="status-sub">All data stays on portable storage.</div></div>{badge(not host_risk, 'YES', 'NO')}</div><div class="status-row"><span class="icon">✓</span><div><div class="status-title">Host write risk</div><div class="status-sub">Windows apps cannot write to host system.</div></div>{badge(not host_risk, 'NO', 'YES')}</div></section>
<section class="info">ⓘ Windows apps run inside isolated capsules. Your system stays clean and untouched.</section>
<section id="capsules" class="card capsules"><h2>Capsules</h2><table><thead><tr><th>ID</th><th>App</th><th>Profile</th></tr></thead><tbody>{capsule_rows}</tbody></table></section>
<section class="card"><h2>Doctor</h2>{checks}</section>
</div></section></main>
<footer class="taskbar"><div class="start-button">☰ venvWin</div><div class="task-button">{PUBLIC_PRODUCT_NAME} Control Center</div><div class="task-button">Capsules: {model['capsule_count']}</div><div class="tray"><span>▣</span><span>◷</span><span>✓</span><span>Leave no trace: {'ON' if leave_no_trace else 'CHECK'}</span></div></footer></body></html>"""


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


def run_dashboard(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None, home: Path | None = None, token: str | None = None) -> None:
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
