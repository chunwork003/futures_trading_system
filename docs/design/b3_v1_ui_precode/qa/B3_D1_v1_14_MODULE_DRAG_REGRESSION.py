"""D1 v1.14 design-only NxM information-slot drag regression.

Usage (after installing Playwright Chromium):
    python docs/design/b3_v1_ui_precode/qa/B3_D1_v1_14_MODULE_DRAG_REGRESSION.py
Override browser executable on an offline workstation with B3_CHROMIUM_EXECUTABLE.
This tests a standalone synthetic design prototype, NOT B3 product/runtime authority.
"""
from pathlib import Path
from hashlib import sha256
import json
import os
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[1] / "prototypes" / "B3_V1_D1_FullDashboard_v1_14_WIP.html"
OUT = Path(__file__).with_name("B3_D1_v1_14_MODULE_DRAG_REPORT.json")
src = HTML.read_text(encoding="utf-8")
checks = []

def check(label, ok, detail=None):
    checks.append({"name": label, "result": "PASS" if ok else "FAIL", "detail": detail})
    print(checks[-1]["result"], label)

with sync_playwright() as pw:
    br = pw.chromium.launch(
        headless=True,
        executable_path=os.environ.get("B3_CHROMIUM_EXECUTABLE") or None,
        args=["--no-sandbox"],
    )
    page = br.new_page(viewport={"width": 1600, "height": 1000})
    page.set_default_timeout(7000)
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    marker = "\n})();\n</script></body></html>"
    assert marker in src, "Source injection marker changed: investigate, do not skip tests."
    instrumented = src.replace(
        marker,
        "\nwindow.__d114={s:d19,paint:d19RenderModule,fit:d114SlotFits,target:d114SlotTarget};" + marker,
    )
    page.set_content(instrumented, wait_until="domcontentloaded")
    page.locator("#settingsEntry").click()
    page.locator("[data-setting=module]").click()
    page.evaluate("""() => {
      const s=window.__d114.s;
      s.mod={id:'drag-test',name:'測試',category:'portfolio',subject:'capital',
        cols:4,rows:2,slots:[
          {x:0,y:0,w:2,h:1,field:'balance',kind:'line',present:'chart',unit:'TWD',period:'month'},
          {x:3,y:0,w:1,h:1,field:'balance',kind:'kpi',present:'kpi',unit:'TWD'}
        ]};
      s.modOriginal=null;s.selectedSlot=0;window.__d114.paint();
    }""")
    check("two information slots available", page.locator("[data-d19-slot]").count() == 2)
    check("full rectangle cannot overlap", not page.evaluate(
        "()=>window.__d114.fit(window.__d114.s.mod,0,2,0)"))
    check("full rectangle can move to second row", page.evaluate(
        "()=>window.__d114.fit(window.__d114.s.mod,0,1,1)"))
    target = page.evaluate("()=>window.__d114.target(window.__d114.s.mod,0,2,0)")
    check("nearest valid rectangle search", target is not None and target != {"x":2,"y":0}, target)
    grid = page.locator("#d19ModuleGrid").bounding_box()
    card = page.locator('[data-d19-slot="0"]').bounding_box()
    check("editor grid has a readable footprint", grid["width"] > 350 and grid["height"] >= 150)
    page.mouse.move(card["x"]+card["width"]/2, card["y"]+card["height"]/2)
    page.mouse.down()
    page.mouse.move(grid["x"]+grid["width"]*.46,grid["y"]+grid["height"]*.76,steps=12)
    check("semi-transparent ghost during drag",
          page.locator("#d114SlotGhost").evaluate("(el)=>getComputedStyle(el).display") == "block")
    page.mouse.up()
    current = page.evaluate("()=>({x:window.__d114.s.mod.slots[0].x,y:window.__d114.s.mod.slots[0].y})")
    check("pointer drop moves legal full footprint",current["y"]==1 and page.evaluate(
        "()=>window.__d114.fit(window.__d114.s.mod,0,window.__d114.s.mod.slots[0].x,window.__d114.s.mod.slots[0].y)"),current)
    card = page.locator('[data-d19-slot="0"]').bounding_box()
    page.mouse.move(card["x"]+card["width"]/2,card["y"]+card["height"]/2)
    page.mouse.down()
    page.mouse.move(grid["x"]-200,grid["y"]-200,steps=8)
    page.mouse.up()
    after = page.evaluate("()=>({x:window.__d114.s.mod.slots[0].x,y:window.__d114.s.mod.slots[0].y})")
    check("out-of-canvas drop preserves prior coords",after==current,after)
    page.locator('[data-d19-slot="0"]').focus()
    page.keyboard.press("Shift+ArrowLeft")
    pos = page.evaluate("()=>({x:window.__d114.s.mod.slots[0].x,y:window.__d114.s.mod.slots[0].y})")
    check("keyboard left moves legal slot",pos=={"x":0,"y":1},pos)
    page.keyboard.press("Shift+ArrowUp")
    pos = page.evaluate("()=>({x:window.__d114.s.mod.slots[0].x,y:window.__d114.s.mod.slots[0].y})")
    check("keyboard up preserves focus",pos=={"x":0,"y":0} and
          page.locator('[data-d19-slot="0"]').evaluate("(el)=>document.activeElement===el"),pos)
    page.keyboard.press("Shift+ArrowRight")
    page.keyboard.press("Shift+ArrowRight")
    pos = page.evaluate("()=>({x:window.__d114.s.mod.slots[0].x,y:window.__d114.s.mod.slots[0].y})")
    check("keyboard refuses collision",pos=={"x":1,"y":0},pos)
    check("original slot count preserved",page.locator("[data-d19-slot]").count()==2)
    check("no JS errors",not errors,errors)
    br.close()

result = {
    "stage":"PRECODE_D1_v1.14_WIP",
    "prototype_sha256":sha256(HTML.read_bytes()).hexdigest(),
    "passed":sum(x["result"]=="PASS" for x in checks),
    "failed":sum(x["result"]=="FAIL" for x in checks),
    "checks":checks,
    "scope_warning":"Synthetic HTML only; not source/contract, production, permission or Human acceptance."
}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("RESULT",result["passed"],"/",len(checks))
if result["failed"]:raise SystemExit(1)
