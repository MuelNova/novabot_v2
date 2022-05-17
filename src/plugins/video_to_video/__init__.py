from aiohttp import ClientSession, TCPConnector
from pathlib import Path
from typing import Union, Dict, List
from time import time

from nonebot import on_command, get_driver
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment, Message

from .config import Config
from .video_par import compress

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

send_video = on_command('.send_video')
compress_video = on_command('.compress_video')
rm_video = on_command('.remove_video')

supported_file_suffix = ['mp4', 'flv', 'wmv', 'avi']


@send_video.handle()
async def _(state: T_State, event: GroupMessageEvent, bot: Bot, arc: Message = CommandArg()):
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
    if r_file.get('file_size') > 300 * 1024 * 1024:
        await send_video.finish('Video is too big! Maximum 300Mb supported')
    url: Dict[str, str] = await bot.call_api('get_group_file_url',
                                             group_id=event.group_id,
                                             file_id=r_file.get('file_id'),
                                             busid=r_file.get('busid'))
    if not (f_url := url.get('url')):
        await send_video.finish('Error occurred while getting the video file url')
    await bot.send(event, 'Downloading...')
    try:
        connector = TCPConnector(force_close=True, limit=50)
        async with ClientSession(connector=connector) as session:
            async with session.get(f_url, timeout=None) as r:
                if r.status != 200:
                    raise ConnectionError(r.status)
                if not config.data_path.exists():
                    config.data_path.mkdir(parents=True)
                total_size = 0
                now_downloaded = total_size // (1024 * 1024)
                start = time()
                with open(config.data_path / f'temp.{suffix}', 'wb') as fd:
                    async for chunk in r.content.iter_chunked(16144):
                        total_size += len(chunk)
                        if total_size // (1024 * 1024) != now_downloaded:
                            now_downloaded = total_size // (1024 * 1024)
                            logger.info(f'{time() - start:0.2f}s, downloaded: {total_size / (1024 * 1024):0.0f}MB')
                        fd.write(chunk)
    except Exception as e:
        await send_video.finish(f'Error occurred while downloading the video file url\n{e}')
    await bot.send(event, 'Video downloaded! Trying to send now...')
    try:
        if arc:
            await compress(path=config.data_path / f'temp.{suffix}')
            await send_video.finish(MessageSegment.video(file=config.data_path / f'temp.{suffix}_compressed.mp4'))
        else:
            await send_video.finish(MessageSegment.video(file=config.data_path / f'temp.{suffix}'))
    except ActionFailed:
        await send_video.finish("Error While Sending the video, the file could be too large to send\n"
                                "You can try compress it")


@compress_video.handle()
async def _(event: GroupMessageEvent, bot: Bot, arc: Message = CommandArg()):
    files = config.data_path.iterdir()
    file = next((f for f in files if f.name.replace(f.suffix, '') == 'temp'), None)
    if not file:
        await compress_video.finish("No video found!")
    await bot.send(event, 'Compressing...')
    try:
        if arc:
            await compress(path=file, arg=str(arc))
        else:
            await compress(path=file)
        await bot.send(event, 'Compressed, now trying to send...')
        print(f'{str(file)}_compressed.mp4')
        await compress_video.finish(
            MessageSegment.video(file=Path(f'{str(file)}_compressed.mp4'))
        )

    except ActionFailed:
        await compress_video.finish("Error While Sending the video, the file could be too large to send\n"
                                    "You can try compress it")


@rm_video.handle()
async def _():
    config.data_path.unlink(missing_ok=True)
