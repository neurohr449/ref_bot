import psycopg2
from psycopg2 import sql, errors
import asyncpg
from aiogram import Bot, types
import gspread
from google.oauth2.service_account import Credentials
import os
import asyncio
from aiogram import Bot, Dispatcher, html, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest


from functions import get_google_sheet_data
from main import get_chat_id

DB_HOST = os.getenv("DB_HOST")          
DB_PORT = os.getenv("DB_PORT")          
DB_NAME = os.getenv("DB_NAME")          
DB_USER = os.getenv("DB_USER")          
DB_PASSWORD = os.getenv("DB_PASSWORD")  

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))

async def get_chat_id(user_id: int):
    try:
        chat = await bot.get_chat(user_id)  # Получаем чат по user_id
        return chat.id
    except TelegramBadRequest:
        print("Бот не знает этого пользователя или чата!")
        return None

async def add_lead_to_db(conn, referral_id: str, partner_tg_id: str, status: str, sheet_id: str, sheet_name: str = None):
    """
    Добавляет новый лид в базу данных и автоматически регистрирует таблицу, если её нет.
    """
    try:
        with conn.cursor() as cursor:
            # 1. Проверяем/добавляем таблицу
            cursor.execute(
                "INSERT INTO tracked_sheets (sheet_id, sheet_name) VALUES (%s, %s) ON CONFLICT (sheet_id) DO NOTHING",
                (sheet_id, sheet_name or "Без названия")
            )
            
            # 2. Добавляем/обновляем лид
            cursor.execute(
                """
                INSERT INTO lead_status_updates 
                    (referral_id, partner_tg_id, last_status, sheet_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (referral_id, sheet_id) 
                DO UPDATE SET last_status = EXCLUDED.last_status
                """,
                (referral_id, partner_tg_id, status, sheet_id)
            )
            conn.commit()
            
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении лида: {e}")


async def check_for_status_updates(bot: Bot, conn, sheet_id: str):
    """
    Сравнивает текущие статусы в Google Sheets с базой данных и отправляет уведомления об изменениях.
    """
    try:
        # 1. Получаем актуальные данные из Google Sheets
        leads = get_google_sheet_data(sheet_id, 3)  # Ваша функция для чтения таблицы
        
        # 2. Для каждой строки в таблице проверяем расхождения с БД
        with conn.cursor() as cursor:
            for lead in leads:
                referral_id = str(lead["id Реферала"])
                current_status = str(lead["Статус"])
                
                # 3. Получаем последний сохранённый статус из БД
                cursor.execute(
                    """
                    SELECT last_status, partner_tg_id 
                    FROM lead_status_updates 
                    WHERE referral_id = %s AND sheet_id = %s
                    """,
                    (referral_id, sheet_id)
                )
                result = cursor.fetchone()
                
                # 4. Если статус изменился - отправляем уведомление
                if result:
                    stored_status, partner_tg_id = result
                    if stored_status != current_status:
                        # Отправляем уведомление
                        chat_id = await get_chat_id(partner_tg_id)
                        await bot.send_message(
                            chat_id,
                            f"🔔 Изменение статуса!\n"
                            f"ID: {referral_id}\n"
                            f"Было: {stored_status}\n"
                            f"Стало: {current_status}"
                        )
                        
                        # Обновляем статус в БД
                        cursor.execute(
                            """
                            UPDATE lead_status_updates 
                            SET last_status = %s
                            WHERE referral_id = %s AND sheet_id = %s
                            """,
                            (current_status, referral_id, sheet_id)
                        )
                        conn.commit()
                        
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")


async def get_async_connection():
    """Асинхронное подключение к PostgreSQL."""
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        min_size=1,
        max_size=10
    )

async def periodic_check(bot: Bot, pool, interval: int = 60):
    """Проверяет изменения каждые `interval` секунд."""
    while True:
        try:
            async with pool.acquire() as conn:  # Берём соединение из пула
                # Получаем список всех таблиц
                sheets = await conn.fetch("SELECT sheet_id FROM tracked_sheets")
                for sheet in sheets:
                    await check_for_status_updates(bot, conn, sheet['sheet_id'])
                    
            print(f"✅ Проверка завершена. Ждем {interval} сек...")
            
        except Exception as e:
            print(f"❌ Ошибка в periodic_check: {e}")
            
        await asyncio.sleep(interval)  # Неблокирующее ожидание