import sqlite3
from datetime import date
import pandas as pd


def db_create():
    conn = sqlite3.connect('wydatki.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transakcje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa TEXT,
            kwota REAL,
            data TEXT,
            kategoria TEXT
        );
    ''')
    conn.commit()
    conn.close()

def db_connect():
    conn = sqlite3.connect('wydatki.db')
    return conn

def insert_data(nazwa: str, kwota, data, kategoria: str):
    if not nazwa:
        nazwa = '???'
    if kwota == '0' or kwota is None:
        print('Brak kwoty')
        return

    try:
        kwota = float(kwota)  # konwersja jeśli np. ktoś podał stringa "123.45"
    except ValueError:
        print("Nieprawidłowa kwota")
        return

    conn = db_connect()
    cursor = conn.cursor()

    sql = "INSERT INTO transakcje (nazwa, kwota, data, kategoria) VALUES (?, ?, ?, ?)"
    values = (nazwa, kwota, data, kategoria)

    try:
        cursor.execute(sql, values)
        conn.commit()
        print("Dane zostały pomyślnie dodane.")
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        cursor.close()
        conn.close()

def show_data():
    try:
        conn = db_connect()
        cursor = conn.cursor()
        sql = "SELECT * from transakcje"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except:
            print(f"Błąd:")
        finally:
            cursor.close()
            conn.close()
        return results
    except:
        print('nie udało się połączyć z bazą danych')
        return

def delete_transaction(transaction_id: int):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        q = "DELETE FROM transakcje WHERE id = ?"
        cursor.execute(q,(transaction_id,))
        conn.commit()
        print(f"Transakcja o ID {transaction_id} została usunięta")
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        cursor.close()
        conn.close()
