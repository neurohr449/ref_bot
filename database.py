import os
import psycopg2
from psycopg2 import sql

# Данные для подключения к БД (берутся из переменных окружения)
DB_HOST = os.getenv("DB_HOST")          # Хост Railway (например, "monorail.proxy.rlwy.net")
DB_PORT = os.getenv("DB_PORT")          # Порт (например, "5432")
DB_NAME = os.getenv("DB_NAME")          # Название БД (обычно "railway")
DB_USER = os.getenv("DB_USER")          # Пользователь (обычно "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # Пароль из Railway

def get_connection():
    """Создает и возвращает подключение к PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Успешное подключение к БД!")
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        raise

async def save_user_data(state_data: dict):
    """
    Сохраняет данные пользователя в таблицу `user_data`.
    Если запись с таким `tg_id` уже существует — обновляет её.
    
    :param state_data: Словарь с данными из FSM (ключами должны быть поля таблицы).
    """
    # SQL-запрос для вставки или обновления данных
    query = sql.SQL("""
        INSERT INTO user_data (
            tg_id, first_name, last_name, phone_number, 
            card_number, bank_info, sbp_info, bank_fio, 
            sheet_id, sheet_range
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tg_id) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            phone_number = EXCLUDED.phone_number,
            card_number = EXCLUDED.card_number,
            bank_info = EXCLUDED.bank_info,
            sbp_info = EXCLUDED.sbp_info,
            bank_fio = EXCLUDED.bank_fio,
            sheet_id = EXCLUDED.sheet_id,
            sheet_range = EXCLUDED.sheet_range
    """)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Подставляем значения из state_data в запрос
                cursor.execute(query, (
                    state_data.get("tg_id"),          # Обязательное поле
                    state_data.get("first_name"),
                    state_data.get("last_name"),
                    state_data.get("phone_number"),
                    state_data.get("card_number"),
                    state_data.get("bank_info"),
                    state_data.get("sbp_info"),
                    state_data.get("bank_fio"),
                    state_data.get("sheet_id"),
                    state_data.get("sheet_range")
                ))
                conn.commit()
                print("Данные успешно сохранены в БД!")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        raise