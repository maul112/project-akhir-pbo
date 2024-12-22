import sqlite3

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = sqlite3.connect("budget.db")
            cls._instance._create_table()
        return cls._instance

    def _create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL
        )
        """
        self._connection.cursor().execute(query)
        self._connection.commit()

    def get_connection(self):
        return self._connection
