import mysql.connector
from datetime import date


def db_connect():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wydatki"
    )
    return conn

def insert_data(nazwa: str, kwota: int, data, kategoria: str):

    if nazwa == '':
        nazwa = '???'
    if kwota == '':
        print('brak kwoty')
        return

    conn = db_connect()
    cursor = conn.cursor()

    sql = "INSERT INTO transakcje (nazwa, kwota, data, kategoria) VALUES (%s, %s, %s, %s)"
    values = (nazwa, kwota, data, kategoria)

    try:
        cursor.execute(sql, values)
        conn.commit()
        print("Dane zostały pomyślnie dodane.")
    except mysql.connector.Error as e:
        print(f"Błąd: {e}")
    finally:
        cursor.close()
        conn.close()

def show_data():
    conn = db_connect()
    cursor = conn.cursor()
    sql = "SELECT * from transakcje"

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Błąd: {e}")
    finally:
        cursor.close()
        conn.close()
    return results
