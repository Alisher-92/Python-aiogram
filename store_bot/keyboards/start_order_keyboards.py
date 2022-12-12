from aiogram.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.tools import CategoryTools, ProductTools


def generate_categories_menu():
    categories = CategoryTools().get_category_names()
    if categories:
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(*categories)
        markup.row(
            KeyboardButton(text="◀ Вернуться в главное меню")
        )
        return markup
    else:
        markup = ReplyKeyboardRemove()
        return markup


def generate_products_menu(category_name: str):
    products = ProductTools().get_product_names(category_name)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if products:
        markup.add(*products)
    markup.row(
        KeyboardButton(text="◀ Вернуться к списку категорий")
    )
    return markup


def generate_product_detail_menu(product_id: int, current_qty: int = 0):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text="-", callback_data=f"change-qty_minus_{product_id}_{current_qty}"),
        InlineKeyboardButton(text=str(current_qty), callback_data=f"change-qty_current_{product_id}_{current_qty}"),
        InlineKeyboardButton(text="+", callback_data=f"change-qty_plus_{product_id}_{current_qty}")
    )
    markup.row(
        InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add-cart_{product_id}_{current_qty}")
    )
    return markup
