from aiogram.types import Message

from config import dp
from keyboards.start_keyboards import *
from database.tools import UserTools


@dp.message_handler(commands=["start"])
async def start(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    await register_user(full_name, chat_id)
    await register_cart(chat_id)
    await message.answer(f"Выберите направления: ",
                         reply_markup=generate_main_menu())


async def register_user(full_name: str, chat_id: int):
    UserTools().register_user(full_name, chat_id)


async def register_cart(chat_id: int):
    user_id = UserTools().get_user_id(chat_id)
    UserTools().register_cart(user_id)
