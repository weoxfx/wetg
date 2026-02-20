"""
WETG runner helpers — run .wetg files from Python code.
"""

import asyncio
import os
from .interpreter import Wetg


def run_file(filepath: str):
    """
    Run a .wetg file. Blocking call — runs until Ctrl+C.

    Example:
        from wetg_superweox import run_file
        run_file("mybot.wetg")
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    bot = Wetg(code)
    bot.parse()
    asyncio.run(bot.run())


async def run_file_async(filepath: str):
    """
    Async version of run_file. Use when you're already inside an async context.

    Example:
        import asyncio
        from wetg import run_file_async
        asyncio.run(run_file_async("mybot.wetg"))
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    bot = Wetg(code)
    bot.parse()
    await bot.run()