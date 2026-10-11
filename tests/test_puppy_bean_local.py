"""Verify genuine BEAN Core copy and offline service, not a fake LLM."""
from __future__ import annotations
import os,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"puppy-native"
CORE=BASE/"bean-core"

def test_real_bean_core_executes_evidence_review_offline():
    env=os.environ.copy()
    env["PYTHONPATH"]=str(CORE)
    result=subprocess.run([sys.executable,str(BASE/"bean-mini-service.py"),"--self-test"],
                          cwd=str(ROOT),env=env,text=True,capture_output=True,timeout=30)
    assert result.returncode==0,(result.stdout,result.stderr)
    assert "BEAN_LOCAL_REAL_CORE_TEST_PASS" in result.stdout

def test_bean_logo_is_actual_upstream_webp():
    logo=(BASE/"art"/"bean-official.webp").read_bytes()
    assert len(logo)>5000
    assert logo[:4]==b"RIFF" and logo[8:12]==b"WEBP"

def test_embedded_core_has_no_hosted_model_or_download_requirements():
    script=(BASE/"bean-mini-service.py").read_text()
    assert '127.0.0.1' in script
    assert 'HTTPServer(("127.0.0.1",8788)' in script
    assert '"model":"not_loaded"' in script
    assert 'EpistemicGuard' in script
    runner=(BASE/"venvwin-bean").read_text()
    assert 'python3' in runner
    assert "ollama pull" not in runner
    assert "curl " not in runner
    session=(BASE/"venvwin-session").read_text()
    assert 'venvwin-bean --serve' in session
    assert "BEAN_UNAVAILABLE" in session

def test_pinboard_has_bean_and_desktop_icons():
    pin=ET.parse(BASE/"art"/"PuppyPin").getroot()
    assert pin.tag=="pinboard"
    targets=[item.text for item in pin.findall("icon")]
    assert "/root/Desktop/venvwin-bean.desktop" in targets
    assert "/root/Desktop/venvwin-app.desktop" in targets
