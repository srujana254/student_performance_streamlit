import pymysql

conn = pymysql.connect(host="localhost", user="root", password="Sql@3117")
cursor = conn.cursor()
cursor.execute("Create database if not exists task_db")
conn.commit()
conn.close()
conn = pymysql.connect(
    host="localhost", user="root", password="Sql@3117", database="task_db"
)
cursor = conn.cursor()

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no INT NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    class VARCHAR(50) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL DEFAULT 'Absent',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
)
""")

# Create marks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    marks INT NOT NULL CHECK (marks >= 0 AND marks <= 100),
    pass_marks INT DEFAULT 40,
    status ENUM('Pass', 'Fail') GENERATED ALWAYS AS (IF(marks >= pass_marks, 'Pass', 'Fail')) STORED,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_marks (student_id, subject)
)
""")

conn.commit()
print("Tables created successfully!")
print("\nTable Structure:")
print("1. students - Stores student information")
print("2. attendance - Tracks daily attendance (Present/Absent)")
print("3. marks - Stores subject-wise marks with pass/fail status")
conn.close()
