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

FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])
TELEGRAM_VIDEO_PATTERN = r'https://t\.me/'

async def menu(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get('user_name')
    text = f"🏠 Главное меню 🎉 {name}, рады видеть вас снова! Выберите необходимый раздел для работы с вашими рекомендациями."
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить клиента", callback_data = "menu_1")],
                  [KeyboardButton(text="Узнать статус клиентов", callback_data = "menu_2")],
                  [KeyboardButton(text="Реферальная ссылка", callback_data = "menu_3")],
                  [KeyboardButton(text="Мои реквезиты", callback_data = "menu_4")],
                  [KeyboardButton(text="Общий чат партнеров", callback_data = "menu_5")],
                  [KeyboardButton(text="Условия партнерства", callback_data = "menu_6")],
                  [KeyboardButton(text="Добавить партнера", callback_data = "menu_7")],
                  [KeyboardButton(text="Связь с менеджером", callback_data = "menu_8")]
                  ],
        resize_keyboard=True,
    )
    await callback_query.message.answer(text=text,reply_markup=keyboard)


async def main_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserState.menu)
    await menu(callback_query, state)

###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###
async def reg_1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    await get_table_data(sheet_id, 0, state)
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
    
    phone_number = message.contact.phone_number
    if phone_number:
        await state.update_data(phone=phone_number)
        await message.answer(text = f"Мы не нашли личный кабинет по номеру телефона {phone_number}. Давайте зарегистрируем вас.  \n\n✏️ Пожалуйста, введите ваше имя, чтобы продолжить.", reply_markup=None)
        await state.set_state(UserState.reg_2)
    else:
        await message.answer("Не удалось получить номер телефона. Попробуйте снова", reply_markup=FAIL_KEYBOARD)

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
    await message.answer(text=text, reply_markup = keyboard)
    await state.set_state(UserState.reg_4)

###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###Reg###
###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###Course###

async def course_1(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "next":
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        func_id = user_data.get('func_id')
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
            await menu(callback_query, state)

    elif callback_query.data == "change":
        await callback_query.message.answer("Введите ваше имя")
        await state.set_state(UserState.reg_2)

async def course_2(callback_query: CallbackQuery, state: FSMContext):
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
            await state.set_state(UserState.course_2)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.course_2)
            await callback_query.answer()
    else:
        await state.set_state(UserState.menu)
        await menu(callback_query, state)

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
        await menu(callback_query, state)

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
        await menu(callback_query, state)

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
        await menu(callback_query, state)

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
        await menu(callback_query, state)

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
        await menu(callback_query, state)

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
        await menu(callback_query, state)


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
        await menu(callback_query, state)


async def course_10(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_10')
    video = user_data.get('video_10')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в меню", callback_data="menu")]
            ])
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, video)
        if match:            
            await callback_query.message.answer_video(video=video)
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.menu)
            await callback_query.answer()
        else:
            
            await callback_query.message.answer(text=text, reply_markup = keyboard)
            await state.set_state(UserState.menu)
            await callback_query.answer()
    else:
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
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def send_client_2(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.send_client_2)
    user_data = await state.get_data()
    text = user_data.get('send_client_2')
    await callback_query.message.answer(text = text)

async def send_client_3(message: Message, state: FSMContext):
    lead_fio = message.text
    await state.update_data(lead_fio=lead_fio)
    await state.set_state(UserState.send_client_3)
    user_data = await state.get_data()
    text = user_data.get('send_client_3')
    await message.answer(text = text)

async def send_client_4(message: Message, state: FSMContext):
    lead_phone = message.text
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


async def send_client_5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    client_name = user_data.get('lead_fio')
    lead_phone = user_data.get('lead_phone')
    text = f"Данные переданы менеджеру.   \n\nИмя клиента: {client_name} \nНомер телефона{lead_phone}   \n\nИнформацию о данном клиенте можно увидеть в разделе \"Узнать статус клиентов\""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)
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
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def client_status_2(callback_query: CallbackQuery, state: FSMContext):
    status = callback_query.data
    client_1, client_2, client_3, client_4, client_5, client_6, client_7, client_8, client_9, client_10 = None
    text = f"Список клиентов по статусу: {status} \n{client_1} \n{client_2} \n{client_3} \n{client_4} \n{client_5} \n{client_6} \n{client_7} \n{client_8} \n{client_9} \n{client_10}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def ref_link_1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('ref_link_1')
    text_2 = user_data.get('ref_link_2')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text)
    await callback_query.message.answer(text = f"{text_2} ссылка", reply_markup = keyboard)

async def bank_info_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change)
    user_data = await state.get_data()
    text = f"Ваши реквизиты 📝  \nУ нас сохранены следующие реквизиты для выплат:     \n\n — Номер карты: {card_number}     \n— Банк: {bank_name}     \n— Телефон: {bank_phone}     \n— ФИО получателя: {bank_name}   \n\nЧтобы изменить реквизиты, выберите нужную кнопку ниже. 😊"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Номер карты", callback_data="card_number"),
             InlineKeyboardButton(text="Банк", callback_data="bank")],
             [InlineKeyboardButton(text="Телефон(СБП)", callback_data="sbp"),
             InlineKeyboardButton(text="ФИО получателя", callback_data="fio")],
             [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def bank_info_change_card_number(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.card_number_change)
    user_data = await state.get_data()
    text = user_data.get('bank_1')
    await callback_query.message.answer(text = text)


async def bank_info_change_bank(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_change)
    user_data = await state.get_data()
    text = user_data.get('bank_2')
    await callback_query.message.answer(text = text)


async def bank_info_change_sbp(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.sbp_change)
    user_data = await state.get_data()
    text = user_data.get('bank_3')
    await callback_query.message.answer(text = text)


async def bank_info_change_fio(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_fio_change)
    user_data = await state.get_data()
    text = user_data.get('bank_4')
    await callback_query.message.answer(text = text)

async def bank_info_change_card_number_2(message: Message, state: FSMContext):
    pass

async def bank_info_change_bank_2(message: Message, state: FSMContext):
    pass

async def bank_info_change_sbp_2(message: Message, state: FSMContext):
    pass

async def bank_info_change_fio_2(message: Message, state: FSMContext):
    pass

async def chat_link(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('partner_chat')
    await callback_query.message.answer(text = text)

async def tos(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('tos')
    await callback_query.message.answer(text = text)

async def add_partner_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.add_partner_1)
    user_data = await state.get_data()
    text = user_data.get('add_partner_1')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔜 Дальше", callback_data="next"),
             InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)


async def add_partner_2(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.add_partner_2)
    user_data = await state.get_data()
    text = user_data.get('add_partner_2')
    
    await callback_query.message.answer(text = text)

async def add_partner_3(message: Message, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('add_partner_3')
    await message.answer(text = text)

async def contact_us(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('tos')
    await callback_query.message.answer(text = text)


async def course_10(callback_query: CallbackQuery, state: FSMContext):
    pass

async def course_10(message: Message, state: FSMContext):
    pass