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
from all_states import *
from database import *
from main import chat_notification, bot

FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])
TELEGRAM_VIDEO_PATTERN = r'https://t\.me/'


async def menu_message(message: Message, state: FSMContext):
    await state.set_state(UserState.menu)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    if sheet_id is None:
        await load_user_data_to_state(user_id, state)
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        await get_table_data(sheet_id, 0, state)
    # user_name, bank_card, bank_bank, bank_sbp, bank_fio = await get_user_reg(sheet_id, user_id)
    # await state.update_data(user_name = user_name,
    #                         bank_card=bank_card,
    #                         bank_bank = bank_bank,
    #                         bank_sbp = bank_sbp,
    #                         bank_fio = bank_fio)
    user_data = await state.get_data()
    name = user_data.get('user_name')
    text = f"🏠 Главное меню 🎉 {name}, рады видеть вас снова! Выберите необходимый раздел для работы с вашими рекомендациями."
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Отправить клиента", callback_data = "menu_1"),
                  InlineKeyboardButton(text="Узнать статус клиентов", callback_data = "menu_2")],
                  [InlineKeyboardButton(text="Реферальная ссылка", callback_data = "menu_3"),
                  InlineKeyboardButton(text="Мои реквезиты", callback_data = "menu_4")],
                  [InlineKeyboardButton(text="Общий чат партнеров", callback_data = "menu_5"),
                  InlineKeyboardButton(text="Условия партнерства", callback_data = "menu_6")],
                  [InlineKeyboardButton(text="Добавить партнера", callback_data = "menu_7"),
                  InlineKeyboardButton(text="Связь с менеджером", callback_data = "menu_8")],
                  [InlineKeyboardButton(text="Согласие на обработку персональных данных", callback_data = "menu_9"),
                  InlineKeyboardButton(text="Оферта", callback_data = "menu_10")]
                  ],
        
    )
    await message.answer(text=text,reply_markup=keyboard)

async def menu(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.menu)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = callback_query.from_user.id
    if sheet_id is None:
        await load_user_data_to_state(user_id, state)
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        await get_table_data(sheet_id, 0, state)
    # user_name, bank_card, bank_bank, bank_sbp, bank_fio = await get_user_reg(sheet_id, user_id)
    # await state.update_data(user_name = user_name,
    #                         bank_card=bank_card,
    #                         bank_bank = bank_bank,
    #                         bank_sbp = bank_sbp,
    #                         bank_fio = bank_fio)
    user_data = await state.get_data()
    name = user_data.get('user_name')
    text = f"🏠 Главное меню 🎉 {name}, рады видеть вас снова! Выберите необходимый раздел для работы с вашими рекомендациями."
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Отправить клиента", callback_data = "menu_1"),
                  InlineKeyboardButton(text="Узнать статус клиентов", callback_data = "menu_2")],
                  [InlineKeyboardButton(text="Реферальная ссылка", callback_data = "menu_3"),
                  InlineKeyboardButton(text="Мои реквезиты", callback_data = "menu_4")],
                  [InlineKeyboardButton(text="Общий чат партнеров", callback_data = "menu_5"),
                  InlineKeyboardButton(text="Условия партнерства", callback_data = "menu_6")],
                  [InlineKeyboardButton(text="Добавить партнера", callback_data = "menu_7"),
                  InlineKeyboardButton(text="Связь с менеджером", callback_data = "menu_8")],
                  [InlineKeyboardButton(text="Согласие на обработку персональных данных", callback_data = "menu_9"),
                  InlineKeyboardButton(text="Оферта", callback_data = "menu_10")]
                  ],
        
    )
    await callback_query.message.edit_text(text=text,reply_markup=keyboard)


async def main_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserState.menu)
    await menu(callback_query, state)

###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###
async def reg_1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id=callback_query.from_user.id
    await state.update_data(tg_id = user_id)
    await get_table_data(sheet_id, 0, state)
    user_data = await state.get_data()
    update_status = await write_to_google_sheet(sheet_id=sheet_id,
                                    user_id=callback_query.from_user.id,
                                    username=callback_query.from_user.username,
                                    status="Начал чат-бота"
                                    )
    text = user_data.get('reg_1')
    text_2 = user_data.get('reg_2')
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
    )
    if text:
        await callback_query.message.answer(text=text)
        await callback_query.message.answer(text=text_2, reply_markup = contact_keyboard)
        await state.set_state(UserState.reg_1)


