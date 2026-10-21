"""D1 v1.12 design-only responsive acceptance smoke.

Prerequisite: pip install playwright && python -m playwright install chromium.
Run from any working directory after checking out the design branch.
This checks only the standalone synthetic HTML prototype, NOT B3 runtime/API correctness.
"""
from pathlib import Path
import hashlib
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "prototypes" / "B3_V1_D1_FullDashboard_v1_12_WIP.html"
OUT = Path(__file__).with_name("B3_D1_v1_12_RESPONSIVE_SMOKE_REPORT.json")
assert HTML.is_file(), str(HTML)
data = HTML.read_bytes()
html = data.decode("utf-8")
checks = []
width_zoom = [
    (2560, 1), (1920, 1), (1500, 1), (1100, 1), (780, 1),
    (1500, 1.25), (1100, 1.25), (780, 1.25),
    (1500, 1.5), (1100, 1.5), (780, 1.5),
    (1500, 2), (1100, 2), (780, 2),
]

def record(case, ok, evidence):
    checks.append({"case": case, "result": "PASS" if ok else "FAIL", "evidence": evidence})
    print(checks[-1]["result"], case)

with sync_playwright() as pw:
    kwargs = {"headless": True}
    local = os.environ.get("D1_CHROMIUM_EXECUTABLE")
    if local:
        kwargs["executable_path"] = local
    browser = pw.chromium.launch(**kwargs)
    for width, zoom in width_zoom:
        page = browser.new_page(viewport={"width": width, "height": 950})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(html, wait_until="domcontentloaded")
        page.evaluate("(z) => { document.body.style.zoom = z; }", zoom)
        state = page.evaluate("""() => ({
          horizontal: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          overflow: [...document.querySelectorAll('.card .card-body')]
            .map((e,i)=>({i,extra:e.scrollHeight-e.clientHeight}))
            .filter(q=>q.extra>2),
          cards: document.querySelectorAll('.card').length
        })""")
        ok = (state["horizontal"] <= 2 and not state["overflow"] and
              state["cards"] == 8 and not errors)
        record(f"cards {width}px x {zoom:g} zoom", ok, {"dom": state, "errors": errors})
        page.close()
    for width in (1500, 1100, 780):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(html, wait_until="domcontentloaded")
        page.evaluate("document.body.style.zoom = 2")
        page.locator("#settingsEntry").click()
        box1 = page.locator(".dialog").bounding_box()
        page.locator("[data-setting=workbench]").click()
        box2 = page.locator(".d19-dialog").bounding_box()
        ok = all(
            0 <= box["x"] and 0 <= box["y"] and
            box["x"] + box["width"] <= width + 1 and
            box["y"] + box["height"] <= 901
            for box in (box1, box2)
        ) and not errors
        record(f"visible modal save/cancel {width}px at 200% simulated zoom",
               ok, {"settings": box1, "workbench": box2, "errors": errors})
        page.close()
    browser.close()

report = {
    "stage": "PRECODE_D1_v1.12_WIP",
    "source_sha256": hashlib.sha256(data).hexdigest(),
    "pass": sum(c["result"] == "PASS" for c in checks),
    "fail": sum(c["result"] == "FAIL" for c in checks),
    "cases": checks,
    "warning": ("Synthetic body zoom is a stress proxy. Native browser zoom, "
                "WCAG keyboard/contrast, 19 UI source bindings and B3 runtime remain unverified."),
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"RESULT {report['pass']}/{len(checks)}")
if report["fail"]:
    raise SystemExit(1)
