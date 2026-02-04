from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

async def edit_or_send(call: CallbackQuery, text: str, reply_markup=None):
    try:
        if call.message.photo or call.message.caption is not None:
            await call.message.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await call.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await call.answer()
            return
        await call.message.answer(text, reply_markup=reply_markup)
    except Exception:
        await call.message.answer(text, reply_markup=reply_markup)
    await call.answer()

async def edit_caption_or_send(message: Message, caption: str, reply_markup=None):
    try:
        await message.edit_caption(caption=caption, reply_markup=reply_markup)
    except:
        await message.answer(caption, reply_markup=reply_markup)
