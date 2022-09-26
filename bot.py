import asyncio
from botpy import Client, Intents
from botpy.message import Message

from configs.config import config
from plugins.maimaidx import mairank, maib40
from plugins.bind import bind
from plugins.jrys import jrys
from plugins.otogesongs import search_songs, song_id
from service.db_context import init, disconnect


class TippyClient(Client):

    async def on_at_message_create(self, message: Message):
        handlers = [mairank, bind, maib40, jrys, search_songs, song_id]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return


if __name__ == '__main__':
    try:
        # init database
        loop = asyncio.get_event_loop()
        # 执行coroutine
        loop.run_until_complete(init())
        intents = Intents(public_guild_messages=True)
        client = TippyClient(intents=intents)
        client.run(appid=config['appid'], token=config['token'])
    except KeyboardInterrupt:
        loop = asyncio.get_event_loop()
        # 执行coroutine
        loop.run_until_complete(disconnect())