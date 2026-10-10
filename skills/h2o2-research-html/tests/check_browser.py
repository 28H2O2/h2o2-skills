"""Development check for the two standalone reading examples; no output runtime dependencies."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--browser-executable')
    args = parser.parse_args()
    output = args.output_dir or Path(tempfile.mkdtemp(prefix='h2o2-research-check-'))
    output.mkdir(parents=True, exist_ok=True)
    executable = args.browser_executable
    chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    if not executable and sys.platform == 'darwin' and chrome.exists():
        executable = str(chrome)
    if not executable:
        executable = shutil.which('chromium') or shutil.which('chromium-browser')
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=executable)
        try:
            for width, height in [(1440, 900), (390, 844), (320, 740)]:
                for example in ['openclaw-brief', 'source-review']:
                    page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
                    errors, requests = [], []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    def block_network(route):
                        requests.append(route.request.url)
                        route.abort()
                    page.route('http://**', block_network)
                    page.route('https://**', block_network)
                    page.goto((ROOT / 'assets' / (example + '.html')).as_uri())
                    assert page.locator('details[open]').count() == 0
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.screenshot(path=str(output / f'{example}-{width}.png'), full_page=width != 1440)
                    if example == 'openclaw-brief':
                        assert '先试 Canary' in page.locator('h1').inner_text()
                        assert '尚未完成 OpenClaw 实测' in page.locator('.status').inner_text()
                        assert page.locator('svg:visible').count() == 1
                        assert page.locator('#history .detail-body').is_hidden()
                        if width == 1440:
                            assert page.locator('figure').bounding_box()['y'] + page.locator('figure').bounding_box()['height'] < 900
                        # A citation reveals its evidence without a second click.
                        page.locator('a[href="#sources"]').first.click()
                        assert page.locator('#sources').get_attribute('open') is not None
                        assert page.locator('#sources .detail-body').is_visible()
                        page.locator('#sources summary').click()
                    else:
                        assert page.locator('svg').count() == 0
                        assert '未执行测试' in page.locator('.status').inner_text()
                    # All folded facts remain available; expanding never causes page overflow.
                    for detail in page.locator('details').all():
                        detail.locator('summary').click()
                        assert detail.get_attribute('open') is not None
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        detail.locator('summary').click()
                    # Native disclosure is also operable using a keyboard.
                    summary = page.locator('summary').first
                    summary.focus()
                    summary.press('Enter')
                    assert page.locator('details').first.get_attribute('open') is not None
                    summary.press('Enter')
                    assert not errors, errors
                    assert not requests, requests
                    results.append({'example': example, 'viewport': [width, height], 'result': 'PASS',
                                    'network_requests': len(requests), 'js_errors': len(errors)})
                    print(example, width, 'PASS: offline, disclosure, keyboard, width and first-screen checks')
                    page.close()
        finally:
            browser.close()
    (output / 'research-checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
