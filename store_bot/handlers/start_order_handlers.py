from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text

from .start_handlers import start
from config import dp
from keyboards.start_order_keyboards import *
from database.tools import CategoryTools, ProductTools


@dp.message_handler(Text(equals="✅ Начать заказ"))
async def start_order(message: Message):
    # await message.delete() если написать данную строку то удаляется смс который вводил user
    await message.answer("Выберите категорию: ",
                         reply_markup=generate_categories_menu())


@dp.message_handler(lambda message: message.text in CategoryTools.CATEGORIES)
async def show_products_menu(message: Message):
    category_name = message.text
    await message.answer("Выберите продукт:",
                         reply_markup=generate_products_menu(category_name))


@dp.message_handler(lambda message: message.text in ProductTools.PRODUCTS)
async def show_detail_product(message: Message):
    product_name = message.text
    pk, title, price, image, units_in_store, units, expire, ingredients = ProductTools().get_product_detail(
        product_name)
    caption = f"Названия продукта: {title}\n\n" \
              f"Стоимость: {price} сум\n" \
              f"Кол-во на складе: {units_in_store} {units}\n" \
              f"Срок годности: {expire}\n\n" \
              f"Ингридиенты: {ingredients}"
    with open(image, mode="rb") as photo:
        await message.answer_photo(photo, caption=caption,
                                   reply_markup=generate_product_detail_menu(pk))


@dp.callback_query_handler(lambda call: call.data.startswith("change-qty"))
async def change_qty_product(call: CallbackQuery):
    _, action, product_id, current_qty = call.data.split("_")
    product_id, current_qty = int(product_id), int(current_qty)
    product_name = ProductTools().get_product_name(product_id)
    pk, title, price, image, units_in_store, units, expire, ingredients = ProductTools().get_product_detail(
        product_name)

    if action == "minus":
        if current_qty > 0:
            current_qty -= 1
        else:
            await call.answer("Нельзя заказать меньше нуля !")
            return
    elif action == "plus":
        if current_qty < units_in_store:
            current_qty += 1
        else:
            await call.answer("Достигнут лимит продуктов !")
            return
    elif action == "current":
        await call.answer("Текущее выбранное кол-во")
        return
    message = call.message
    caption = f"Названия продукта: {title}\n\n" \
              f"Стоимость: {price} сум\n" \
              f"Кол-во на складе: {units_in_store - current_qty} {units}\n" \
              f"Срок годности: {expire}\n\n" \
              f"Ингридиенты: {ingredients}"
    await message.edit_caption(caption=caption, reply_markup=generate_product_detail_menu(product_id, current_qty))


@dp.message_handler(Text(equals="◀ Вернуться в главное меню"))
async def back_to_main_menu(message: Message):
    await start(message)


@dp.message_handler(Text(equals="◀ Вернуться к списку категорий"))
async def back_to_categories_menu(message: Message):
    await start_order(message)