async def reg_2(message: Message, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    if message.contact and message.contact.phone_number:
        phone_number = message.contact.phone_number
    elif message.text:
        phone_number = message.text
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number.lstrip('+')}"
    pattern = re.compile(r'^\+7\d{10}$')
    match = re.fullmatch(pattern, phone_number)
    
    if match:
        
        if phone_number:
            user_reg_status = await check_user_reg(sheet_id, user_id, phone_number)
            if user_reg_status == False:
                await state.update_data(phone=phone_number)
                await message.answer(text = f"Мы не нашли личный кабинет по номеру телефона {phone_number}. Давайте зарегистрируем вас.  \n\n✏️ Пожалуйста, введите ваше имя, чтобы продолжить.", reply_markup=ReplyKeyboardRemove())
                await state.set_state(UserState.reg_2)
            else:
                text = "Нашли ваш профиль!"
                await message.answer(text = text, reply_markup=ReplyKeyboardRemove())
                await menu_message(message, state)
        else:
            await message.answer("Не удалось получить номер телефона. Попробуйте снова", reply_markup=FAIL_KEYBOARD)
    else:
        await message.answer("Введите телефон в формате +7xxxxxxxxxx")


async def reg_3(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_name = message.text
    await state.update_data(user_name=user_name)
    text = user_data.get('reg_3')
    if text:
        await message.answer(text=text)
        await state.set_state(UserState.reg_3)


async def reg_4(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_last_name = message.text
    user_name = user_data.get('user_name')
    phone = user_data.get('phone')
    await state.update_data(user_last_name=user_last_name)
    text = f"🔎 Пожалуйста, проверьте введённые данные:      \n\n— Имя: {user_name}     \n— Фамилия:{user_last_name}     \n— Телефон: {phone}  \n\n------ \nЕсли всё верно, нажмите кнопку «Далее» для перехода к следующему шагу.  Если нужно что-то изменить, нажмите «Изменить»— вы сможете внести корректировки."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data="next"),InlineKeyboardButton(text="Изменить", callback_data="change")]
    ])
    user_data = await state.get_data()
    await save_user_data(user_data)
    await message.answer(text=text, reply_markup = keyboard)
    await state.set_state(UserState.reg_4)

###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###
###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###

async def course_1(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "next":
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        user_phone = user_data.get('phone')
        first_name=user_data.get('user_name')
        last_name=user_data.get('user_last_name')
        ref_id = user_data.get('ref_id')
        ref_cash = user_data.get("cash_amount")
        if ref_id == "1":
            if not user_phone.startswith("+"):
                user_phone = f"+{user_phone.lstrip('+')}"
            update_status = await write_to_google_sheet(sheet_id=sheet_id,
                                        user_id=callback_query.from_user.id,
                                        username=callback_query.from_user.username,
                                        first_name=first_name,
                                        last_name=last_name,
                                        user_phone=user_phone,
                                        status = "Начал обучение"
                                        )
            print(update_status)
            chat_text = f"Новый партнер прошел регистрацию и начал обучение\n\nИмя: {first_name}\nФамилия: {last_name}\nНомер телефона: {user_phone}"
            chat_id = user_data.get('notification_chat')
            await chat_notification(chat_id, chat_text)
        else:
            username = await get_username_by_id(bot, ref_id)
            update_status = await write_to_lead_google_sheet(sheet_id=sheet_id,
                                                             first_name=first_name,
                                                             ref_phone=user_phone,
                                                             user_id=ref_id,
                                                             username=username,
                                                             ref_cash=ref_cash
                                        )
            print(update_status)
            update_status_2 = await write_to_google_sheet(sheet_id=sheet_id,
                                        user_id=callback_query.from_user.id,
                                        username=callback_query.from_user.username,
                                        first_name=first_name,
                                        last_name=last_name,
                                        user_phone=user_phone,
                                        status = "Начал обучение"
                                        )
            print(update_status_2)
            chat_text = f"Новый клиент прошел регистрацию и начал обучение\n\nИмя: {first_name}\nФамилия: {last_name}\nНомер телефона: {user_phone}"
            chat_id = user_data.get('notification_chat')
            await chat_notification(chat_id, chat_text)
        await get_table_data(sheet_id, 1, state)
        user_data = await state.get_data()
        text = user_data.get('text_1')
        video = user_data.get('video_1')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Продолжить", callback_data="next")]
                ])
        if text:
            match = re.search(TELEGRAM_VIDEO_PATTERN, video)
            if match:
                
                await callback_query.message.answer_video(video=video)
                await callback_query.message.answer(text=text, reply_markup = keyboard)
                await state.set_state(UserState.course_1)
                await callback_query.answer()
            else:
                
                await callback_query.message.answer(text=text, reply_markup = keyboard)
                await state.set_state(UserState.course_1)
                await callback_query.answer()
        else:
            await state.set_state(UserState.menu)
            await end_course_handler(callback_query, state)

    elif callback_query.data == "change":
        await callback_query.message.answer("Введите ваше имя")
        await state.set_state(UserState.reg_2)

