import logging

from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def _safe_answer(call: CallbackQuery, text: str | None = None, show_alert: bool = False):
    try:
        if text is None:
            await call.answer()
        else:
            await call.answer(text, show_alert=show_alert)
    except Exception:
        pass

async def edit_or_send(call: CallbackQuery, text: str, reply_markup=None):
    await _safe_answer(call)
    message = call.message
    if message is None:
        return
    try:
        if message.photo or message.caption is not None:
            await message.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        err = str(e).lower()
        if "message is not modified" in err:
            return
        try:
            await message.answer(text, reply_markup=reply_markup)
        except Exception:
            logger.exception("Failed to send fallback message in edit_or_send")
    except Exception:
        try:
            await message.answer(text, reply_markup=reply_markup)
        except Exception:
            logger.exception("Failed to send fallback message in edit_or_send")

async def edit_caption_or_send(message: Message, caption: str, reply_markup=None):
    try:
        await message.edit_caption(caption=caption, reply_markup=reply_markup)
    except Exception:
        await message.answer(caption, reply_markup=reply_markup)
