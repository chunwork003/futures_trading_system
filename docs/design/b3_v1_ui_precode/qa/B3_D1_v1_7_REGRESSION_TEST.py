"""D1 v1.7 design-only browser regression test (requires Chromium, Playwright)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
src=root/"prototypes"/"B3_V1_D1_FullDashboard_v1_7_REVIEW_CANDIDATE.html"
html=src.read_text(encoding="utf-8")
passed=0

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width,zoom in [(1510,1),(1100,1),(780,1),(1510,1.25),(1510,1.5)]:
        page=browser.new_page(viewport={"width":width,"height":970})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.set_content(html)
        page.evaluate("(z)=>document.documentElement.style.fontSize=(z*16)+'px'",zoom)
        metrics=page.evaluate("""() => ({
          cards:document.querySelectorAll('[data-card]').length,
          horizontal:document.documentElement.scrollWidth-document.documentElement.clientWidth,
          overflowing:[...document.querySelectorAll('[data-card]')].filter(c=>c.scrollHeight>c.clientHeight+2||c.scrollWidth>c.clientWidth+2).map(c=>c.dataset.card)
        })""")
        assert metrics["cards"]==8 and metrics["horizontal"]<=2 and not metrics["overflowing"] and not errors, (width,zoom,metrics,errors)
        passed+=1
        if width==1510 and zoom==1:
            page.click("#quickEdit")
            assert page.locator("#d17IconGroup").count()==1
            assert page.locator("#d17IconSymbol option:last-child").get_attribute("value")=="import"
            assert page.locator("#d1QuickCatalog [data-toggle]:visible").count()==0
            page.locator(".d17-catbtn").first.click()
            assert page.locator("#d1QuickCatalog [data-toggle]:visible").count()>0
            page.click("#dlgCancel")
            passed+=1
            page.click("#settingsEntry")
            assert page.locator("#themeWheel").is_visible()
            assert page.locator("#d17PalettePick option").count()>=3
            page.click("#dlgCancel")
            passed+=1
            page.click("#settingsEntry")
            page.click('[data-setting="start"]')
            page.select_option("#d17LaunchSelect","UI08")
            page.click("#d17AddLaunch")
            assert page.locator("#d17LaunchList .d17-chip").count()==2
            page.click("#dlgCancel")
            passed+=1
            page.select_option("#d17SelectPage","p2")
            assert "我的投資組合 2" in page.locator("h1").inner_text()
            page.select_option("#d17SelectPage","all")
            assert "全組合總覽" in page.locator("h1").inner_text()
            passed+=1
            page.click("#settingsEntry")
            page.click('[data-setting="workbench"]')
            assert page.locator("#d17WorkbenchPage").count()==1
            page.click("#d17ModuleTab")
            assert page.locator("#d17ManagerPane").is_visible()
            page.click("#d17LayoutTab")
            assert page.locator("#workbenchCanvas").is_visible()
            page.click("#dlgCancel")
            passed+=1
            page.select_option("#d17SelectPage","p1")
            assert page.locator('[data-card="trend"] rect[data-series-index]').count()==24
            assert page.locator('[data-card="allocation"] .d17-assetstat').count()==5
            passed+=1
        page.close()
    browser.close()

print("PASS",passed,"design-only checks; no official B3 runtime/E2E assertions")
