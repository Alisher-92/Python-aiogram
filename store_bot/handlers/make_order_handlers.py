from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from geopy.geocoders import Nominatim

from config import dp
from .start_handlers import start
from keyboards.make_order_keyboards import *


class OrderForm(StatesGroup):
    cart_id = State()
    full_name = State()
    phone_number = State()
    address = State()
    comment = State()
    accept = State()


@dp.callback_query_handler(lambda call: call.data.startswith("make-order"))
async def start_make_order(call: CallbackQuery, state: FSMContext):
    cart_id = int(call.data.split("_")[-1])
    await call.message.answer("Чтобы оформить заказ, "
                              "вам необходимо будет указать:\n"
                              "- ФИО\n"
                              "- Номер телефона\n"
                              "- Адрес\n"
                              "- Комментарий\n"
                              "Чтобы отменить оформление заказа - /cancel",
                              reply_markup=ReplyKeyboardRemove())
    await get_cart_id(cart_id, state)
    await send_request_full_name(call.message)


async def send_request_full_name(message: Message):
    await message.answer("Введите ФИО: ")
    await OrderForm.full_name.set()


@dp.message_handler(commands=["cancel"], state="*")
async def stop_make_order(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state.startswith("OrderForm"):
        await state.finish()
        await message.answer("Оформление заказа отменено.")
        await start(message)


async def get_cart_id(cart_id: int, state: FSMContext):
    async with state.proxy() as data:
        data["cart_id"] = cart_id


@dp.message_handler(state=OrderForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text
    full_name_list = full_name.split()
    if len(full_name_list) == 3:
        for info in full_name_list:
            if not info.isalpha():
                await message.reply("Недопустимый символ в ФИО !")
                return
        else:
            async with state.proxy() as data:
                data["full_name"] = full_name
            await message.answer("Введите номер телефона: ",
                                 reply_markup=generate_phone_number())
            await OrderForm.next()
    else:
        await message.reply("Необходимо указывать ФИО полностью !")


@dp.message_handler(state=OrderForm.phone_number, content_types=["contact"])
async def get_phone_contact(message: Message, state: FSMContext):
    contact = message.contact
    number = contact["phone_number"]
    phone_number = "+" + number
    async with state.proxy() as data:
        data["phone_number"] = phone_number
    await message.answer("Введите адрес: ",
                         reply_markup=generate_locations_menu())
    await OrderForm.next()


@dp.message_handler(state=OrderForm.phone_number, content_types=["message"])
async def get_phone_number(message: Message, state: FSMContext):
    phone_number = message.text
    if phone_number.startswith("+") and phone_number[1:].isdigit():
        # Запись полученной информации в Прокси туннель
        async with state.proxy() as data:
            data["phone_number"] = phone_number
        # Переключения шага
        await message.answer("Введите адрес: ",
                             reply_markup=generate_locations_menu())
        await OrderForm.next()
    else:
        await message.reply("Примерный формат номер телефона:\n"
                            "+998971234567")


@dp.message_handler(state=OrderForm.address, content_types=["location"])
async def get_address_location(message: Message, state: FSMContext):
    latitude, longitude = message.location["latitude"], message.location["longitude"]
    geolocator = Nominatim(user_agent="fast_food_bot_geolocator17")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    address = location.address
    async with state.proxy() as data:
        data["address"] = address
    await message.answer("Укажите комментарий к заказу: ", reply_markup=generate_comment_menu())
    await OrderForm.next()


@dp.message_handler(state=OrderForm.address, content_types=["text"])
async def get_address_text(message: Message, state: FSMContext):
    address = message.text
    async with state.proxy() as data:
        data["address"] = address
    await message.answer("Укажите комментарий к заказу: ", reply_markup=generate_comment_menu())
    await OrderForm.next()


@dp.message_handler(state=OrderForm.comment)
async def get_comment(message: Message, state: FSMContext):
    comment = message.text
    order_data = {}
    async with state.proxy() as data:
        data["comment"] = comment

        order_data["cart_id"] = data["cart_id"]
        order_data["full_name"] = data["full_name"]
        order_data["phone_number"] = data["phone_number"]
        order_data["address"] = data["address"]
        order_data["comment"] = comment
    await message.answer(f"Детали вашего заказа: \n\n"
                         f"ID корзины: {order_data['cart_id']}\n"
                         f"Имя заказчика: {order_data['full_name']}\n"
                         f"Номер телефона: {order_data['phone_number']}\n"
                         f"Адрес: {order_data['address']}\n"
                         f"Комментарии к заказу: {order_data['comment']}",
                         reply_markup=generate_accept_menu())
    await OrderForm.next()
