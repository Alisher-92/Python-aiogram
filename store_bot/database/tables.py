from database import connect_database
from config import DB_NAME


class InitDB:
    def __init__(self):
        self.connection, self.cursor = connect_database(f"../{DB_NAME}")
        self.PRODUCT_UNITS = ["шт", "кг", "г"]

    def __create_users_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(100) NOT NULL,
            chat_id INTEGER NOT NULL UNIQUE,
            rating INTEGER DEFAULT 0
        )""")

    def __create_categories_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(15) NOT NULL UNIQUE
        )""")

    def __create_products_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER REFERENCES categories(id),
            title VARCHAR(15) NOT NULL UNIQUE,
            price DECIMAL(9, 2) NOT NULL,
            image VARCHAR(255) NOT NULL,
            units_in_store INTEGER NOT NULL,
            units VARCHAR(3) DEFAULT "шт.",
            expire VARCHAR(12) NOT NULL,
            ingredients VARCHAR(255) DEFAULT "Ингридиенты не указаны"
        )""")

    def __create_carts_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS carts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            total_price DECIMAL(12, 2) DEFAULT 0,
            in_order BOOL DEFAULT 0
        )""")

    def __create_cart_products_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS cart_products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(id),
            product_id INTEGER REFERENCES products(id),
            product_name VARCHAR(15) NOT NULL,
            quantity INTEGER NOT NULL,
            units VARCHAR(5) NOT NULL,
            total_price DECIMAL(9, 2) NOT NULL,
            
            UNIQUE (cart_id, product_id)
        )""")

    def __create_reviews_cart(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            full_name VARCHAR(50) NOT NULL,
            phone_number VARCHAR(15) NOT NULL,
            review TEXT NOT NULL,
            create_datetime VARCHAR(16) NOT NULL    
        )""")

    def init_db(self):
        self.__create_users_table()
        self.__create_categories_table()
        self.__create_products_table()
        self.__create_carts_table()
        self.__create_cart_products_table()
        self.__create_reviews_cart()

        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    InitDB().init_db()
