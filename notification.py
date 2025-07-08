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
from typing import AsyncIterator

from functions import get_google_sheet_notification


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


async def check_for_status_updates(bot: Bot, pool, sheet_id: str):
    """
    Сравнивает текущие статусы в Google Sheets с базой данных.
    """
    try:
        leads = await get_google_sheet_notification(sheet_id, 3)
        
        async with pool.acquire() as conn:
            async with conn.transaction():  # Транзакция для атомарности
                for lead in leads:
                    raw_referral_id = str(lead["id Реферала"])
                    referral_id = f"+{raw_referral_id}"
                    current_status = str(lead["Статус"])
                    
                    # Получаем данные из БД
                    row = await conn.fetchrow(
                        """SELECT last_status, partner_tg_id 
                        FROM lead_status_updates 
                        WHERE referral_id = $1 AND sheet_id = $2""",
                        referral_id, sheet_id
                    )
                    
                    if row and row['last_status'] != current_status:
                        try:
                            await bot.send_message(
                                row['partner_tg_id'],
                                f"🔔 Изменение статуса!\n"
                                f"ID: {referral_id}\n"
                                f"Было: {row['last_status']}\n"
                                f"Стало: {current_status}"
                            )
                            
                            await conn.execute(
                                """UPDATE lead_status_updates 
                                SET last_status = $1
                                WHERE referral_id = $2 AND sheet_id = $3""",
                                current_status, referral_id, sheet_id
                            )
                        except Exception as e:
                            print(f"Ошибка при отправке уведомления: {e}")
                            
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")
        raise


async def get_async_connection() -> AsyncIterator[asyncpg.Pool]:
    """Создает и возвращает пул подключений к PostgreSQL."""
    try:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            min_size=1,
            max_size=10,
            timeout=30  # Таймаут подключения в секундах
        )
        print("✅ Подключение к PostgreSQL установлено")
        return pool
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        raise

async def periodic_check(bot: Bot, pool, interval: int = 60):
    """Периодическая проверка обновлений."""
    while True:
        try:
            async with pool.acquire() as conn:  # Получаем соединение из пула
                # Получаем список всех отслеживаемых таблиц
                sheets = await conn.fetch("SELECT sheet_id FROM tracked_sheets")
                
                for sheet in sheets:
                    sheet_id = sheet['sheet_id']
                    await check_for_status_updates(bot, pool, sheet_id)
                    print(f"Проверяю {sheet_id}")
                    
        except Exception as e:
            print(f"❌ Ошибка в periodic_check: {e}")
            
        await asyncio.sleep(interval)