"""Stub mock server for KKTIX."""
from aiohttp import web


class KKTIxMockServer:
    def __init__(self):
        self._runner = None

    async def start(self, port: int = 0) -> int:
        self._runner = web.AppRunner(web.Application())
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", port)
        await site.start()
        return site._server.sockets[0].getsockname()[1]

    async def stop(self):
        if self._runner:
            await self._runner.cleanup()
