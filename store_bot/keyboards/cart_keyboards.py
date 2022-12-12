from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def generate_delete_cart_products(cart_product_info: list, cart_id: int):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="🚀  Оформить заказ", callback_data=f"make-order_{cart_id}"))
    for name, pk in cart_product_info:
        markup.row(
            InlineKeyboardButton(text=name, callback_data=f"delete-cart_{cart_id}_{pk}")
        )
    return markup
