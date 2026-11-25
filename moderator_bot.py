# moderator_bot.py
import html
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID, CHANNEL_ID

logger = logging.getLogger(__name__)
processed_callbacks = set()

def register_moderator_handlers(dp: Dispatcher, moderator_bot: Bot):

    @dp.message(Command("start"))
    async def moderator_start(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        await message.answer("👋 Бот модерации готов. Жду сообщений.")

    @dp.callback_query(F.data.startswith("approve:"))
    async def approve_message(callback: CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            return
        
        cb_data = callback.data
        if cb_data in processed_callbacks:
            await callback.answer("Уже обработано!", show_alert=True)
            return
        
        processed_callbacks.add(cb_data)

        # Достаем текст из карточки
        original_text = callback.message.text or ""
        try:
            text_to_publish = original_text.split("<pre>")[1].split("</pre>")[0]
        except IndexError:
            await callback.answer("Ошибка чтения текста.", show_alert=True)
            return

        channel_post = (
            "📩 <b>ПОДСЛУШАНО ОЦ №7</b>\n\n"
            f"<blockquote>{text_to_publish}</blockquote>"
        )

        try:
            await moderator_bot.send_message(chat_id=CHANNEL_ID, text=channel_post)
            await callback.message.delete()
            await callback.answer("✅ Опубликовано!")
        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")
            processed_callbacks.discard(cb_data)
            await callback.answer("⚠️ Не удалось опубликовать. Проверь права бота в канале.", show_alert=True)

    @dp.callback_query(F.data.startswith("reject:"))
    async def reject_message(callback: CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            return
            
        cb_data = callback.data
        if cb_data in processed_callbacks:
            await callback.answer("Уже обработано!", show_alert=True)
            return
            
        processed_callbacks.add(cb_data)
        try:
            await callback.message.delete()
            await callback.answer("❌ Отклонено.")
        except Exception:
            pass