import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # your MySQL username
        password="divyanshu123@4",  # your MySQL password
        database="task_manager_db"
    )
