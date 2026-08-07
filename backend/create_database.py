import sqlite3


connection = sqlite3.connect(
    "sample_data/company.db"
)

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE customers(
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")


cursor.execute("""
CREATE TABLE orders(
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount FLOAT,

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)
)
""")


connection.commit()

connection.close()

print("Database created")