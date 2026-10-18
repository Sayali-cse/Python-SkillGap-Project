import mysql.connector


class Database:
    """Job: connect to MySQL and run SQL commands."""

    def __init__(self, host, user, password, name, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.name = name              # database name
        self.port = port

    def connect(self):
        return mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                       database=self.name, port=self.port)

    def run(self, sql, values=()):
        """For INSERT / CREATE. Returns the id of the new row."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    def fetch(self, sql, values=()):
        """For SELECT. Returns a list of rows (each row is a dictionary)."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, values)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def setup(self):
        """Creates the database and the 3 tables if they do not exist."""
        conn = mysql.connector.connect(host=self.host, user=self.user,
                                       password=self.password, port=self.port)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + self.name)
        cursor.close()
        conn.close()

        self.run("""CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        password VARCHAR(64) NOT NULL,
                        created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        self.run("""CREATE TABLE IF NOT EXISTS results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        overall_percent INT NOT NULL,
                        taken_on DATETIME NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id))""")
        self.run("""CREATE TABLE IF NOT EXISTS skill_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        result_id INT NOT NULL,
                        skill VARCHAR(50) NOT NULL,
                        score INT NOT NULL,
                        total INT NOT NULL,
                        level_name VARCHAR(20) NOT NULL,
                        required_name VARCHAR(20) NOT NULL,
                        gap INT NOT NULL,
                        priority VARCHAR(20) NOT NULL,
                        FOREIGN KEY (result_id) REFERENCES results(id))""")
