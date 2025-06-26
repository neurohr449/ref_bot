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


async def menu_message(message: Message, state: FSMContext):
    await state.set_state(UserState.menu)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    user_name, bank_card, bank_bank, bank_sbp, bank_fio = await get_user_reg(sheet_id, user_id)
    await state.update_data(user_name = user_name,
                            bank_card=bank_card,
                            bank_bank = bank_bank,
                            bank_sbp = bank_sbp,
                            bank_fio = bank_fio)
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
                  InlineKeyboardButton(text="Связь с менеджером", callback_data = "menu_8")]
                  ],
        
    )
    await message.answer(text=text,reply_markup=keyboard)

async def menu(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.menu)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = callback_query.from_user.id
    user_name, bank_card, bank_bank, bank_sbp, bank_fio = await get_user_reg(sheet_id, user_id)
    await state.update_data(user_name = user_name,
                            bank_card=bank_card,
                            bank_bank = bank_bank,
                            bank_sbp = bank_sbp,
                            bank_fio = bank_fio)
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
                  InlineKeyboardButton(text="Связь с менеджером", callback_data = "menu_8")]
                  ],
        
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
    user_data = await state.get_data()
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
    phone_number = message.contact.phone_number
    user_reg_status = await check_user_reg(sheet_id, user_id)
    if phone_number:
        if user_reg_status == False:
            await state.update_data(phone=phone_number)
            await message.answer(text = f"Мы не нашли личный кабинет по номеру телефона {phone_number}. Давайте зарегистрируем вас.  \n\n✏️ Пожалуйста, введите ваше имя, чтобы продолжить.", reply_markup=ReplyKeyboardRemove())
            await state.set_state(UserState.reg_2)
        else:
            
            await menu_message(message, state)
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
        user_phone = user_data.get('phone')
        func_id = user_data.get('func_id')
        await write_to_google_sheet(sheet_id=sheet_id,
                                    user_id=callback_query.from_user.id,
                                    username=callback_query.from_user.username,
                                    first_name=user_data.get('user_name'),
                                    last_name=user_data.get('user_last_name'),
                                    user_phone=user_phone
                                    )
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
    sheet_id = user_data.get('sheet_id')
    await write_to_lead_google_sheet(
        sheet_id=sheet_id,
        first_name=client_name,
        ref_phone=lead_phone,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username
    )
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
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def ref_link_1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('ref_link_1')
    text_2 = user_data.get('ref_link_2')
    sheet_id = user_data.get('sheet_id')
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text)
    await callback_query.message.answer(text = f"{text_2} https://t.me/teferal_test_bot?start={sheet_id}_{user_id}_1", reply_markup = keyboard)

async def bank_info_1(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.bank_info_change)
    
    
    user_data = await state.get_data()
    card_number = user_data.get('bank_card')
    if not card_number:
        card_number = ""
    bank_name = user_data.get('bank_bank')
    if not bank_name:
        bank_name = ""
    bank_sbp = user_data.get('bank_sbp')
    if not bank_sbp:
        bank_sbp = ""
    bank_fio = user_data.get('bank_fio')
    if not bank_fio:
        bank_fio = ""
    text = f"Ваши реквизиты 📝  \nУ нас сохранены следующие реквизиты для выплат:     \n\n — Номер карты: {card_number}     \n— Банк: {bank_name}     \n— Телефон: {bank_sbp}     \n— ФИО получателя: {bank_fio}   \n\nЧтобы изменить реквизиты, выберите нужную кнопку ниже. 😊"
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
    await state.update_data(card_number = message.text)
    user_data = state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "card"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, message.text)
    await bank_info_1(message, state)

async def bank_info_change_bank_2(message: Message, state: FSMContext):
    await state.update_data(bank_name = message.text)
    user_data = state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "bank"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, message.text)
    await bank_info_1(message, state)

async def bank_info_change_sbp_2(message: Message, state: FSMContext):
    await state.update_data(bank_sbp = message.text)
    user_data = state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "sbp"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, message.text)
    await bank_info_1(message, state)

async def bank_info_change_fio_2(message: Message, state: FSMContext):
    await state.update_data(bank_fio = message.text)
    user_data = state.get_data()
    sheet_id = user_data.get('sheet_id')
    user_id = message.from_user.id
    bank_info = "fio"
    await change_bank_info_google_sheet(sheet_id, user_id, bank_info, message.text)
    await bank_info_1(message, state)

async def chat_link(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('partner_chat')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)

async def tos(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('tos')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ])
    await callback_query.message.answer(text = text, reply_markup = keyboard)

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


