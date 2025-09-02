import asyncio
import logging
import sys
import os
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, html, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from functions import *
from callback_functions import *
from all_states import *
from notification import periodic_check


BOT_TOKEN = os.getenv("BOT_TOKEN")
FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  
        TimedRotatingFileHandler(
            filename=str(log_dir / 'bot.log'),  
            when='midnight',     
            interval=1,          
            backupCount=7,       
            encoding='utf-8',
            utc=False            
        )
    ]
)


logger = logging.getLogger("ref_bot")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)


class StateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        state = data['state']
        current_state = await state.get_state()
        data['current_state'] = current_state
        return await handler(event, data)
    
@router.callback_query(lambda c: c.data == 'menu')
async def menu_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent message {callback_query.data}")
    try:
        user_data = await state.get_data()
        func_id = user_data.get('func_id')
        if func_id == "3":
            text = user_data.get("lead_message")
            await callback_query.message.answer(text=text)
        else:
            await menu(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(Command("menu"))
async def command_menu(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await menu_message(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

async def on_startup(bot: Bot):
    """Обработчик запуска бота."""
    try:
        print("🔄 Запуск обработчика on_startup")
        
        pool = await get_async_connection()
        asyncio.create_task(periodic_check(bot, pool, interval=3600))
        print("🔄 Фоновая задача periodic_check запущена")
        return pool  
    except Exception as e:
        print(f"❌ Ошибка в on_startup: {e}")
        raise

@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await state.set_state(UserState.welcome)
        args = command.args

        if args:
            parts = args.rsplit('_', 2)
            sheet_id  = parts[0]
            ref_id = parts[1]    
            func_id = parts[2]
            await state.update_data(sheet_id=sheet_id,
                                ref_id=ref_id,
                                func_id=func_id)
            await get_table_data(sheet_id, 0, state)
            user_data = await state.get_data()
            text = user_data.get('welcome_message')
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="next")]
            ])
            
            await message.answer(f"{text}", reply_markup = keyboard)
        else:
            await message.answer("👋 Здравствуйте. Запустите бота по уникальной ссылке!")
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.data}"
            )
    

@router.callback_query(StateFilter(UserState.welcome))
async def reg_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await state.update_data(
            survey_started=datetime.now(),
            survey_completed=False
        )
        user_data = await state.get_data()
        for i in range(1, 6):
            if user_data.get(f"survey{i}") and user_data.get(f"survey_target{i}") == "Этап регистрации":
                asyncio.create_task(check_survey_completion(callback_query.message.chat.id, state, i))
        await reg_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(StateFilter(UserState.reg_1))
async def reg_2_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await reg_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.reg_2))
async def reg_3_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await reg_3(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.reg_3))
async def reg_4_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await reg_4(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )
@router.callback_query(StateFilter(UserState.reg_4_1))
async def reg_4_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent message {callback_query.data}")
    try:
        await reg_4_1(callback_query, state)  
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

######################################################################################################################################################################################################################################################
@router.callback_query(StateFilter(UserState.reg_4))
async def course_1_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await state.update_data(
            survey_started=datetime.now(),
            survey_completed_2=False
        )
        user_data = await state.get_data()
        for i in range(1, 6):
            if user_data.get(f"survey{i}") and user_data.get(f"survey_target{i}") == "Этап обучения":
                asyncio.create_task(check_survey_completion_2(callback_query.message.chat.id, state, i))
        await course_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_1))
async def course_2_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_2))
async def course_3_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_3(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_3))
async def course_4_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_4(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_4))
async def course_5_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_5(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_5))
async def course_6_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_6(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_6))
async def course_7_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_7(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_7))
async def course_8_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_8(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_8))
async def course_9_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_9(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_9))
async def course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await course_10(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.course_10))
async def course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await end_course_handler(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

######################################################################################################################################################################################################################################################
#########
@router.callback_query(StateFilter(UserState.menu_course_1))
async def menu_course_2_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_2))
async def menu_course_3_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_3(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_3))
async def menu_course_4_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_4(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_4))
async def menu_course_5_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_5(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_5))
async def menu_course_6_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_6(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_6))
async def menu_course_7_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_7(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_7))
async def menu_course_8_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_8(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_8))
async def menu_course_9_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_9(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_9))
async def menu_course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:    
        await menu_course_10(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.menu_course_10))
async def menu_course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_end_course_handler(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )
######################################################################################################################################################################################################################################################
#########
@router.callback_query(lambda c: c.data == 'menu_1')
async def send_client_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await send_client_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.send_client_1))
async def send_client_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await send_client_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(StateFilter(UserState.send_client_2))
async def send_client_3_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await send_client_3(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )
    
@router.message(StateFilter(UserState.send_client_3))
async def send_client_4_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await send_client_4(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.callback_query(StateFilter(UserState.send_client_4))
async def send_client_5_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        if callback_query.data == "confurm":
            await send_client_5(callback_query, state)
        elif callback_query.data == "edit":
            await send_client_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

###########
@router.callback_query(lambda c: c.data == 'menu_2')
async def client_status_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await client_status_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.client_status_1))
async def client_status_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await client_status_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

############
@router.callback_query(lambda c: c.data == 'menu_3')
async def ref_link_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await ref_link_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

