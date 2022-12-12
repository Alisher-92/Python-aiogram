from database import connect_database


class _BaseTools:  # данный класс не стоит импортировать
    def __init__(self):
        self.connection, self.cursor = connect_database()

    def reconnect(self):
        """Переподключения к БД"""
        self.__init__()


class UserTools(_BaseTools):
    def register_user(self, full_name: str, chat_id: int) -> None:
        """Регистрация пользователя"""
        try:
            self.cursor.execute("""INSERT INTO users (full_name, chat_id)
                VALUES (?, ?)
            """, (full_name, chat_id))
        except:
            pass
        else:
            self.connection.commit()
        finally:
            self.connection.close()

    def get_user_id(self, chat_id: int) -> int:
        """Получить user_id пользователя"""
        self.cursor.execute("""SELECT id
            FROM users
            WHERE chat_id = ?
        """, (chat_id,))
        user_id = self.cursor.fetchone()[0]
        self.connection.close()
        return user_id

    def get_active_cart(self, user_id: int) -> tuple[int, int, float]:
        """Получить активную корзину пользователя
        id, user_id, total_price"""
        self.cursor.execute("""SELECT id, user_id, total_price
            FROM carts
            WHERE user_id = ? AND in_order = 0
        """, (user_id,))
        cart = self.cursor.fetchone()
        self.connection.close()
        return cart

    def register_cart(self, user_id: int) -> None:
        """Регистрация корзины для пользователя, но только в том случае если у него нет активной корзины"""
        # LYSB - Не глядя броду не лезь в воду
        if not self.get_active_cart(user_id):
            self.reconnect()
            self.cursor.execute("""INSERT INTO carts (user_id)
                VALUES (?)
            """, (user_id,))
            self.connection.commit()
            self.connection.close()

    def recalc_cart(self, cart_id: int) -> None:
        self.cursor.execute("""UPDATE carts
            SET total_price = (
                SELECT SUM(total_price)
                FROM cart_products
                WHERE cart_id = :cart_id
            )
            WHERE id = :cart_id
        """, {"cart_id": cart_id})
        self.connection.commit()
        self.connection.close()


class CategoryTools(_BaseTools):
    CATEGORIES = []  # атрибут на уровне класса

    def get_category_names(self) -> list:
        """Список имён категорий"""
        self.cursor.execute("""SELECT name
            FROM categories
        """)
        CategoryTools.CATEGORIES = [
            category[0]
            for category in self.cursor.fetchall()
        ]

        self.connection.close()
        return CategoryTools.CATEGORIES


class ProductTools(_BaseTools):
    PRODUCTS = []

    def get_product_name(self, product_id: int) -> str:
        """Получает на вход product_id, возвращает product_name"""
        self.cursor.execute("""SELECT title
            FROM products
            WHERE id = ?
        """, (product_id,))
        product_name, = self.cursor.fetchone()
        self.connection.close()
        return product_name

    def get_product_names(self, category_name: str) -> list:
        self.cursor.execute("""SELECT title
            FROM products
            WHERE category_id = (
                SELECT id
                FROM categories
                WHERE name = ?
            )
        """, (category_name,))
        ProductTools.PRODUCTS = [
            product[0]
            for product in self.cursor.fetchall()
        ]
        self.connection.close()
        return ProductTools.PRODUCTS

    def get_product_detail(self, product_name: str) -> tuple:
        """Получить детально продукт: id, title, price, image,
            units_in_store, units, expire, ingredients"""
        self.cursor.execute("""SELECT id, title, price, image,
            units_in_store, units, expire, ingredients
            FROM products
            WHERE title = ?
        """, (product_name,))
        product = self.cursor.fetchone()
        self.connection.close()
        return product

    def get_units_in_store(self, product_name: str) -> int:
        try:
            units_in_store = self.get_product_detail(product_name)[4]
            return units_in_store
        except:
            return 0


class CartProductTools(_BaseTools):
    def get_cart_products(self, cart_id: int) -> list:
        """Получаем список продуктов из корзины:
        product_id, product_name, quantity, units, total_price"""
        self.cursor.execute("""SELECT product_id, product_name, quantity, units, total_price
            FROM cart_products
            WHERE cart_id = ?
        """, (cart_id,))
        cart_products = self.cursor.fetchall()
        self.connection.close()
        return cart_products

    def add_cart_product(self, cart_id: int, product_id: int, product_name: str,
                         qty: int, units: str, total_price: float) -> bool:
        status_add = False
        try:
            # Добавления продукта в корзину
            self.cursor.execute("""INSERT INTO cart_products (cart_id, product_id, product_name,
                            quantity, units, total_price)
                            VALUES (?, ?, ?, ?, ?, ?)
                         """, (cart_id, product_id, product_name, qty, units, total_price))
        except:
            self.edit_cart_product(cart_id, product_id, qty, total_price)
        else:
            status_add = True
            self.connection.commit()
        finally:
            self.connection.close()
        return status_add

    def edit_cart_product(self, cart_id: int, product_id: int, qty: int, total_price: float):
        self.cursor.execute("""UPDATE cart_products
            SET quantity = ?, total_price = ?
            WHERE cart_id = ? AND product_id = ?
        """, (qty, total_price, cart_id, product_id))
        self.connection.commit()
        self.connection.close()

    def delete_cart_product(self, cart_id: int, product_id: int) -> None:
        self.cursor.execute("""DELETE FROM cart_products
            WHERE cart_id = ? AND product_id = ?
        """, (cart_id, product_id))
        self.connection.commit()
        self.connection.close()


class ReviewTools(_BaseTools):
    def add_review(self, user_id: int, full_name: str,
                   phone_number: str, review: str, create_datetime: str):
        self.cursor.execute("""INSERT INTO reviews (user_id, full_name,
         phone_number, review, create_datetime) VALUES (?, ?, ?, ?, ?)""",
                            (user_id, full_name, phone_number, review, create_datetime))
        self.connection.commit()
        self.connection.close()
