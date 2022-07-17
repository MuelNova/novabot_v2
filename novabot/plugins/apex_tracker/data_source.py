import base64
import json

from typing import Dict
from aiohttp import ClientSession
from PIL import Image
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment
from novabot.basic_plugins.playwright import get_browser
from novabot.utils.image_utils import BuildImage, Text2Image

from .config import APEXLEGEND_PRED_URL


async def get_tracker_data(url: str) -> MessageSegment:
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
        return MessageSegment.image(image)
    except Exception:
        if page:
            await page.close()
        raise


async def get_master_and_pred_raw_data(API_KEY: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    async with ClientSession() as session:
        async with session.get(APEXLEGEND_PRED_URL + API_KEY) as resp:
            if resp.status == 200:
                return json.loads((await resp.read()).decode())
            else:
                raise ConnectionError(resp.status, await resp.read())


async def get_master_and_pred_image(API_KEY: str) -> MessageSegment:
    data = await get_master_and_pred_raw_data(API_KEY)
    RP_pred = "{:,} RP".format(data.get('RP', {}).get('PC', {}).get('val', 0))
    AP_pred = "{:,} AP".format(data.get('AP', {}).get('PC', {}).get('val', 0))
    RP_master = "{:,} players".format(data.get('RP', {}).get('PC', {}).get('totalMastersAndPreds', 0))
    AP_master = "{:,} players".format(data.get('AP', {}).get('PC', {}).get('totalMastersAndPreds', 0))

    background = Image.new('RGBA', (1600, 800), "#1f1f1f")
    blank = Image.new('RGBA', (600, 160), "#292929")
    blank = BuildImage(blank).circle_corner(40).image
    pred_blank = blank.copy()
    master_blank = blank.copy()

    # Predator
    image = Image.open(Path(__file__).parent / "predator.png", 'r').convert('RGBA')
    pred_blank.paste(image, (20, 20), image)
    txt = Text2Image.from_text("Predator Cutoff", 50, weight='bold', fill='#cccccc', align='center').to_image()
    pred_blank.paste(txt, (160, 5), txt)
    RP_pred_blank = pred_blank
    AP_pred_blank = pred_blank.copy()

    # Master
    image = Image.open(Path(__file__).parent / "master.png", 'r').convert('RGBA')
    master_blank.paste(image, (20, 20), image)
    txt = Text2Image.from_text("Master/Predator", 50, weight='bold', fill='#cccccc', align='center').to_image()
    master_blank.paste(txt, (160, 5), txt)
    RP_master_blank = master_blank
    AP_master_blank = master_blank.copy()

    txt_rp = Text2Image.from_text(RP_pred, 60, weight='bold', fill='#efefef').to_image()
    txt_ap = Text2Image.from_text(AP_pred, 60, weight='bold', fill='#efefef').to_image()
    RP_pred_blank.paste(txt_rp, (155, 60), txt_rp)
    AP_pred_blank.paste(txt_ap, (155, 60), txt_ap)

    txt_rp = Text2Image.from_text(RP_master, 60, weight='bold', fill='#efefef').to_image()
    txt_ap = Text2Image.from_text(AP_master, 60, weight='bold', fill='#efefef').to_image()
    RP_master_blank.paste(txt_rp, (155, 60), txt_rp)
    AP_master_blank.paste(txt_ap, (155, 60), txt_ap)

    txt = Text2Image.from_text("Battle Royal", 100, weight='bold', fill='#efefef').to_image()
    background.paste(txt, (30, 30), txt)
    txt = Text2Image.from_text("追猎指南", 100, weight='bold', fill='#efefef').to_image()
    background.paste(txt, (1000, 30), txt)
    background.paste(RP_pred_blank, (100, 200), RP_pred_blank)
    background.paste(RP_master_blank, (900, 200), RP_master_blank)
    background.paste(AP_pred_blank, (100, 400), AP_pred_blank)
    background.paste(AP_master_blank, (900, 400), AP_master_blank)
    txt = Text2Image.from_text("Arenas", 100, weight='bold', fill='#efefef').to_image()
    background.paste(txt, (60, 550), txt)
    txt = Text2Image.from_text("* All Masters have a hidden ladder ranking that is only displayed when being a Predator"
                               " (you can still see it on the website on your profile page). The total"
                               " amount of masters is guessed using the highest ranking found in the"
                               " ALS database. The number found is very likely to be under-estimated,"
                               " as all masters players are not in the ALS database. However, if the last"
                               " master is in our database, the ranking will be 100% accurate.", 20, style='italic',
                               fill='#efefef').wrap(800).to_image()
    background.paste(txt, (800, 650), txt)
    path = Path(__file__).parent / 'apex_pred_img.png'
    background.resize((1000, 500)).save(path)
    return MessageSegment.image(path)


