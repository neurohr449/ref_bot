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

from functions import *
from callback_functions import *
from all_states import *
from notification import periodic_check


BOT_TOKEN = os.getenv("BOT_TOKEN")
FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])


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
    await menu(callback_query, state)

@router.message(Command("menu"))
async def command_menu(message: Message, state: FSMContext):
    await menu_message(message, state)


async def on_startup(bot: Bot, dp: Dispatcher):
    """Запуск при старте бота."""
    print("🔄 Startup handler called")  # Для отладки
    try:
        pool = await get_connection()  # Создаем пул подключений
        asyncio.create_task(periodic_check(bot, pool, interval=60))
        print("🔄 Фоновая задача periodic_check запущена!")
    except Exception as e:
        print(f"❌ Ошибка в on_startup: {e}")
        raise

@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.set_state(UserState.welcome)
    args = command.args

    if args:
        parts = args.rsplit('_', 2)
        sheet_id  = parts[0]
        ref_id = parts[1]    
        func_id = parts[2]
    else:
        await message.answer("👋 Здравствуйте. Запустите бота по уникальной ссылке!")

    await state.update_data(sheet_id=sheet_id,
                            ref_id=ref_id,
                            func_id=func_id)
    text = "👋 Добро пожаловать в нашу партнёрскую программу!\n\nВ этом Телеграм-боте доступен ваш личный кабинет партнёра:    \n\n— ➕ Добавление новых рекомендаций    \n\n— 🔄 Статусы добавленных рекомендаций    \n\n— 💰 Выплаты    \n\n— 🎓 Обучение и условия    \n\n— 📞 Связь с персональным менеджером\n\nЧтобы начать зарабатывать на рекомендациях, осталось только зарегистрироваться!"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Регистрация", callback_data="next")]
    ])
    
    await message.answer(f"{text}", reply_markup = keyboard)

@router.callback_query(StateFilter(UserState.welcome))
async def reg_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await reg_1(callback_query, state)

@router.message(StateFilter(UserState.reg_1))
async def reg_2_handler(message: Message, state: FSMContext) -> None:
    await reg_2(message, state)

@router.message(StateFilter(UserState.reg_2))
async def reg_3_handler(message: Message, state: FSMContext) -> None:
    await reg_3(message, state)

@router.message(StateFilter(UserState.reg_3))
async def reg_4_handler(message: Message, state: FSMContext) -> None:
    await reg_4(message, state)
    
@router.callback_query(StateFilter(UserState.reg_4_1))
async def reg_4_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await reg_4_1(callback_query, state)  
######################################################################################################################################################################################################################################################
@router.callback_query(StateFilter(UserState.reg_4))
async def course_1_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_1(callback_query, state)

@router.callback_query(StateFilter(UserState.course_1))
async def course_2_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_2(callback_query, state)

@router.callback_query(StateFilter(UserState.course_2))
async def course_3_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_3(callback_query, state)

@router.callback_query(StateFilter(UserState.course_3))
async def course_4_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_4(callback_query, state)

@router.callback_query(StateFilter(UserState.course_4))
async def course_5_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_5(callback_query, state)

@router.callback_query(StateFilter(UserState.course_5))
async def course_6_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_6(callback_query, state)

@router.callback_query(StateFilter(UserState.course_6))
async def course_7_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_7(callback_query, state)

@router.callback_query(StateFilter(UserState.course_7))
async def course_8_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_8(callback_query, state)

@router.callback_query(StateFilter(UserState.course_8))
async def course_9_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_9(callback_query, state)

@router.callback_query(StateFilter(UserState.course_9))
async def course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await course_10(callback_query, state)

@router.callback_query(StateFilter(UserState.course_10))
async def course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await end_course_handler(callback_query, state)
######################################################################################################################################################################################################################################################
#########
@router.callback_query(StateFilter(UserState.menu_course_1))
async def menu_course_2_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_2(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_2))
async def menu_course_3_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_3(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_3))
async def menu_course_4_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_4(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_4))
async def menu_course_5_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_5(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_5))
async def menu_course_6_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_6(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_6))
async def menu_course_7_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_7(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_7))
async def menu_course_8_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_8(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_8))
async def menu_course_9_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_9(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_9))
async def menu_course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_10(callback_query, state)

@router.callback_query(StateFilter(UserState.menu_course_10))
async def menu_course_10_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_end_course_handler(callback_query, state)
######################################################################################################################################################################################################################################################
#########
@router.callback_query(lambda c: c.data == 'menu_1')
async def send_client_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await send_client_1(callback_query, state)

@router.callback_query(StateFilter(UserState.send_client_1))
async def send_client_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await send_client_2(callback_query, state)

@router.message(StateFilter(UserState.send_client_2))
async def send_client_3_handler(message: Message, state: FSMContext) -> None:
    await send_client_3(message, state)

@router.message(StateFilter(UserState.send_client_3))
async def send_client_4_handler(message: Message, state: FSMContext) -> None:
    await send_client_4(message, state)

