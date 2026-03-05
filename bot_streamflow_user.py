#!/usr/bin/env python3
import asyncio
import os

from dotenv import load_dotenv


load_dotenv()

streamflow_token = (os.getenv("STREAMFLOW_BOT_TOKEN") or "").strip()
if streamflow_token:
    os.environ["BOT_TOKEN"] = streamflow_token

os.environ["ADMIN_PANEL_ENABLED"] = "0"
os.environ["ADMIN_CENTER_MODE"] = "0"

import bot as streamflow_bot  # noqa: E402


if __name__ == "__main__":
    asyncio.run(streamflow_bot.main())
