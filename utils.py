from aiogram.types import CallbackQuery, Message

async def edit_or_send(call: CallbackQuery, text: str, reply_markup=None):
    try:
        await call.message.edit_text(text, reply_markup=reply_markup)
    except:
        await call.message.answer(text, reply_markup=reply_markup)
    await call.answer()

async def edit_caption_or_send(message: Message, caption: str, reply_markup=None):
    try:
        await message.edit_caption(caption=caption, reply_markup=reply_markup)
    except:
        await message.answer(caption, reply_markup=reply_markup)