from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ...config import LOG_FILE
from typing import AsyncGenerator
from io import SEEK_END
import asyncio
import aiofiles

admin_router = APIRouter()

@admin_router.get("/")
async def stream_logs() -> StreamingResponse:
    async def logs_iterator():
        async with aiofiles.open(LOG_FILE, 'r', encoding='utf-8') as f:
            await f.seek(0, SEEK_END)
            while True:
                log = await f.readline()
                if not log:
                    await asyncio.sleep(0.5)
                    continue
                await asyncio.sleep(0.2)
                yield log


    return StreamingResponse(
        content=logs_iterator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
        media_type="text/plain"
    )