async def course_2(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_2')
    video = user_data.get('video_2')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_2)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_2)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_3(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_3')
    video = user_data.get('video_3')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_3)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_3)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_4(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_4')
    video = user_data.get('video_4')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_4)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_4)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_5')
    video = user_data.get('video_5')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_5)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_5)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_6(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_6')
    video = user_data.get('video_6')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_6)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_6)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_7(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_7')
    video = user_data.get('video_7')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_7)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_7)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def course_8(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_8')
    video = user_data.get('video_8')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_8)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_8)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)


async def course_9(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_9')
    video = user_data.get('video_9')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_9)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_9)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)


async def course_10(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_10')
    video = user_data.get('video_10')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в меню", callback_data="next")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_10)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_10)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await end_course_handler(callback_query, state)

async def end_course_handler(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    update_status = await write_to_google_sheet(sheet_id=sheet_id,
                                    user_id=callback_query.from_user.id,
                                    username=callback_query.from_user.username,
                                    status = "Закончил обучение"
                                    )
    print(update_status)
    user_phone = user_data.get('phone')
    first_name=user_data.get('user_name')
    last_name=user_data.get('user_last_name')
    chat_id = user_data.get('notification_chat')
    chat_text = f"Партнер прошел обучение\n\nИмя: {first_name}\nФамилия: {last_name}\nНомер телефона: {user_phone}"
    await chat_notification(chat_id, chat_text)
    await state.set_state(UserState.menu)
    await menu(callback_query, state)

###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###

###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu###Menu

async def send_client_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.send_client_1)
    user_data = await state.get_data()
    text = user_data.get('send_client_1')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить", callback_data="next"),
             InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)

async def send_client_2(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.send_client_2)
    user_data = await state.get_data()
    text = user_data.get('send_client_2')
    await callback_query.message.edit_text(text = text)

async def send_client_3(message: Message, state: FSMContext):
    lead_fio = message.text
    await state.update_data(lead_fio=lead_fio)
    await state.set_state(UserState.send_client_3)
    user_data = await state.get_data()
    text = user_data.get('send_client_3')
    await message.answer(text = text)

async def send_client_4(message: Message, state: FSMContext):
    lead_phone = message.text
    pattern = re.compile(r'^\+7\d{10}$')
    match = re.fullmatch(pattern, lead_phone)
    
    if match:
        user_data = await state.get_data()
        client_name = user_data.get('lead_fio')
        await state.update_data(lead_phone=lead_phone)
        await state.set_state(UserState.send_client_4)
        text = f"Проверьте данные перед отправкой менеджеру.   \n\nИмя клиента: {client_name} \nНомер телефона{lead_phone}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data="confurm"),
                InlineKeyboardButton(text="Редактировать", callback_data="edit")]
                ])
        await message.answer(text = text, reply_markup = keyboard)
    else:
        await message.answer("Введите телефон в формате +7xxxxxxxxxx")