@router.callback_query(StateFilter(UserState.send_client_4))
async def send_client_5_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    if callback_query.data == "confurm":
        await send_client_5(callback_query, state)
    elif callback_query.data == "edit":
        await send_client_2(callback_query, state)

###########
@router.callback_query(lambda c: c.data == 'menu_2')
async def client_status_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await client_status_1(callback_query, state)

@router.callback_query(StateFilter(UserState.client_status_1))
async def client_status_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await client_status_2(callback_query, state)

############
@router.callback_query(lambda c: c.data == 'menu_3')
async def ref_link_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await ref_link_1(callback_query, state)


############
@router.callback_query(lambda c: c.data == 'menu_4')
async def bank_info_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await bank_info_1(callback_query, state)

@router.callback_query(StateFilter(UserState.bank_info_change))
async def bank_info_change_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    if callback_query.data == "card_number":
        await bank_info_change_card_number(callback_query, state)
    elif callback_query.data == "bank":
        await bank_info_change_bank(callback_query, state)
    elif callback_query.data == "sbp":
        await bank_info_change_sbp(callback_query, state)
    elif callback_query.data == "fio":
        await bank_info_change_fio(callback_query, state)

@router.message(StateFilter(UserState.bank_info_change_card_number))
async def bank_info_change_card_number_handler(message: Message, state: FSMContext) -> None:
    await bank_info_change_card_number_2(message, state)

@router.message(StateFilter(UserState.bank_info_change_bank))
async def bank_info_change_bank_handler(message: Message, state: FSMContext) -> None:
    await bank_info_change_bank_2(message, state)
    
@router.message(StateFilter(UserState.bank_info_change_sbp))
async def bank_info_change_sbp_handler(message: Message, state: FSMContext) -> None:
    await bank_info_change_sbp_2(message, state)

@router.message(StateFilter(UserState.bank_info_change_fio))
async def bank_info_change_fio_handler(message: Message, state: FSMContext) -> None:
    await bank_info_change_fio_2(message, state)

@router.message(StateFilter(UserState.bank_info_1))
async def full_bank_info_1_handler(message: Message, state: FSMContext) -> None:
    await full_bank_info_2(message, state)

@router.message(StateFilter(UserState.bank_info_2))
async def full_bank_info_2_handler(message: Message, state: FSMContext) -> None:
    await full_bank_info_3(message, state)
    
@router.message(StateFilter(UserState.bank_info_3))
async def full_bank_info_3_handler(message: Message, state: FSMContext) -> None:
    await full_bank_info_4(message, state)
@router.message(StateFilter(UserState.bank_info_4))
async def full_bank_info_4_handler(message: Message, state: FSMContext) -> None:
    await full_bank_info_5(message, state)
    

    
########
@router.callback_query(lambda c: c.data == 'menu_5')
async def chat_link_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await chat_link(callback_query, state)



#########
@router.callback_query(lambda c: c.data == 'menu_6')
async def tos_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await tos(callback_query, state)

#########
@router.callback_query(lambda c: c.data == 'menu_7')
async def add_partner_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await add_partner_1(callback_query, state)

@router.callback_query(StateFilter(UserState.add_partner_1))
async def add_partner_2_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await add_partner_2(callback_query, state)

@router.message(StateFilter(UserState.add_partner_2))
async def add_partner_3_handler(message: Message, state: FSMContext) -> None:
    await add_partner_3(message, state)




#########
@router.callback_query(lambda c: c.data == 'menu_8')
async def contact_us_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await contact_us(callback_query, state)

@router.callback_query(StateFilter(UserState.contuct_us_1))
async def contact_us_1_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await contact_us_2(callback_query, state)

@router.message(StateFilter(UserState.contuct_us_2))
async def contact_us_2_handler(message: Message, state: FSMContext) -> None:
    await contact_us_3(message, state)

@router.callback_query(StateFilter(UserState.contuct_us_3))
async def contact_us_3_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await contact_us_4(callback_query, state)

@router.callback_query(lambda c: c.data == 'menu_9')
async def pd_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await pd(callback_query, state)

@router.callback_query(lambda c: c.data == 'menu_10')
async def oferta_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await oferta(callback_query, state)

@router.callback_query(lambda c: c.data == 'menu_11')
async def menu_course_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await menu_course_1(callback_query, state)

# async def get_chat_id(user_id: int):
#     try:
#         chat = await bot.get_chat(user_id)  # Получаем чат по user_id
#         return chat.id
#     except TelegramBadRequest:
#         print("Бот не знает этого пользователя или чата!")
#         return None

# async def chat_notification(chat_id, text):
#     await bot.send_message(chat_id=chat_id,
#                            text=text)

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Сначала создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    
    # Затем регистрируем обработчики
    dp.include_router(router)
    dp.message.middleware(StateMiddleware())
    dp.startup.register(on_startup)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())