############
@router.callback_query(lambda c: c.data == 'menu_4')
async def bank_info_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await bank_info_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.bank_info_change))
async def bank_info_change_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        if callback_query.data == "card_number":
            await bank_info_change_card_number(callback_query, state)
        elif callback_query.data == "bank":
            await bank_info_change_bank(callback_query, state)
        elif callback_query.data == "sbp":
            await bank_info_change_sbp(callback_query, state)
        elif callback_query.data == "fio":
            await bank_info_change_fio(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(StateFilter(UserState.bank_info_change_card_number))
async def bank_info_change_card_number_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await bank_info_change_card_number_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_change_bank))
async def bank_info_change_bank_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await bank_info_change_bank_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_change_sbp))
async def bank_info_change_sbp_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await bank_info_change_sbp_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_change_fio))
async def bank_info_change_fio_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await bank_info_change_fio_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_1))
async def full_bank_info_1_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await full_bank_info_2(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_2))
async def full_bank_info_2_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await full_bank_info_3(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.message(StateFilter(UserState.bank_info_3))
async def full_bank_info_3_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await full_bank_info_4(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )
    
@router.message(StateFilter(UserState.bank_info_4))
async def full_bank_info_4_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await full_bank_info_5(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

    
########
@router.callback_query(lambda c: c.data == 'menu_5')
async def chat_link_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:    
        await chat_link(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )


#########
@router.callback_query(lambda c: c.data == 'menu_6')
async def tos_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:    
        await tos(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

#########
@router.callback_query(lambda c: c.data == 'menu_7')
async def add_partner_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await add_partner_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.add_partner_1))
async def add_partner_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await add_partner_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(StateFilter(UserState.add_partner_2))
async def add_partner_3_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await add_partner_3(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )



#########
@router.callback_query(lambda c: c.data == 'menu_8')
async def contact_us_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await contact_us(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(StateFilter(UserState.contuct_us_1))
async def contact_us_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await contact_us_2(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(StateFilter(UserState.contuct_us_2))
async def contact_us_2_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        await contact_us_3(message, state)
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )

@router.callback_query(StateFilter(UserState.contuct_us_3))
async def contact_us_3_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await contact_us_4(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(lambda c: c.data == 'menu_9')
async def pd_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await pd(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(lambda c: c.data == 'menu_10')
async def oferta_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:    
        await oferta(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(lambda c: c.data == 'menu_11')
async def menu_course_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await menu_course_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.callback_query(lambda c: c.data == 'registration')
async def menu_reg_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        await reg_1(callback_query, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )

@router.message(Command("get_chat_id"))
async def chat_command(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} sent message {message.text}")
    try:
        chat_id = message.chat.id
        chat_type = message.chat.type
        await message.reply(
            f"🆔 Chat ID: <code>{chat_id}</code>\n"
            f"📌 Тип чата: {chat_type}",
            parse_mode="HTML"
        )
    except Exception as e:
            logger.error(
                f"Error for user {message.from_user.id}: {e}\n"
                f"Message: {message.text}"
            )
    
async def check_survey_completion(chat_id: int, state: FSMContext, i):
    data = await state.get_data()
    timer = int(data.get(f"timer{i}")) * 60
    await asyncio.sleep(timer)  
    data = await state.get_data()
    
    if not data.get("survey_completed", False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="notification")]
        ])
        await bot.send_message(chat_id, f"{data.get(f'survey{i}')}",reply_markup=keyboard)


async def check_survey_completion_2(chat_id: int, state: FSMContext, i):
    data = await state.get_data()
    timer = int(data.get(f"timer{i}")) * 60
    await asyncio.sleep(timer)  
    data = await state.get_data()
    
    if not data.get("survey_completed_2", False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="notification")]
        ])
        await bot.send_message(chat_id, f"{data.get(f'survey{i}')}",reply_markup=keyboard)



@router.callback_query(lambda c: c.data == 'notification')
async def notification_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback_query.from_user.id} sent callback {callback_query.data}")
    try:
        current_state = await state.get_state()

        if current_state == UserState.reg_1.state:
            await reg_1(callback_query, state)
        elif current_state == UserState.reg_2.state:
            await reg_2(callback_query, state)
        elif current_state == UserState.reg_3.state:
            await reg_3(callback_query, state)
        elif current_state == UserState.reg_4.state:
            await reg_4(callback_query, state)
        elif current_state == UserState.reg_4_1.state:
            await reg_4_1(callback_query, state)
        elif current_state == UserState.course_1.state:
            await course_1(callback_query, state)
        elif current_state == UserState.course_2.state:
            await course_2(callback_query.message, state)
        elif current_state == UserState.course_3.state:
            await course_3(callback_query.message, state)
        elif current_state == UserState.course_4.state:
            await course_4(callback_query.message, state)
        elif current_state == UserState.course_5.state:
            await course_5(callback_query.message, state)
        elif current_state == UserState.course_6.state:
            await course_6(callback_query.message, state)
        elif current_state == UserState.course_7.state:
            await course_7(callback_query.message, state)
        elif current_state == UserState.course_8.state:
            await course_8(callback_query.message, state)
        elif current_state == UserState.course_9.state:
            await course_9(callback_query.message, state)
        elif current_state == UserState.course_10.state:
            await course_10(callback_query.message, state)
    except Exception as e:
            logger.error(
                f"Error for user {callback_query.from_user.id}: {e}\n"
                f"Message: {callback_query.data}"
            )



async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    
    dp = Dispatcher(storage=storage)
    
    
    dp.message.middleware(StateMiddleware())
    dp.include_router(router)
    
    
    dp.startup.register(on_startup)
    
    
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())