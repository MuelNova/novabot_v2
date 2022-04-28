import sys
import os
import base64

from typing import Optional
from playwright.__main__ import main
from playwright.async_api import Browser, async_playwright

sys.argv = ["", "install", "chromium"]
os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.sk415.workers.dev"

_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    browser = await async_playwright().start()
    _browser = await browser.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


async def get_tracker_data(url: str):
    browser = await get_browser()
    page = None
    try:
        page = await browser.new_page(device_scale_factor=2)
        await page.goto(url, wait_until="load", timeout=20000)
        await page.set_viewport_size({"width": 2560, "height": 1080})
        card = page.locator('div[class="trn-grid trn-grid--vertical trn-grid--small"]')
        assert card
        clip = await card.bounding_box()
        assert clip
        image = await page.screenshot(clip=clip, full_page=True)
        await page.close()
        with open('img.png', 'wb') as f:
            f.write(image)
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


def install():
    """自动安装、更新 Chromium"""

    def restore_env():
        del os.environ["PLAYWRIGHT_DOWNLOAD_HOST"]
        if original_proxy is not None:
            os.environ["HTTPS_PROXY"] = original_proxy

    sys.argv = ["", "install", "chromium"]
    original_proxy = os.environ.get("HTTPS_PROXY")
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.sk415.workers.dev"
    success = False
    try:
        main()
    except SystemExit as e:
        if e.code == 0:
            success = True
    if not success:
        os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = ""
        try:
            main()
        except SystemExit as e:
            if e.code != 0:
                restore_env()
                raise RuntimeError("未知错误，Chromium 下载失败")
    restore_env()
