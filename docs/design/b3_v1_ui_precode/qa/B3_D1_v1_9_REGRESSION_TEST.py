"""D1 v1.9 bounded standalone HTML design regression. No B3 backend/API/SQL."""
import json
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
HTML = BASE.parent / "prototypes" / "B3_V1_D1_FullDashboard_v1_9_THREE_LAYER_CANDIDATE.html"
assert HTML.is_file(), f"Missing local prototype {HTML}"
results = []
def check(label, condition):
    results.append({"test": label, "status": "PASS" if condition else "FAIL"})
    print(results[-1])

with sync_playwright() as pw:
    binary = which("chromium") or which("google-chrome")
    opts = {"headless": True, "args": ["--no-sandbox"]}
    if binary:
        opts["executable_path"] = binary
    browser = pw.chromium.launch(**opts)
    page = browser.new_page(viewport={"width":1500,"height":950})
    page.set_default_timeout(8000)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.set_content(HTML.read_text(encoding="utf-8"), wait_until="domcontentloaded")
    check("首頁原始八模組保留",page.locator(".card").count()==8)
    page.locator("#settingsEntry").click()
    page.locator("[data-setting=workbench]").click()
    check("三層編輯器入口",page.locator("#d19Shade").is_visible() and page.locator("[data-d19-layer]").count()==4)
    check("原有草稿八模組",page.locator("[data-d19-card]").count()==8)
    page.locator("#d19Kind").select_option("chart")
    names=page.locator("#d19ModuleChoice option").all_text_contents()
    check("B 呈現類型過濾 C 候選",bool(names) and all("組合表現" in n or "資產分布" in n for n in names))
    page.locator("#d19Kind").select_option("")
    page.locator("#d19ModuleChoice").select_option("capital")
    page.locator("#d19Add").click()
    check("右側＋加入，而非點空白格",page.locator("[data-d19-card]").count()==9 and page.locator("[data-cell]").count()==0)
    page.locator("#d19Discard").click()
    check("取消草稿不改首頁",page.locator(".card").count()==8)
    page.locator("[data-setting=workbench]").click()
    page.locator("[data-d19-cat=market]").click()
    page.locator("[data-d19-page=UI02]").click()
    check("一般市場頁面類別鎖定",page.locator("#d19Add").is_disabled())
    page.locator("[data-d19-cat=custom]").click()
    page.locator("[data-d19-page=custom-1]").click()
    page.locator("#d19CategoryChoice").select_option("portfolio")
    check("僅自定義頁面可切換來源類別",page.locator("#d19CategoryChoice").is_visible() and page.locator("#d19ModuleChoice option").count()>=4)
    page.locator("#d19Discard").click()
    page.locator("[data-setting=workbench]").click()
    page.locator("[data-d19-layer=module]").click()
    check("第二層模組 A-G 分區",page.locator("#d19ModRight").get_by_text("A　大類").count()==1 and page.locator("#d19ModuleGrid").count()==1)
    page.locator("[data-d19-slotempty]").first.click()
    check("點新資訊格進第三層",page.locator("#d19InfoPreview").count()==1)
    page.locator("#d19InfoField").select_option("balance")
    page.locator("#d19InfoKind").select_option("line")
    page.locator("#d19InfoPeriod").select_option("month")
    query=json.loads(page.locator("#d19QuerySpec").inner_text())
    check("查詢採規格資料且不執行 SQL",query["field"]=="balance" and query["resolution"]=="month" and query["sql_execution"]=="NOT_AUTHORIZED")
    page.locator("#d19InfoApply").click()
    check("第三層返回模組並保留資訊",page.locator("#d19ModuleGrid").count()==1 and "目前資金" in page.locator("#d19ModuleGrid").inner_text())
    page.locator("#d19ModName").fill("資金雙格候選")
    page.locator("#d19SaveModule").click()
    check("第二層儲存返回工作區",page.locator("#d19Grid").count()==1 and page.locator("#d19ModuleChoice").count()==1)
    page.locator("[data-d19-layer=startup]").click()
    page.locator("[data-d19-startmode=custom]").click()
    n=page.locator("#d19StartupList > div").count()
    page.locator("#d19AddStartupPage").click()
    check("指定情境可新增啟動頁面",page.locator("#d19StartupList > div").count()==n+1)
    page.locator("#d19Discard").click()
    page.locator("[data-setting=workbench]").click()
    page.locator("[data-d19-layer=startup]").click()
    page.locator("[data-d19-startmode=custom]").click()
    check("取消後不保留未儲存啟動頁",page.locator("#d19StartupList > div").count()==n)
    page.locator("#d19Discard").click()
    check("JS 執行無錯誤",not errors)
    for width in (1500,1100):
        page.set_viewport_size({"width":width,"height":920})
        page.locator("[data-setting=workbench]").click()
        g=page.locator(".d19-dialog").evaluate("(e)=>({left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:window.innerWidth})")
        check(f"{width}px 編輯器整體未越界",g["left"]>=-1 and g["right"]<=g["width"]+1)
        page.locator("#d19Discard").click()
    browser.close()

report={"result":f"{sum(x['status']=='PASS' for x in results)}/{len(results)} PASS","scope":"Stand-alone HTML only. Not API, SQL, UI01-19 or 64-Finding acceptance.","checks":results}
(BASE/"B3_D1_v1_9_REGRESSION_LOCAL_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
if any(r["status"]!="PASS" for r in results):
    raise SystemExit("D1 v1.9 bounded regression has failures")
