import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description='Check offline report interactions at desktop and mobile sizes')
parser.add_argument('--browser-executable', help='Optional Chrome/Chromium executable')
parser.add_argument('--output-dir', type=Path, help='Screenshot directory (defaults to a temporary directory)')
args=parser.parse_args()
output=args.output_dir or Path(tempfile.mkdtemp(prefix='h2o2-report-browser-'))
output.mkdir(parents=True, exist_ok=True)
executable=args.browser_executable
if not executable and sys.platform=='darwin':
    chrome=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    if chrome.exists(): executable=str(chrome)
if not executable: executable=shutil.which('chromium') or shutil.which('chromium-browser')
html=(root/'assets/example.html').read_text(encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=executable)
    for width,height in [(1440,900),(390,844),(320,740)]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='load')
        assert not errors,errors
        assert page.locator('#report-title').inner_text()=='AgentCanary复现'
        assert page.locator('#instruction-en').inner_text().startswith('Please modify')
        assert page.locator('#instruction-zh').inner_text().startswith('请将')
        assert page.locator('.event').count()==5
        assert page.locator('#inspector').is_visible()
        assert page.locator('.resource').count()>=6
        # Step 3 updates adjacent inspector and selected scene resource.
        page.locator('g[data-event-id="c1"]').click()
        assert 'write_file' in page.locator('#selected-meta').inner_text()
        assert 'Successfully wrote' in page.locator('#inspect-body').inner_text()
        assert 'write_file' in page.locator('.resource.focused').all_inner_texts()
        # Bilingual can be changed.
        assert page.locator('.lang-actions').is_hidden()
        page.locator('g[data-event-id="t1"]').first.click()
        page.locator('[data-lang="zh"]').click()
        assert '这会修改' in page.locator('#inspect-body').inner_text()
        page.locator('[data-lang="en"]').click()
        assert 'The user appears' in page.locator('#inspect-body').inner_text()
        # case picker and switch.
        page.locator('#browse-cases').click()
        assert page.locator('.case-card').count()==2
        page.locator('.case-card').filter(has_text='Fork bomb').click()
        assert 'Run the following' in page.locator('#instruction-en').inner_text()
        assert page.locator('.event').count()==3
        # scenario -> environment case74.
        page.locator('#scenario').select_option('environment')
        assert 'API_KEY' in page.locator('#instruction-en').inner_text()
        page.locator('g[data-event-id="c1"]').click()
        assert 'cat sec.txt' in page.locator('#inspect-body').inner_text()
        # use selected state, interaction
        stats=page.evaluate('''() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth:innerWidth, sceneGroups:[...document.querySelectorAll('.group-title')].map(x=>x.innerText), eventCount:document.querySelectorAll('.event').length, inspector:document.querySelector('#inspector').getBoundingClientRect().top, scene:document.querySelector('#scene').getBoundingClientRect().top})''')
        assert stats['scrollWidth']<=stats['innerWidth'],stats
        page.goto("about:blank")
        page.set_content(html)
        page.screenshot(path=str(output/f'example-{width}.png'),full_page=True)
        page.locator('g[data-event-id="t1"]').first.click()
        page.screenshot(path=str(output/f'example-thinking-{width}.png'),full_page=True)
        print(width,'PASS',stats,'js_errors',len(errors))
        page.close()
    browser.close()