#
async def send_client_5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    client_name = user_data.get('lead_fio')
    lead_phone = user_data.get('lead_phone')
    sheet_id = user_data.get('sheet_id')
    ref_cash = user_data.get('cash_amount')
    await write_to_lead_google_sheet(
        sheet_id=sheet_id,
        first_name=client_name,
        ref_phone=lead_phone,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username,
        ref_cash=ref_cash
    )
    chat_text = f"Новый клиент\n\n Имя: {client_name}\nНомер телефона: {lead_phone}"
    chat_id = user_data.get('notification_chat')
    await chat_notification(chat_id, chat_text)
    text = f"Данные переданы менеджеру.   \n\nИмя клиента: {client_name} \nНомер телефона: {lead_phone}   \n\nИнформацию о данном клиенте можно увидеть в разделе \"Узнать статус клиентов\""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)
#####################
async def client_status_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.client_status_1)
    user_data = await state.get_data()
    text = user_data.get('client_status')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Рекомендации в работе", callback_data="in_progress"),
             InlineKeyboardButton(text="Ожидают выплаты", callback_data="waiting_for_payment")],
             [InlineKeyboardButton(text="Выплачено", callback_data="payed"),
             InlineKeyboardButton(text="Отказано", callback_data="denied")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)

async def client_status_2(callback_query: CallbackQuery, state: FSMContext):
    status = callback_query.data
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = callback_query.from_user.id

    if status == "in_progress":
        func_status = "Рекомендация в работе"
    elif status == "waiting_for_payment":
        func_status = "Ожидают выплаты"
    elif status == "payed":
        func_status = "Выплачено"
    elif status == "denied":
        func_status = "Отказано"
    lead_list = await read_lead_google_sheet(sheet_id, user_id, func_status)

    formatted_lead_list = "".join(lead_list).strip()

    text = f"Список клиентов по статусу: {func_status}\n\n {formatted_lead_list}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)

async def ref_link_1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('ref_link_1')
    text_2 = user_data.get('ref_link_2')
    sheet_id = user_data.get('sheet_id')
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text)
    await callback_query.message.answer(text = f"{text_2} https://t.me/teferal_test_bot?start={sheet_id}_{user_id}_2", reply_markup = keyboard)

async def bank_info_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change)
    
    
    user_data = await state.get_data()
    card_number = user_data.get('bank_card')
    bank_name = user_data.get('bank_bank')
    bank_sbp = user_data.get('bank_sbp')
    bank_fio = user_data.get('bank_fio')
    if card_number != None:
        text = f"Ваши реквизиты 📝  \nУ нас сохранены следующие реквизиты для выплат:     \n\n — Номер карты: {card_number}     \n— Банк: {bank_name}     \n— Телефон: {bank_sbp}     \n— ФИО получателя: {bank_fio}   \n\nЧтобы изменить реквизиты, выберите нужную кнопку ниже. 😊"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Номер карты", callback_data="card_number"),
                InlineKeyboardButton(text="Банк", callback_data="bank")],
                [InlineKeyboardButton(text="Телефон(СБП)", callback_data="sbp"),
                InlineKeyboardButton(text="ФИО получателя", callback_data="fio")],
                [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
                ])
        await callback_query.message.edit_text(text = text, reply_markup = keyboard)
    else:
        text = user_data.get('empty_bank_info')
        await callback_query.message.edit_text(text = text)
        await full_bank_info_cb_1(callback_query, state)




async def bank_info_1_message(message: Message, state: FSMContext):
    await state.set_state(UserState.bank_info_change)
    
    
    user_data = await state.get_data()
    card_number = user_data.get('bank_card', "❌ не указан")
    bank_name = user_data.get('bank_bank', "❌ не указан")
    bank_sbp = user_data.get('bank_sbp', "❌ не указан")
    bank_fio = user_data.get('bank_fio', "❌ не указан")
    if card_number != None:
        text = f"Ваши реквизиты 📝  \nУ нас сохранены следующие реквизиты для выплат:     \n\n — Номер карты: {card_number}     \n— Банк: {bank_name}     \n— Телефон: {bank_sbp}     \n— ФИО получателя: {bank_fio}   \n\nЧтобы изменить реквизиты, выберите нужную кнопку ниже. 😊"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Номер карты", callback_data="card_number"),
                InlineKeyboardButton(text="Банк", callback_data="bank")],
                [InlineKeyboardButton(text="Телефон(СБП)", callback_data="sbp"),
                InlineKeyboardButton(text="ФИО получателя", callback_data="fio")],
                [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
                ])
        await message.answer(text = text, reply_markup = keyboard)
    else:
        text = user_data.get('empty_bank_info')
        await message.answer(text = text)
        await full_bank_info_m_1(message, state)

