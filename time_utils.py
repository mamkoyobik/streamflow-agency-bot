from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

DEFAULT_DISPLAY_TZ = timezone(timedelta(hours=3))
_OFFSET_RE = re.compile(
    r"^(?:UTC|GMT)?\s*([+-])?\s*(\d{1,2})(?::?(\d{2}))?$",
    re.IGNORECASE,
)
# Do not prioritize generic `TZ` from hosting platform because it is often `UTC`
# and causes confusing offsets in user-facing timestamps.
_ENV_TZ_KEYS = ("APP_TIMEZONE", "DISPLAY_TZ", "TIMEZONE")


def _parse_offset_timezone(value: str):
    raw = (value or "").strip().upper()
    if not raw:
        return None
    match = _OFFSET_RE.match(raw)
    if not match:
        return None
    sign = -1 if match.group(1) == "-" else 1
    hours = int(match.group(2))
    minutes = int(match.group(3) or "0")
    if hours > 14 or minutes > 59:
        return None
    offset = timedelta(hours=hours, minutes=minutes) * sign
    return timezone(offset)


@lru_cache(maxsize=1)
def get_display_tz():
    for key in _ENV_TZ_KEYS:
        value = os.getenv(key, "").strip()
        if not value:
            continue
        tz = _parse_offset_timezone(value)
        if tz is not None:
            return tz
        if ZoneInfo is not None:
            try:
                return ZoneInfo(value)
            except Exception:
                pass
    return DEFAULT_DISPLAY_TZ


def format_submit_time(timestamp: str | None) -> str:
    tz = get_display_tz()
    if not timestamp:
        return datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    try:
        dt = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            # Legacy records may be saved without timezone and already in display timezone.
            dt = dt.replace(tzinfo=tz)
        return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(timestamp)
