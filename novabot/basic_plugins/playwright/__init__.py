import sys
import os

from typing import Optional
from playwright.__main__ import main
from playwright.async_api import Browser, async_playwright

from nonebot import get_driver


driver = get_driver()
sys.argv = ["", "install", "chromium"]
os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.sk415.workers.dev"

browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global browser
    browser = await async_playwright().start()
    browser = await browser.chromium.launch(**kwargs)
    return browser


async def get_browser(**kwargs) -> Browser:
    return browser or await init(**kwargs)


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


driver.on_startup(install)
driver.on_startup(init)
