import pymysql

conn=pymysql.connect(
  host="localhost",
  user="root",
  password="Sql@3117",
  database="student_db"
)
cursor=conn.cursor()
cursor.execute("Create table if not exists student(id int AUTO_INCREMENT primary key, name varchar(20),age int,subject varchar(20),marks int)")
conn.commit()