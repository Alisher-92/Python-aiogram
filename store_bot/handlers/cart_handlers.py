from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from config import dp
from database.tools import UserTools, ProductTools, CartProductTools
from keyboards.cart_keyboards import *


@dp.message_handler(Text(equals="🛒 Корзинка"))
async def show_cart(message: Message, edit: bool = False):
    chat_id = message.chat.id
    user_id = UserTools().get_user_id(chat_id)
    cart_id, _, cart_price = UserTools().get_active_cart(user_id)

    cart_text = "Ваша корзина: \n\n"
    cart_products = CartProductTools().get_cart_products(cart_id)
    if not cart_products:
        await message.answer("Корзина пуста !")
        if edit:
            await message.delete()
        return
    cart_product_info = []
    i = 0
    for product_id, product_name, quantity, units, total_price in cart_products:
        cart_product_info.append((f"❌  {product_name}", product_id))
        i += 1
        cart_text += f"{i}. {product_name}\n"  \
                     f"    Кол-во: {quantity} {units}\n"  \
                     f"    Общая стоимость: {total_price} сум.\n\n"
    cart_text += f"Общая стоимость корзины: {cart_price} сум."
    if edit:
        await message.edit_text(cart_text,
                                reply_markup=generate_delete_cart_products(cart_product_info, cart_id))
    else:
        await message.answer(cart_text,
                         reply_markup=generate_delete_cart_products(cart_product_info, cart_id))


@dp.callback_query_handler(lambda call: call.data.startswith("add-cart"))
async def add_cart_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = UserTools().get_user_id(chat_id)
    cart_id = UserTools().get_active_cart(user_id)[0]

    _, product_id, current_qty = call.data.split("_")
    product_id, current_qty = int(product_id), int(current_qty)
    product_name = ProductTools().get_product_name(product_id)
    _, _, product_price, _, _, units, _, _ = ProductTools().get_product_detail(product_name)
    total_price = product_price * current_qty

    status_add = CartProductTools().add_cart_product(cart_id, product_id, product_name,
                                                     current_qty, units, total_price)
    if status_add:
        await call.answer("Продукт успешно добавлен !")
    else:
        await call.answer("Количество успешно изменено !")
    UserTools().recalc_cart(cart_id)


@dp.callback_query_handler(lambda call: call.data.startswith("delete-cart"))
async def delete_cart_product(call: CallbackQuery):
    _, cart_id, product_id = call.data.split("_")
    cart_id, product_id = int(cart_id), int(product_id)
    CartProductTools().delete_cart_product(cart_id, product_id)
    await call.answer("Продукт был успешно удалён !")
    UserTools().recalc_cart(cart_id)
    await show_cart(call.message, edit=True)
