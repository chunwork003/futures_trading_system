"""D1 design-only test: Chromium/Playwright, no B3 runtime API or broker.
Run from docs/design/b3_v1_ui_precode:
python qa/B3_D1_v1_6_REGRESSION_TEST.py prototypes/B3_V1_D1_FullDashboard_v1_6_RECOVERY_CANDIDATE.html
Requires pip install playwright and Chromium installed. Override CHROMIUM_PATH as needed.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os, sys

source=Path(sys.argv[1]); assert source.is_file(), source
html=source.read_text(encoding='utf-8')
cases=[]
def check(name, value):
    assert value, name
    cases.append(name)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1500,'height':940})
    page.set_default_timeout(3000)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    check('eight baseline cards',page.locator('article.card').count()==8)
    check('four portfolios',page.locator('#d1PortfolioSelector option').count()==4)
    page.locator('#d1PortfolioSelector').select_option('1')
    check('main switching',page.locator('[data-card="overview"] .big').inner_text()=='NT$ 2,590,000')
    page.locator('[data-card="overview"] [data-pin]').click()
    page.locator('#d1PortfolioSelector').select_option('2')
    check('independent pin',page.locator('[data-card="overview"] .big').inner_text()=='NT$ 2,590,000')
    check('six periods times four strategy bars',page.locator('#trendPlot rect[data-series-index]').count()==24)
    page.locator('[data-d1period="季"]').click()
    check('period selection',page.locator('[data-d1period="季"]').get_attribute('class')=='small current')
    before=page.locator('[data-card="assets"]').bounding_box()['height']
    page.locator('[data-tab="股票"]').click()
    check('stock tab and six reserved slots',page.locator('.asset:not(.placeholder)').count()==1 and page.locator('.asset.placeholder').count()==5)
    check('fixed category card height',page.locator('[data-card="assets"]').bounding_box()['height']==before)
    page.locator('[data-tab="總覽"]').click()
    page.locator('#d1AssetSort').select_option('return')
    check('asset sort selection',page.locator('#d1AssetSort').input_value()=='return')
    page.locator('[data-view="card"]').click()
    check('holdings card mode','simple-cards' in page.locator('.data-rows').get_attribute('class'))
    page.locator('#d1GlobalSearch').fill('audit')
    check('UI18 search',page.locator('#d1GlobalResults button').count()>=1)
    page.locator('#d1GlobalSearch').fill('')
    name=page.locator('[data-card="news"] strong').inner_text()
    page.locator('[data-pg="news:next"]').click()
    check('news carousel',page.locator('[data-card="news"] strong').inner_text()!=name)
    page.locator('#quickEdit').click()
    check('feature catalog by subfeatures',page.locator('#d1QuickCatalog [data-toggle]').count()>=27)
    page.locator('#d1QuickStyle').select_option('both')
    page.locator('#d1QuickSearch').fill('Audit')
    page.locator('[data-toggle="UI18:audit"]').click()
    check('shortcut selection','Audit' in page.locator('#d1SelectedQuick').inner_text())
    page.locator('#dlgSave').click()
    check('shortcut mode saved','d1-rail-wide' in page.locator('#rail').get_attribute('class'))
    page.locator('#settingsEntry').click()
    page.locator('[data-setting="workbench"]').click()
    check('layout JSON action',page.locator('#d1LayoutExport').is_visible())
    page.locator('#settingPage button').first.click()
    check('vacant workbench occupancy cells',page.locator('[data-empty]').count()>0)
    page.locator('[data-empty]').first.click()
    page.locator('#dlgCancel').click()
    check('cancel retains original eight cards',page.locator('article.card').count()==8)
    page.locator('#dlgCancel').click()
    page.locator('#settingsEntry').click()
    page.locator('[data-setting="module"]').click()
    page.locator('#settingPage button').first.click()
    page.locator('#modCols').select_option('6')
    page.locator('#modRows').select_option('2')
    for _ in range(7): page.locator('[data-mod-empty]').first.click()
    check('seven NxM slots',page.locator('[data-slot]').count()==7)
    page.locator('#dlgCancel').click()
    check('nested editor returns to settings',page.locator('[data-setting="module"]').is_visible())
    page.locator('#dlgCancel').click()
    page.locator('#stateSel').select_option('UNKNOWN')
    check('UNKNOWN masks total, trend and allocation',page.locator('[data-card="overview"] .big').inner_text()=='—' and page.locator('#trendPlot').count()==0 and 'UNKNOWN' in page.locator('[data-card="allocation"]').inner_text())
    assert not errors, errors
    browser.close()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    for width in (1500,1100,780):
        page=browser.new_page(viewport={'width':width,'height':940})
        page.set_content(html)
        for percent in (100,125,150):
            page.evaluate('(n)=>document.body.style.fontSize=(13*n/100)+"px"',percent)
            result=page.evaluate("""() => ({overflow:document.documentElement.scrollWidth-innerWidth,bad:[...document.querySelectorAll('.card')].filter(c=>c.querySelector('.card-body').scrollHeight-c.querySelector('.card-body').clientHeight>2).map(c=>c.dataset.card)})""")
            check('visual %spx %s%%'%(width,percent),result['overflow']<=0 and not result['bad'])
        page.close()
    browser.close()
print('PASS %d bounded design-only checks; not product conformance.'%len(cases))
