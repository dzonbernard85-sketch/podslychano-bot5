# student_bot.py
import html
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID

logger = logging.getLogger(__name__)

class StudentForm(StatesGroup):
    waiting_for_text = State()

def get_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Написать сообщение", callback_data="write_message"))
    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_write"))
    return builder.as_markup()

def register_student_handlers(dp: Dispatcher, student_bot: Bot, moderator_bot: Bot):
    
    @dp.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "👋 Добро пожаловать в «Подслушано ОЦ №7»!\n\n"
            "Здесь ты можешь анонимно поделиться своей историей.\n"
            "Твоё сообщение пройдет проверку и появится в @podslychanooc7",
            reply_markup=get_start_keyboard()
        )

    @dp.callback_query(F.data == "write_message")
    async def start_writing(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "✍️ Напиши своё сообщение одним текстом:",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(StudentForm.waiting_for_text)
        await callback.answer()

    @dp.callback_query(F.data == "cancel_write")
    async def cancel_writing(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text("Отменено.", reply_markup=get_start_keyboard())
        await callback.answer()

    @dp.message(Command("cancel"))
    async def cmd_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Отменено.", reply_markup=get_start_keyboard())

    @dp.message(StudentForm.waiting_for_text, F.text)
    async def receive_student_message(message: Message, state: FSMContext):
        text = message.text.strip()
        if not text:
            await message.answer("Пустое сообщение. Напиши текст.")
            return

        student_chat_id = message.chat.id
        student_message_id = message.message_id

        # Экранируем HTML, чтобы спецсимволы не сломали бота
        safe_text = html.escape(text)

        card_text = (
            "📩 <b>НОВОЕ СООБЩЕНИЕ</b>\n\n"
            f"Текст сообщения:\n<pre>{safe_text}</pre>\n\n"
            "Статус: ⏳ Ожидает проверки."
        )

        callback_data_approve = f"approve:{student_chat_id}:{student_message_id}"
        callback_data_reject = f"reject:{student_chat_id}:{student_message_id}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=callback_data_approve),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=callback_data_reject),
            ]
        ])

        try:
            await moderator_bot.send_message(
                chat_id=ADMIN_ID,
                text=card_text,
                reply_markup=keyboard
            )
            await message.answer("✅ Твоё сообщение отправлено на проверку!", reply_markup=get_start_keyboard())
        except Exception as e:
            logger.error(f"Ошибка отправки модератору: {e}")
            await message.answer("⚠️ Ошибка отправки. Попробуй позже.")

        await state.clear()