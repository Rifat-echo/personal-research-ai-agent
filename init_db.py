
import sqlite3
from pathlib import Path

# Store the database beside this Python file.
DB_PATH = Path(__file__).with_name("business.db")


def initialize_database():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total_gbp REAL NOT NULL
            )
        """)

        sample_orders = [
            (
                "ORD-1042",
                "Shipped",
                "Northstar Office Ltd",
                "Monitor",
                12,
                2088.00,
            ),
            (
                "ORD-1043",
                "Processing",
                "Brightway Consulting",
                "Keyboard",
                5,
                175.00,
            ),
        ]

        connection.executemany("""
            INSERT OR IGNORE INTO orders
            (order_id, status, customer, product, quantity, total_gbp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_orders)

    print(f"Database initialized: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()
