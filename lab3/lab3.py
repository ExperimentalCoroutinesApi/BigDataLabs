# Веселов С.С.
import psycopg2
import random
import matplotlib.pyplot as plt
import os
import sys
import locale


class ConnectDB:
    """Класс для работы с базой данных PostgreSQL.

    Позволяет подключаться к базе данных, выполнять SQL-запросы (SELECT, INSERT, UPDATE, DELETE)
    и закрывать соединение.

    Attributes:
        conn (psycopg2.extensions.connection): Объект соединения с базой данных.
        cur (psycopg2.extensions.cursor): Курсор для выполнения SQL-запросов.
    """

    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        """Инициализирует подключение к базе данных.

        Args:
            dbname (str): Имя базы данных.
            user (str): Имя пользователя базы данных.
            password (str): Пароль пользователя базы данных.
            host (str, optional): Хост базы данных. По умолчанию "localhost".
            port (str, optional): Порт базы данных. По умолчанию "5432".
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()
        print("Подключение к базе данных установлено.")

    def select(self, query, params=None):
        """Выполняет SQL-запрос на выборку данных (SELECT).

        Args:
            query (str): SQL-запрос.
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None.

        Returns:
            list: Список кортежей с результатами запроса.
        """
        self.cur.execute(query, params or ())
        return self.cur.fetchall()

    def insert(self, query, params=None):
        """Выполняет SQL-запрос на вставку данных (INSERT).

        Args:
            query (str): SQL-запрос.
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None.
        """
        self.cur.execute(query, params or ())
        self.conn.commit()
        print("Данные успешно вставлены.")

    def update(self, query, params=None):
        """Выполняет SQL-запрос на обновление данных (UPDATE).

        Args:
            query (str): SQL-запрос.
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None.
        """
        self.cur.execute(query, params or ())
        self.conn.commit()
        print("Данные успешно обновлены.")

    def delete(self, query, params=None):
        """Выполняет SQL-запрос на удаление данных (DELETE).

        Args:
            query (str): SQL-запрос.
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None.
        """
        self.cur.execute(query, params or ())
        self.conn.commit()
        print("Данные успешно удалены.")

    def close(self):
        """Закрывает соединение с базой данных."""
        self.cur.close()
        self.conn.close()
        print("Соединение с базой данных закрыто.")


def main():
    # Подключение к базе данных
    db = ConnectDB(dbname="rggu", user="test", password=":)")

    # ========================== Задания предыдущего урока ==========================
    try:
        # 1. Создать таблицу `flights`
        db.cur.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                id SERIAL PRIMARY KEY,
                flight_number VARCHAR(50) NOT NULL,
                airline VARCHAR(100) NOT NULL,
                departure_time TIMESTAMP,
                arrival_time TIMESTAMP,
                destination VARCHAR(100)
            )
        """)
        db.conn.commit()

        # Заполнить таблицу 10 записями
        airlines = ["АЭРОФЛОТ", "S7", "Победа", "Уральские авиалинии"]
        destinations = ["Москва", "Санкт-Петербург",
                        "Новосибирск", "Екатеринбург", "Сочи"]

        for i in range(10):
            flight_number = f"SU{i+1:03d}"
            airline = random.choice(airlines)
            departure_time = f"2023-10-{random.randint(1, 30)} {random.randint(0, 23)}:{random.randint(0, 59)}:00"
            arrival_time = f"2023-10-{random.randint(1, 30)} {random.randint(0, 23)}:{random.randint(0, 59)}:00"
            destination = random.choice(destinations)

            db.insert("""
                INSERT INTO flights (flight_number, airline, departure_time, arrival_time, destination)
                VALUES (%s, %s, %s, %s, %s)
            """, (flight_number, airline, departure_time, arrival_time, destination))

        # 2. Вывести все самолеты, принадлежащие компании "АЭРОФЛОТ"
        print("Самолеты компании АЭРОФЛОТ:")
        aeroflot_flights = db.select(
            "SELECT * FROM flights WHERE airline = 'АЭРОФЛОТ'")
        for flight in aeroflot_flights:
            print(flight)

        # 3. Вывести все самолеты, не принадлежащие компании "АЭРОФЛОТ"
        print("Самолеты, не принадлежащие компании АЭРОФЛОТ:")
        non_aeroflot_flights = db.select(
            "SELECT * FROM flights WHERE airline != 'АЭРОФЛОТ'")
        for flight in non_aeroflot_flights:
            print(flight)

        # 7. Изменить данные для всех самолетов, принадлежащих компании "АЭРОФЛОТ", на "АЭРОФЛОТ 2"
        db.update(
            "UPDATE flights SET airline = 'АЭРОФЛОТ 2' WHERE airline = 'АЭРОФЛОТ'")
        print("Данные обновлены: 'АЭРОФЛОТ' -> 'АЭРОФЛОТ 2'\n")
        print(db.select("SELECT * FROM flights"))

        # 8. Удалить все данные о компании "S7"
        db.delete("DELETE FROM flights WHERE airline = 'S7'")
        print("Все данные о компании S7 удалены.\n")
        print(db.select("SELECT * FROM flights"))

    finally:
        # Закрытие соединения с базой данных
        db.close()

    # ========================== Задание текущего урока ==========================

    # Подключение к базе данных
    db = ConnectDB(dbname="rggu", user="test", password=":)")

    db.cur.execute("""
        CREATE TABLE IF NOT EXISTS coordinates (
            x INTEGER,
            y INTEGER
        )
    """)
    db.conn.commit()

    # Заполнение таблицы сгенерированными данными (30 записей)
    for _ in range(30):
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        db.insert("INSERT INTO coordinates (x, y) VALUES (%s, %s)", (x, y))

    # Получение данных из таблицы
    data = db.select("SELECT x, y FROM coordinates;")
    print("Данные из таблицы coordinates:", data)

    # Удаление таблицы coordinates
    db.cur.execute("DROP TABLE coordinates;")
    print("Таблица coordinates удалена.")

    # Создание списков x и y
    x_values = [row[0] for row in data]
    y_values = [row[1] for row in data]

    # Построение графика
    plt.scatter(x_values, y_values)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Типа график)')
    plt.show()

    # Закрытие соединения с базой данных
    db.close()


if __name__ == "__main__":
    main()
