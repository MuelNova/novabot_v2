import base64

from novabot.basic_plugins.playwright import get_browser


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
