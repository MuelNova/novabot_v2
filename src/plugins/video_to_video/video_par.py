from ffmpy3 import FFmpeg
from typing import Union, Optional, List
from pathlib import Path


async def compress(path: Union[str, Path], arg: Optional[Union[str, List[str]]] = None):
    if arg is None:
        arg = '-b:v 10M -c:a copy -c:v libx264 -y'
    if isinstance(path, str):
        path = Path(path)
    ff = FFmpeg(
        inputs={str(path): None},
        outputs={str(path)+"_compressed.mp4": arg}
    )
    await ff.run_async()
    return await ff.wait()


if __name__ == '__main__':
    import asyncio
    event = asyncio.new_event_loop()
    asyncio.set_event_loop(event)
    event.run_until_complete(compress(Path(__file__).parent / 'test.mp4'))
