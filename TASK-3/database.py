import pymysql

conn = pymysql.connect(host="localhost", user="root", password="Sql@3117")
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS complaint_db")
conn.commit()
conn.close()
conn = pymysql.connect(
    host="localhost", user="root", password="Sql@3117", database="complaint_db"
)
cursor = conn.cursor()
# Create complaints table
cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Open', 'In Progress', 'Resolved', 'Closed') DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
print("Complaints table created successfully!")
conn.close()
