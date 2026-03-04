#!/usr/bin/env python3
import asyncio
import os

from dotenv import load_dotenv


def _required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _configure_runtime() -> None:
    load_dotenv()

    # Keep legacy streamflow token for outbound user messages from central admin bot.
    streamflow_token = (os.getenv("STREAMFLOW_BOT_TOKEN") or "").strip()
    if not streamflow_token:
        legacy_token = (os.getenv("BOT_TOKEN") or "").strip()
        if legacy_token:
            os.environ["STREAMFLOW_BOT_TOKEN"] = legacy_token

    os.environ["BOT_TOKEN"] = _required_env("ADMIN_CENTER_BOT_TOKEN")
    os.environ["ADMIN_PANEL_ENABLED"] = "1"
    os.environ["ADMIN_CENTER_MODE"] = "1"


_configure_runtime()

import bot as streamflow_bot  # noqa: E402


if __name__ == "__main__":
    asyncio.run(streamflow_bot.main())
