from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def generate_locations_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton(text="📍  Отправить свою локацию", request_location=True)
    )
    return markup


def generate_comment_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton(text="Нет комментариев")
    )
    return markup


def generate_accept_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton(text="✍  Изменить ФИО")
    )
    markup.row(
        KeyboardButton(text="✍  Изменить номер телефона")
    )
    markup.row(
        KeyboardButton(text="✍  Изменить адрес")
    )
    markup.row(
        KeyboardButton(text="✍  Изменить комментарий")
    )
    markup.row(
        KeyboardButton(text="❌  Отменить заказ"),
        KeyboardButton(text="✅  Подтвердить")
    )
    return markup


def generate_phone_number():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton(text="📱  Отправить свой номер телефона", request_contact=True)
    )
    return markup