async def full_bank_info_cb_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_1)
    user_data = await state.get_data()
    text = user_data.get('bank_1')
    await callback_query.message.answer(text = text)

async def full_bank_info_m_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_1)
    user_data = await state.get_data()
    text = user_data.get('bank_1')
    await callback_query.message.answer(text = text)

async def full_bank_info_2(message: Message, state: FSMContext):
    
    bank_card = message.text
    await state.set_state(UserState.bank_info_change_card_number)
    pattern = re.compile(r'^\d{16}$')
    match = re.fullmatch(pattern, bank_card)
    if match:
        await state.set_state(UserState.bank_info_2)
        await state.update_data(bank_card=bank_card)
        user_data = await state.get_data()
        text = user_data.get('bank_2')
        await message.answer(text = text)
    else:
        await message.answer("Введите номер карты в формате 16 цифр без пробелов")

async def full_bank_info_3(message: Message, state: FSMContext):
    await state.set_state(UserState.bank_info_3)
    bank_bank = message.text
    await state.update_data(bank_bank=bank_bank)
    user_data = await state.get_data()
    
    text = user_data.get('bank_3')
    await message.answer(text = text)

async def full_bank_info_4(message: Message, state: FSMContext):
    bank_sbp = message.text
    pattern = re.compile(r'^\+7\d{10}$')
    match = re.fullmatch(pattern, bank_sbp)
    if match:
        await state.set_state(UserState.bank_info_4)
        await state.update_data(bank_sbp=bank_sbp)
        user_data = await state.get_data()
        text = user_data.get('bank_4')
        await message.answer(text = text)
    else:
        await message.answer("Введите номер телефона в фомате +7хххххххххх")

async def full_bank_info_5(message: Message, state: FSMContext):
    
    bank_fio = message.text
    await state.update_data(bank_fio=bank_fio)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info_card_number=user_data.get('bank_card')
    bank_info_bank=user_data.get('bank_bank')
    bank_info_sbp=user_data.get('bank_sbp')
    bank_info_fio=user_data.get('bank_fio')
    await save_user_data(user_data)
    update_status = await write_to_google_sheet(sheet_id=sheet_id,
                                                user_id=user_id,
                                                bank_info_card_number=bank_info_card_number,
                                                bank_info_bank=bank_info_bank,
                                                bank_info_sbp=bank_info_sbp,
                                                bank_info_fio=bank_info_fio)
    print(update_status)
    await bank_info_1_message(message, state)

async def bank_info_change_card_number(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change_card_number)
    user_data = await state.get_data()
    text = user_data.get('bank_1')
    await callback_query.message.edit_text(text = text)


async def bank_info_change_bank(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change_bank)
    user_data = await state.get_data()
    text = user_data.get('bank_2')
    await callback_query.message.edit_text(text = text)


async def bank_info_change_sbp(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change_sbp)
    user_data = await state.get_data()
    text = user_data.get('bank_3')
    await callback_query.message.edit_text(text = text)


async def bank_info_change_fio(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change_fio)
    user_data = await state.get_data()
    text = user_data.get('bank_4')
    await callback_query.message.edit_text(text = text)

async def bank_info_change_card_number_2(message: Message, state: FSMContext):
    card_number = message.text
    pattern = re.compile(r'^\d{16}$')
    match = re.fullmatch(pattern, card_number)
    if match:
        await state.update_data(bank_card = card_number)
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        user_id = message.from_user.id
        bank_info = "card"
        await change_bank_info_google_sheet(sheet_id, user_id, bank_info, card_number)
        await save_user_data(user_data)
        await bank_info_1_message(message, state)
    else:
        await message.answer("Введите номер карты в формате 16 цифр без пробелов")

