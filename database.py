import os
import psycopg2
from psycopg2 import sql
from aiogram.fsm.context import FSMContext

DB_HOST = os.getenv("DB_HOST")          
DB_PORT = os.getenv("DB_PORT")          
DB_NAME = os.getenv("DB_NAME")          
DB_USER = os.getenv("DB_USER")          
DB_PASSWORD = os.getenv("DB_PASSWORD")  

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
        
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        raise

async def save_user_data(state_data: dict):
    """
    Сохраняет данные пользователя в таблицу `user_data`.
    Если запись с таким `tg_id` уже существует — обновляет только не-NULL поля.
    
    :param state_data: Словарь с данными из FSM (ключами должны быть поля таблицы).
    """
    
    query = sql.SQL("""
        INSERT INTO user_data (
            tg_id, first_name, last_name, phone_number, 
            card_number, bank_info, sbp_info, bank_fio, 
            sheet_id, sheet_range
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tg_id) DO UPDATE SET
            first_name = COALESCE(EXCLUDED.first_name, user_data.first_name),
            last_name = COALESCE(EXCLUDED.last_name, user_data.last_name),
            phone_number = COALESCE(EXCLUDED.phone_number, user_data.phone_number),
            card_number = COALESCE(EXCLUDED.card_number, user_data.card_number),
            bank_info = COALESCE(EXCLUDED.bank_info, user_data.bank_info),
            sbp_info = COALESCE(EXCLUDED.sbp_info, user_data.sbp_info),
            bank_fio = COALESCE(EXCLUDED.bank_fio, user_data.bank_fio),
            sheet_id = COALESCE(EXCLUDED.sheet_id, user_data.sheet_id),
            sheet_range = COALESCE(EXCLUDED.sheet_range, user_data.sheet_range)
    """)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute(query, (
                    state_data.get("tg_id"),          
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

async def load_user_data_to_state(tg_id: int, state: FSMContext):
    """
    Загружает данные пользователя из БД и сохраняет в FSM state.
    
    :param tg_id: ID пользователя в Telegram
    :param state: Объект состояния FSM
    """
    query = """
        SELECT 
            first_name, last_name, phone_number, 
            card_number, bank_info, sbp_info, bank_fio,
            sheet_id, sheet_range
        FROM user_data
        WHERE tg_id = %s
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (tg_id,))
                result = cursor.fetchone()
                
                if result:
                    # Сопоставляем поля результата с ключами state
                    user_data = {
                        "first_name": result[0],
                        "last_name": result[1],
                        "phone_number": result[2],
                        "card_number": result[3],
                        "bank_info": result[4],
                        "sbp_info": result[5],
                        "bank_fio": result[6],
                        "sheet_id": result[7],
                        "sheet_range": result[8]
                    }
                    
                    # Очищаем текущее состояние и заполняем данными из БД
                    await state.update_data(**user_data)
                    print(f"Данные пользователя {tg_id} загружены в state")
                    return True
                else:
                    print(f"Пользователь с tg_id {tg_id} не найден в БД")
                    return False
                    
    except Exception as e:
        print(f"Ошибка при загрузке данных пользователя: {e}")
        raise