
import sqlite3
from config import DB_NAME


def connect_database(db_path: str = DB_NAME):
    connection_ = sqlite3.connect(db_path)
    cursor_ = connection_.cursor()
    return connection_, cursor_