async def bank_info_change_bank_2(message: Message, state: FSMContext):
    bank_name = message.text
    await state.update_data(bank_bank = bank_name)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "bank"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, bank_name)
    await save_user_data(user_data)
    await bank_info_1_message(message, state)

async def bank_info_change_sbp_2(message: Message, state: FSMContext):
    bank_sbp = message.text
    pattern = re.compile(r'^\+7\d{10}$')
    match = re.fullmatch(pattern, bank_sbp)
    if match:
        await state.update_data(bank_sbp = bank_sbp)
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        user_id = message.from_user.id
        bank_info = "sbp"
        await change_bank_info_google_sheet(sheet_id, user_id, bank_info, bank_sbp)
        await save_user_data(user_data)
        await bank_info_1_message(message, state)
    else:
        await message.answer("Введите номер телефона в фомате +7хххххххххх")

async def bank_info_change_fio_2(message: Message, state: FSMContext):
    bank_fio = message.text
    await state.update_data(bank_fio = bank_fio)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "fio"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, bank_fio)
    await save_user_data(user_data)
    await bank_info_1_message(message, state)

async def chat_link(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('partner_chat')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)

async def tos(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('tos')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)

async def add_partner_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.add_partner_1)
    user_data = await state.get_data()
    text = user_data.get('add_partner_1')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔜 Дальше", callback_data="next"),
             InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup = keyboard)


async def add_partner_2(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.add_partner_2)
    user_data = await state.get_data()
    text = user_data.get('add_partner_2')
    
    await callback_query.message.edit_text(text = text)

async def add_partner_3(message: Message, state: FSMContext):
    lead_phone = message.text
    pattern = re.compile(r'^\+7\d{10}$')
    match = re.fullmatch(pattern, lead_phone)
    if match:
        user_data = await state.get_data()
        text = user_data.get('add_partner_3')
        text_2 = user_data.get('add_partner_4')
        sheet_id = user_data.get('sheet_id')
        user_id = message.from_user.id
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
        await message.answer(text = text)
        await message.answer(text = f"{text_2} https://t.me/teferal_test_bot?start={sheet_id}_{user_id}_3", reply_markup=keyboard)
    else:
        await message.answer("Введите телефон в формате +7xxxxxxxxxx")


async def contact_us(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.set_state(UserState.contuct_us_1)
    text = user_data.get('contuct_us_1')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить сообщение", callback_data="next"), 
             InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup=keyboard)

async def contact_us_2(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.set_state(UserState.contuct_us_2)
    text = user_data.get('contuct_us_2')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup=keyboard)

async def contact_us_3(message: Message, state: FSMContext):
    
    await state.set_state(UserState.contuct_us_3)
    text_to_send = message.text
    await state.update_data(text_to_send=text_to_send)
    text = f"Текст для отправки менеджеру: \n\"{text_to_send}\""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить сообщение", callback_data="next"),
             InlineKeyboardButton(text="Изменить", callback_data="change"),
             InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await message.answer(text = text, reply_markup=keyboard)

async def contact_us_4(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "next":
        user_data = await state.get_data()
        text_to_send = user_data.get('text_to_send')
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.username
        first_name = user_data.get('user_name')
        user_phone = user_data.get('phone')
        sheet_id = user_data.get('sheet_id')
        chat_id = user_data.get('notification_chat')
        text_to_chat = f"Новый запрос на связь с менеджером от пользователя:\n id Пользователя: {user_id} \nИмя: {first_name}\nСсылка на чат: https://t.me/{user_name} \n\nТекст сообщения: \n{text_to_send}"
        update_status = await write_to_contact_google_sheet(sheet_id, user_id, user_name,first_name,user_phone,text_to_send)
        await chat_notification(chat_id, text_to_chat)
        text = f"Информация передана менеджеру"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
                ])
        await callback_query.message.edit_text(text = text, reply_markup=keyboard)
    if callback_query.data == "change":
        await contact_us_2(callback_query, state)

async def pd(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('pd')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup=keyboard)

async def oferta(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('oferta')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.edit_text(text = text, reply_markup=keyboard)