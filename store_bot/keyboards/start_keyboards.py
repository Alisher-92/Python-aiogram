from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def generate_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton(text="✅ Начать заказ")
    )
    markup.row(
        KeyboardButton(text="🛒 Корзинка"),
        KeyboardButton(text="✍ Оставить отзыв")
    )
    return markup
