# Стартовая функция start_review
#   ФИО
#   Номер телефона
#   Отзыв
# Конечная функция stop_review
#   ФИО - get_full_name
#   Номер телефона - get_phone_number
#   Отзыв get_review
from datetime import datetime

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from .start_handlers import start
from database.tools import ReviewTools, UserTools
from config import bot, dp, ADMINS


# Создание формы, наших шагов
class ReviewForm(StatesGroup):
    full_name = State()
    phone_number = State()
    review = State()


@dp.message_handler(Text(equals="✍ Оставить отзыв"))
async def start_review(message: Message):
    await message.answer("Что бы оставить отзыв, вам необходимо заполнить "
                         "следующие поля:\n"
                         "- ФИО\n"
                         "- Номер телефона\n"
                         "- Отзыв\n\n"
                         "Что бы отменить отправку отзыва - /stop",
                         reply_markup=ReplyKeyboardRemove())
    await request_full_name(message)


async def request_full_name(message: Message):
    await message.answer("Введите ФИО :")
    await ReviewForm.full_name.set()


@dp.message_handler(state="*", commands=["stop"])
async def stop_review(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state.startswith("ReviewForm"):
        await state.finish()
        await message.answer("Отправка отзыва отменена.")
        await start(message)


@dp.message_handler(state=ReviewForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text
    full_name_list = full_name.split()
    if len(full_name_list) == 3:
        # Валидация ФИО
        for info in full_name_list:
            if not info.isalpha():
                await message.reply("Недопустимы символ в ФИО !")
                return
        else:
            # Запись полученной информации в Прокси тоннель
            async with state.proxy() as data:
                data["full_name"] = full_name
            # Переключения шага
            await message.answer("Введите номер телефона: ")
            await ReviewForm.next()
    else:
        await message.reply("Необходимо указывать ФИО полностью !")


@dp.message_handler(state=ReviewForm.phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    phone_number = message.text
    if phone_number.startswith("+") and phone_number[1:].isdigit():
        # Запись полученной информации в Прокси туннель
        async with state.proxy() as data:
            data["phone_number"] = phone_number
        # Переключения шага
        await message.answer("Введите отзыв: ")
        await ReviewForm.next()
    else:
        await message.reply("Примерный формат номер телефона:\n"
                            "+998971234567")


@dp.message_handler(state=ReviewForm.review)
async def get_review(message: Message, state: FSMContext):
    review = message.text
    user_data = {}
    async with state.proxy() as data:
        data["review"] = review

        user_data["full_name"] = data["full_name"]
        user_data["phone_number"] = data["phone_number"]
        user_data["review"] = review
    await write_review_db(message, user_data)
    await state.finish()
    await message.answer("Спасибо за отзыв !")
    await send_review_info_admins(user_data)
    await start(message)


async def write_review_db(message: Message, user_data: dict):
    chat_id = message.chat.id
    ReviewTools().add_review(
        user_id=UserTools().get_user_id(chat_id),
        full_name=user_data["full_name"],
        phone_number=user_data["phone_number"],
        review=user_data["review"],
        create_datetime=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


async def send_review_info_admins(user_data: dict):
    for admin_id in ADMINS.values():
        await bot.send_message(admin_id, text="Новый отзыв !\n\n"
                                              f"От пользователя: {user_data['full_name']}\n"
                                              f"Телефон: {user_data['phone_number']}\n"
                                              f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                                              f"Отзыв: {user_data['review']}")
