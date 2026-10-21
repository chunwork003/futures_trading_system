"""D1 v1.8 standalone design-only browser regression. No B3 product/runtime I/O."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, time

ARTIFACT = Path('/mnt/data/B3_V1_D1_FullDashboard_v1_8_DESIGN_CANDIDATE.html')
S = ARTIFACT.read_text()
REPORT = {'version':'D1 v1.8', 'type':'STANDALONE_DESIGN_ONLY', 'tests':[], 'runtime_b3_evidence':False}

def check(name, func):
    t=time.monotonic(); errs=[]
    page=browser.new_page(viewport={'width':1500,'height':960},accept_downloads=True)
    page.on('pageerror',lambda e:errs.append(str(e)))
    try:
        page.set_content(S,wait_until='domcontentloaded',timeout=18000)
        func(page)
        if errs: raise AssertionError('JS exceptions: '+str(errs))
        REPORT['tests'].append({'id':name,'result':'PASS','ms':round((time.monotonic()-t)*1000)})
        print('PASS',name)
    except Exception as e:
        REPORT['tests'].append({'id':name,'result':'FAIL','error':str(e)[:320]})
        print('FAIL',name,repr(e)[:220])
    finally: page.close()

def t01(page):
    assert page.locator('#dashboard .card').count()==8
    for a in ['portfolio','market','lab','schedule']:
        page.locator('[data-rail="%s"]'%a).hover();assert page.locator('#flyout').is_visible()
        assert page.locator('#flyhead').is_hidden()
    css=page.locator('#flyout').evaluate('(e)=>getComputedStyle(e).backgroundColor');print('   flyout bg',css)

def t02(page):
    page.locator('[data-rail=portfolio]').hover()
    page.mouse.move(1020,760);page.wait_for_timeout(1100);assert page.locator('#flyout').is_visible()
    page.wait_for_timeout(1050);assert page.locator('#flyout').is_hidden()

def t03(page):
    page.locator('#quickEdit').click()
    assert page.locator('#d18IconCategory').is_visible()
    assert page.locator('#d1QuickExport').is_visible()
    assert page.locator('.d18-quickrow select').count()==4
    page.locator('#d18IconCategory').select_option('market')
    page.locator('#d18IconSymbol').select_option('import')
    assert page.locator('#d18IconImport').count()==1
    page.locator('#dlgCancel').click()
    page.locator('#settingsEntry').click()
    assert page.locator('#d1QuickExport').count()==0

def t04(page):
    page.locator('#settingsEntry').click()
    assert page.locator('#d18SwatchStrip button').count()==5
    assert page.locator('#d18Wheel').is_visible()
    orig=page.locator('html').evaluate('(el)=>getComputedStyle(el).getPropertyValue("--bg").trim()')
    page.locator('#d18ThemeChoose').select_option('1')
    changed=page.locator('html').evaluate('(el)=>getComputedStyle(el).getPropertyValue("--bg").trim()')
    assert changed!=orig, (orig,changed)
    page.locator('#dlgCancel').click()
    back=page.locator('html').evaluate('(el)=>getComputedStyle(el).getPropertyValue("--bg").trim()')
    assert back==orig,(orig,back)

def t05(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting="workbench"]').click()
    assert page.locator('#d18Grid').count()==1
    assert page.locator('[data-d18-page]').count()>=20
    assert page.locator('#d18ChooseType option').count()==8  # 7 + all
    assert page.locator('#d18Canvas').is_visible()
    assert page.locator('#d18ExportLayout').is_visible()
    assert page.locator('#d1QuickExport').count()==0

def t06(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    # Non-custom: A locked
    assert page.locator('#d18ChooseCategory').is_disabled()
    assert 'portfolio' in page.locator('#d18ChooseCategory').input_value()
    page.locator('[data-d18-page="custom-1"]').click()
    assert page.locator('#d18ChooseCategory').is_enabled()
    page.locator('#d18ChooseCategory').select_option('market')
    assert page.locator('#d18ChooseCategory').input_value()=='market'

def t07(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    first=page.locator('[data-d18-drag="overview"]')
    before=first.get_attribute('style')
    rect=first.bounding_box();grid=page.locator('#d18Grid').bounding_box()
    assert rect and grid
    page.mouse.move(rect['x']+30,rect['y']+25);page.mouse.down()
    page.mouse.move(grid['x']+75,grid['y']+6*64+20,steps=10)
    assert page.locator('#d18Ghost').is_visible()
    page.mouse.up()
    after=page.locator('[data-d18-drag="overview"]').get_attribute('style')
    assert before!=after,(before,after)
    page.locator('#dlgCancel').click()
    assert page.locator('#dashboard .card').count()==8

def t08(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    page.locator('#d18CanvasModules').click()
    assert page.locator('#d18ModuleNew').is_visible()
    page.locator('#d18ModuleNew').click()
    assert page.locator('#modGrid').is_visible()
    page.locator('#dlgCancel').click()
    assert page.locator('#d18ModuleNew').is_visible()

def t09(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    page.locator('#d18CanvasModules').click();page.locator('#d18ModuleNew').click()
    page.locator('[data-mod-empty]').first.click()
    page.locator('#dlgSave').click()
    assert page.locator('#d18ModuleNew').is_visible()
    n=page.locator('[data-mact=copy]').count()
    assert n>=2
    page.locator('[data-mact=copy]').last.click()
    assert page.locator('[data-mact=copy]').count()==n+1

def t10(page):
    page.locator('#settingsEntry').click();page.locator('[data-setting=workbench]').click()
    item=page.locator('[data-d18-drag="overview"]')
    orig=item.get_attribute('style')
    page.locator('[data-d18-del="overview"]').click()
    assert page.locator('[data-d18-drag="overview"]').count()==0
    page.locator('#dlgCancel').click()
    page.locator('[data-setting=workbench]').click()
    assert page.locator('[data-d18-drag="overview"]').get_attribute('style')==orig

def t11(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    page.locator('[data-d18-page="UI03"]').click()
    assert page.locator('#d18ChooseCategory').input_value()=='market'
    assert page.locator('#d18ChooseCategory').is_disabled()
    assert page.locator('[data-d18-drag]').count()==0
    page.locator('#dlgCancel').click()
    assert page.locator('#dashboard .card').count()==8

def t12(page):
    page.locator('#settingsEntry').click()
    page.locator('[data-setting=workbench]').click()
    page.locator('[data-d18-page="UI08"]').click()
    page.locator('[data-shared=portfolio]').check()
    page.locator('#dlgSave').click()
    # No mutation of official UI01, current home still 8 modules.
    assert page.locator('#dashboard .card').count()==8

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for key,fn in list(globals().items()):
        if key.startswith('t') and len(key)==3 and key[1:].isdigit() and callable(fn):check('D18-'+key,fn)
    browser.close()
REPORT['passed']=sum(x['result']=='PASS' for x in REPORT['tests'])
REPORT['failed']=sum(x['result']=='FAIL' for x in REPORT['tests'])
Path('/mnt/data/B3_D1_v1_8_REGRESSION_REPORT.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2))
print(json.dumps({'passed':REPORT['passed'],'failed':REPORT['failed']},ensure_ascii=False))