#!/usr/bin/env python3
"""BEAN local companion: actual BEAN Core continuity and evidence guard, no LLM."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse,json,os,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone

def start(db):
    from bean.runtime.bootstrap import start_bean
    from bean.cognition.epistemic_guard import EpistemicGuard
    ctx=start_bean(db_path=str(db),silent=True)
    guard=EpistemicGuard()
    return ctx,guard

def review(ctx,guard,payload):
    from bean.cognition.epistemic_guard import CandidateClaim
    from bean.memory.event_logger import log_event,EventType,Source
    claim=payload.get("claim","")
    if not isinstance(claim,str) or not 1<=len(claim.strip())<=2000:
        raise ValueError("Claim must be 1-2000 characters")
    source=payload.get("source","")
    if not isinstance(source,str) or len(source)>200:
        raise ValueError("Source label must be under 200 characters")
    event_id=log_event(ctx["session_uuid"],EventType.OBSERVATION,
                       "Operator submitted local claim for evidence review",
                       source=Source.HUMAN,subtype="venvwin-bean",
                       data={"statement":claim,"source_label":source})
    c=CandidateClaim(key="venvwin-local-claim",content=claim,
                     source_type="user_declared",source_ref=source or None,
                     confidence=None,evidence=[],falsification_path=None)
    result=guard.audit(c,persist=True)
    return {"event_id":event_id,"audit_id":result.audit_id,
            "verdict":result.verdict.value,"reasons":result.reasons,
            "source_verified":False,"llm_loaded":False,"action_executed":False}

HTML="""<!doctype html><html><head><meta charset="utf-8"><title>BEAN Local | venvWin Portable</title>
<style>body{background:#101216;color:#f4f1ea;font:16px system-ui;max-width:720px;
margin:7vh auto;padding:20px}header{display:flex;align-items:center;gap:18px}img{width:88px}
section{margin-top:25px;padding:25px;background:#1c2026;border:1px solid #393d44;border-radius:14px}
h1{font-size:36px;margin:0}em{color:#ff8a00;font-style:normal}p,small{color:#b5bac4}
textarea,input{box-sizing:border-box;width:100%;color:#fff;background:#101216;
padding:14px;border:1px solid #50545a;border-radius:9px;font:inherit;margin:12px 0}
button{background:#ff8a00;padding:12px 22px;border:0;border-radius:8px;font-weight:bold}
pre{white-space:pre-wrap;word-break:break-word;color:#ffcb91}</style></head><body>
<header><img alt="Official BEAN logo" src="/bean.webp">
<div><h1>BEAN <em>Local</em></h1><small>venvWin Portable · Offline evidence companion</small></div></header>
<section><h2>BEAN Core online</h2><p>Real BEAN continuity, SQLite memory and evidence review.
No language model loaded. No cloud connection, autonomous trading or hardware control.</p>
<small id="status">Reading local Core status...</small></section>
<section><h2>Evaluate a claim</h2><p>BEAN can flag missing evidence and uncertainties.
A source you type is not an independently verified source.</p>
<textarea id="claim" maxlength="2000" rows="4" placeholder="Enter an observation or claim"></textarea>
<input id="source" maxlength="200" placeholder="Source label (optional, not attested)">
<button onclick="review()">Review locally</button><pre id="result"></pre></section>
<script>
fetch('/status').then(r=>r.json()).then(x=>{document.getElementById('status').textContent=
'Session '+x.session.slice(0,8)+' | Mode: '+x.mode+' | Model: '+x.model;});
async function review(){const result=document.getElementById('result');result.textContent='Reviewing...';
const r=await fetch('/review',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({claim:document.getElementById('claim').value,
source:document.getElementById('source').value})});
result.textContent=JSON.stringify(await r.json(),null,2);}
</script></body></html>"""

def serve(ctx,guard,logo):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_): pass
        def respond(self,code,body,content_type="application/json"):
            self.send_response(code)
            self.send_header("Content-Type",content_type)
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def trusted(self):
            return self.headers.get("Host","").lower() in ("127.0.0.1:8788","localhost:8788")
        def do_GET(self):
            if not self.trusted(): return self.respond(403,b'{"error":"host"}')
            if self.path=="/": return self.respond(200,HTML.encode(),"text/html; charset=utf-8")
            if self.path=="/bean.webp" and logo.is_file():
                return self.respond(200,logo.read_bytes(),"image/webp")
            if self.path=="/status":
                return self.respond(200,json.dumps({"mode":"offline_evidence_core",
                    "session":ctx["session_uuid"],"model":"not_loaded",
                    "capabilities":["memory","epistemic_review"],"persistence_verified":False,
                    "network_requests":False,"autonomous_actions":False}).encode())
            return self.respond(404,b'{"error":"not_found"}')
        def do_POST(self):
            if self.path!="/review" or not self.trusted():
                return self.respond(403,b'{"error":"forbidden"}')
            origin=self.headers.get("Origin","")
            if origin and origin not in ("http://127.0.0.1:8788","http://localhost:8788"):
                return self.respond(403,b'{"error":"origin"}')
            if self.headers.get("Content-Type","").split(";")[0]!="application/json":
                return self.respond(415,b'{"error":"content_type"}')
            try: n=int(self.headers.get("Content-Length","0"))
            except ValueError: n=0
            if not 2<=n<=4096: return self.respond(413,b'{"error":"request_size"}')
            try:
                data=json.loads(self.rfile.read(n))
                if not isinstance(data,dict): raise ValueError("Object expected")
                output=review(ctx,guard,data)
            except (ValueError,TypeError) as exc:
                return self.respond(400,json.dumps({"error":str(exc)}).encode())
            except Exception:
                return self.respond(500,b'{"error":"core_failed"}')
            return self.respond(200,json.dumps(output).encode())
    server=HTTPServer(("127.0.0.1",8788),Handler)
    print("BEAN_LOCAL_EVIDENCE_CORE_READY_NO_LLM",flush=True)
    from bean.runtime.bootstrap import shutdown_bean
    try: server.serve_forever(0.5)
    finally:
        shutdown_bean(ctx)
        server.server_close()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--serve",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--db-path")
    args=ap.parse_args()
    if args.self_test:
        from bean.runtime.bootstrap import shutdown_bean
        with tempfile.TemporaryDirectory() as tmp:
            ctx,guard=start(Path(tmp)/"bean.db")
            item=review(ctx,guard,{"claim":"Unverified local observation"})
            assert item["audit_id"] and not item["source_verified"]
            shutdown_bean(ctx)
            print("BEAN_LOCAL_REAL_CORE_TEST_PASS")
        return
    if not args.serve: ap.error("Specify --serve or --self-test")
    if not args.db_path: ap.error("Explicit --db-path required")
    ctx,guard=start(Path(args.db_path))
    serve(ctx,guard,Path("/usr/share/venvwin/assets/bean-official.webp"))

if __name__=="__main__": main()
