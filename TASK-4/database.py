import pymysql


DB_NAME = "inventory_db"


def ensure_database():
    conn = pymysql.connect(
        host="localhost", user="root", password="Sql@3117", autocommit=True
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.close()


def get_connection():
    ensure_database()
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Sql@3117",
        database=DB_NAME,
        autocommit=True,
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
		CREATE TABLE IF NOT EXISTS products(
			id INT AUTO_INCREMENT PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			price DECIMAL(10,2) NOT NULL,
			stock INT NOT NULL
		)
		"""
    )
    cursor.execute(
        """
		CREATE TABLE IF NOT EXISTS bills(
			id INT AUTO_INCREMENT PRIMARY KEY,
			bill_date DATE NOT NULL,
			total_amount DECIMAL(10,2) NOT NULL
		)
		"""
    )
    cursor.execute(
        """
		CREATE TABLE IF NOT EXISTS bill_items(
			id INT AUTO_INCREMENT PRIMARY KEY,
			bill_id INT NOT NULL,
			product_id INT NOT NULL,
			quantity INT NOT NULL,
			FOREIGN KEY (bill_id) REFERENCES bills(id),
			FOREIGN KEY (product_id) REFERENCES products(id)
		)
		"""
    )
    conn.close()


def fetch_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_product(name, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
        (name, price, stock),
    )
    conn.close()


def update_stock(product_id, new_stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id)
    )
    conn.close()


def create_bill(bill_date, total_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bills (bill_date, total_amount) VALUES (%s, %s)",
        (bill_date, total_amount),
    )
    bill_id = cursor.lastrowid
    conn.close()
    return bill_id


def add_bill_item(bill_id, product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bill_items (bill_id, product_id, quantity) VALUES (%s, %s, %s)",
        (bill_id, product_id, quantity),
    )
    conn.close()


def daily_sales_summary(bill_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM bills WHERE bill_date = %s",
        (bill_date,),
    )
    summary = cursor.fetchone()
    conn.close()
    return summary
