from aiohttp import ClientSession, TCPConnector
from typing import Union, Dict, List

from nonebot import on_command, get_driver
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment

from .config import Config

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

send_video = on_command('.send_video')
rm_video = on_command('.remove_video')

supported_file_suffix = ['mp4', 'flv', 'wmv', 'avi']


@send_video.handle()
async def _(state: T_State, event: GroupMessageEvent, bot: Bot):
    logger.info(state)
    logger.info(event.dict())
    files: Dict[str, List] = await bot.call_api('get_group_root_files', group_id=event.group_id)
    files: List[Dict[str, Union[str, int]]] = files.get('files')
    r_file = None
    suffix = ''
    for file in files:
        if len(f := file.get('file_name', '').split('.')) > 1:
            suffix = f[-1]
            if suffix in supported_file_suffix:
                r_file = file
                break
    try:
        assert r_file
    except AssertionError:
        await send_video.finish('No Supported Video File Found!')
    url: Dict[str, str] = await bot.call_api('get_group_file_url',
                                             group_id=event.group_id,
                                             file_id=r_file.get('file_id'),
                                             busid=r_file.get('busid'))
    print(url)
    if not (f_url := url.get('url')):
        await send_video.finish('Error occurred while getting the video file url')
    await bot.send(event, 'Downloading...')
    try:
        connector = TCPConnector(force_close=True, limit=50)
        async with ClientSession(connector=connector) as session:
            async with session.get(f_url) as r:
                if r.status != 200:
                    raise ConnectionError(r.status)
                if not config.data_path.exists():
                    config.data_path.mkdir(parents=True)
                with open(config.data_path / f'temp.{suffix}', 'wb') as fd:
                    async for chunk in r.content.iter_chunked(1024):
                        fd.write(chunk)
    except Exception as e:
        await send_video.finish(f'Error occurred while downloading the video file url\n{e}')
    await bot.send(event, 'Video downloaded! Trying to send now...')
    await send_video.finish(MessageSegment.video(file=config.data_path / f'temp.{suffix}'))


@rm_video.handle()
async def _():
    config.data_path.unlink(missing_ok=True)
