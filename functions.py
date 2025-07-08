import os
import gspread
import asyncio
from google.oauth2.service_account import Credentials
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest




async def get_google_sheet_data(sheet_id, range_name, worksheet):
    scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    
    creds = Credentials.from_service_account_info({
        "type": os.getenv("GS_TYPE"),
        "project_id": os.getenv("GS_PROJECT_ID"),
        "private_key_id": os.getenv("GS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GS_CLIENT_EMAIL"),
        "client_id": os.getenv("GS_CLIENT_ID"),
        "auth_uri": os.getenv("GS_AUTH_URI"),
        "token_uri": os.getenv("GS_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GS_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GS_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }, scopes=scope)
    
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).get_worksheet(worksheet) 
    data = sheet.get(range_name)
    return data

async def get_google_sheet(sheet_id: str, list_index: int):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    
    
    creds = Credentials.from_service_account_info({
        "type": os.getenv("GS_TYPE"),
        "project_id": os.getenv("GS_PROJECT_ID"),
        "private_key_id": os.getenv("GS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GS_CLIENT_EMAIL"),
        "client_id": os.getenv("GS_CLIENT_ID"),
        "auth_uri": os.getenv("GS_AUTH_URI"),
        "token_uri": os.getenv("GS_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GS_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GS_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }, scopes=scope)
    
    try:
        client = await asyncio.to_thread(gspread.authorize, creds)
        
        spreadsheet = await asyncio.to_thread(client.open_by_key, sheet_id)
        worksheet = await asyncio.to_thread(spreadsheet.get_worksheet, list_index)
        return worksheet
    except Exception as e:
        print(f"Ошибка доступа к Google Sheets: {e}")
        raise

async def get_google_sheet_notification(sheet_id: str, list_index: int):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds = Credentials.from_service_account_info({
        "type": os.getenv("GS_TYPE"),
        "project_id": os.getenv("GS_PROJECT_ID"),
        "private_key_id": os.getenv("GS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GS_CLIENT_EMAIL"),
        "client_id": os.getenv("GS_CLIENT_ID"),
        "auth_uri": os.getenv("GS_AUTH_URI"),
        "token_uri": os.getenv("GS_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GS_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GS_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }, scopes=scope)
    
    try:
        client = await asyncio.to_thread(gspread.authorize, creds)
        spreadsheet = await asyncio.to_thread(client.open_by_key, sheet_id)
        worksheet = await asyncio.to_thread(spreadsheet.get_worksheet, list_index)
        
        # Получаем все значения из листа
        records = await asyncio.to_thread(worksheet.get_all_records)
        return records
    except Exception as e:
        print(f"Ошибка доступа к Google Sheets: {e}")
        raise

async def get_range_data(sheet_id, worksheet, state: FSMContext):
    range_name = "B2:B2"
    value = await get_google_sheet_data(sheet_id, range_name, worksheet)
    row_data = value[0]
    return row_data[0]

async def get_table_data(sheet_id, worksheet, state: FSMContext):
    
    if worksheet == 0:
        
        range_name = await get_range_data(sheet_id, worksheet, state)
        value = await get_google_sheet_data(sheet_id, range_name, worksheet)
        row_data = value[0]
        await state.update_data(
            notification_chat=row_data[0],
            cash_amount=row_data[2],
            reg_1=row_data[3],
            reg_2=row_data[4],
            reg_3=row_data[5],
            send_client_1=row_data[6],
            send_client_2=row_data[7],
            send_client_3=row_data[8],
            client_status=row_data[9],
            ref_link_1=row_data[10],
            ref_link_2=row_data[11],
            empty_bank_info=row_data[12],
            bank_1=row_data[13],
            bank_2=row_data[14],
            bank_3=row_data[15],
            bank_4=row_data[16],
            partner_chat=row_data[17],
            tos=row_data[18],
            add_partner_1=row_data[19],
            add_partner_2=row_data[20],
            add_partner_3=row_data[21],
            add_partner_4=row_data[22],
            add_partner_5=row_data[23],
            contuct_us_1 = row_data[24],
            contuct_us_2 = row_data[25],
            pd=row_data[26],
            oferta=row_data[27]
            )
    elif worksheet == 1:
        user_data = await state.get_data()
        range_id = user_data.get('func_id')
        range_name = f"A{range_id}:T{range_id}"
        value = await get_google_sheet_data(sheet_id, range_name, worksheet)
        row_data = value[0]
        await state.update_data(
            text_1=row_data[0],
            text_2=row_data[1],
            text_3=row_data[2],
            text_4=row_data[3],
            text_5=row_data[4],
            text_6=row_data[5],
            text_7=row_data[6],
            text_8=row_data[7],
            text_9=row_data[8],
            text_10=row_data[9],
            video_1=row_data[10],
            video_2=row_data[11],
            video_3=row_data[12],
            video_4=row_data[13],
            video_5=row_data[14],
            video_6=row_data[15],
            video_7=row_data[16],
            video_8=row_data[17],
            video_9=row_data[18],
            video_10=row_data[19]
            )
        


#
async def check_user_reg(sheet_id, user_id, phone_number):
    sheet = await get_google_sheet(sheet_id, 2)
    data = await asyncio.to_thread(sheet.get_all_records)
    
    if not data or not isinstance(data, list):
        return False
    if not phone_number.startswith("+"):
                phone_number = f"+{phone_number.lstrip('+')}"

    for row in data:  
        if str(user_id) == str(row.get('id Партнера', '')) and str(phone_number) == str(row.get('Номер телефона', '')):
            return True
    
    return False


async def get_user_reg(sheet_id, user_id):
    sheet = await get_google_sheet(sheet_id, 2)
    data = await asyncio.to_thread(sheet.get_all_records)
    
    
    
    for row in data:  
        if str(user_id) == str(row.get('id Партнера', '')):
            user_name = str(row.get('Имя', ''))
            bank_card = str(row.get('Инормация для выплат Номер карты', ''))
            bank_bank = str(row.get('Инормация для выплат Банк', ''))
            bank_sbp = str(row.get('Инормация для выплат Номер телефона СБП', ''))
            bank_fio = str(row.get('Инормация для выплат Имя получателя', ''))
            return user_name, bank_card, bank_bank, bank_sbp, bank_fio
    
    

async def write_to_google_sheet(
    sheet_id: str,
    user_id: str,
    username: str,
    first_name: str = None,
    last_name: str = None,
    user_phone: str = None,
    bank_info_card_number: str = None,
    bank_info_bank: str = None,
    bank_info_sbp: str = None,
    bank_info_fio: str = None,
    status: str = None
) -> bool:
    try:
        sheet = await get_google_sheet(sheet_id, 2)
        data = await asyncio.to_thread(sheet.get_all_records)

        if user_phone:
            user_phone = user_phone.lstrip('+')
            user_phone = f"+{user_phone}" 

        user_row = None
        for i, row in enumerate(data, start=2):
            if str(user_id) == str(row.get('id Партнера', '')):
                user_row = i
                break

        update_data = {
            'id Партнера': user_id,
            'ТГ Ник': f"@{username}",
            'Ссылка на партнера': f"https://t.me/{username}",
            'Имя': first_name or "",
            'Фамилия': last_name or "",
            'Номер телефона': user_phone,
            'Инормация для выплат Номер карты': bank_info_card_number,
            'Инормация для выплат Банк': bank_info_bank or "",
            'Инормация для выплат Номер телефона СБП': bank_info_sbp or "",
            'Инормация для выплат Имя получателя': bank_info_fio or "",
            'Статус': status or ""
        }

        if user_row:
            current_values = data[user_row-2]
            need_phone_format = False
            need_card_format = False

            if user_phone is not None and str(current_values.get('Номер телефона', '')) != user_phone:
                need_phone_format = True
            
            if bank_info_card_number is not None and str(current_values.get('Инормация для выплат Номер карты', '')) != bank_info_card_number:
                need_card_format = True

            if need_phone_format or need_card_format:
                columns_to_format = []
                if need_phone_format:
                    columns_to_format.append(f'F{user_row}')
                if need_card_format:
                    columns_to_format.append(f'G{user_row}')
                
                if columns_to_format:
                    await asyncio.to_thread(
                        sheet.format,
                        ','.join(columns_to_format),
                        {"numberFormat": {"type": "TEXT"}}
                    )

            for key, value in update_data.items():
                if value is not None:
                    current_values[key] = value

            row_values = [
                current_values.get('id Партнера', ''),
                current_values.get('ТГ Ник', ''),
                current_values.get('Ссылка на партнера', ''),
                current_values.get('Имя', ''),
                current_values.get('Фамилия', ''),
                current_values.get('Номер телефона', ''),
                current_values.get('Инормация для выплат Номер карты', ''),
                current_values.get('Инормация для выплат Банк', ''),
                current_values.get('Инормация для выплат Номер телефона СБП', ''),
                current_values.get('Инормация для выплат Имя получателя', ''),
                current_values.get('Статус', '')
            ]
            
            await asyncio.to_thread(sheet.update, f'A{user_row}:K{user_row}', [row_values])
        else:
            new_row = [
                user_id,
                f"@{username}",
                f"https://t.me/{username}",
                first_name or "",
                last_name or "",
                user_phone,
                bank_info_card_number,
                bank_info_bank or "",
                bank_info_sbp or "",
                bank_info_fio or "",
                status or ""
            ]
            
            last_row = len(data) + 2
            if user_phone is not None:
                await asyncio.to_thread(
                    sheet.format,
                    f'F{last_row}',
                    {"numberFormat": {"type": "TEXT"}}
                )
            if bank_info_card_number is not None:
                await asyncio.to_thread(
                    sheet.format,
                    f'G{last_row}',
                    {"numberFormat": {"type": "TEXT"}}
                )
            
            await asyncio.to_thread(sheet.append_row, new_row)

        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False
    
#
async def write_to_lead_google_sheet(
    sheet_id: str,
    first_name: str,
    ref_phone: str,
    user_id: str,
    username: str,
    ref_cash: str
) -> bool:

    try:
        sheet = await get_google_sheet(sheet_id, 3)
        data = await asyncio.to_thread(sheet.get_all_records)
        if ref_phone.startswith("+"):
                    ref_phone_check = f"{ref_phone.lstrip('+')}"
        for row in data:
            if str(ref_phone_check) == str(row.get('Номер телефона', '')):
                return False
        

        ref_id = ref_phone

        status = "Рекомендация в работе"
               
        
            
        new_row = [
            ref_id,                                     # A id Реферала
            first_name,                                 # B Имя
            ref_phone or "",                            # C Номер телефона
            user_id,                                    # D id Партнера
            f"https://t.me/{username}" or "" ,          # E Ссылка на партнера    
            status,                                     # F Статус
            ref_cash                                    # G Запланированная выплата
            ]
        
        await asyncio.to_thread(sheet.append_row, new_row)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False
    

async def read_lead_google_sheet(
    sheet_id: str,
    user_id: str,
    lead_status: str
) -> bool:

    try:
        sheet = await get_google_sheet(sheet_id, 3)
        data = await asyncio.to_thread(sheet.get_all_records)
        print (data)
        ref_status = []
        i = 0
        for row in data:  
            if i <= 9:
                if str(user_id) == str(row.get('id Партнера', '')) and lead_status == str(row.get('Статус', '')):
                    ref_name = str(row.get('Имя', ''))
                    ref_phone = str(row.get('Номер телефона', ''))
                    ref_cash = str(row.get('Запланированная выплата', ''))
                    ref_status.append(f"Имя реферала: {ref_name} \nНомер телефона: {ref_phone} \nЗапланированная выплата: {ref_cash}\n\n")
                    i = i+1
        
        return ref_status




    except Exception as e:
        print(f"Ошибка чтения Google Sheets: {e}")
        return False
    
async def change_bank_info_google_sheet(
    sheet_id: str,
    user_id: str,
    bank_info: str,
    subject_to_change: str
) -> bool:

    try:
        sheet = await get_google_sheet(sheet_id, 2)
        data = await asyncio.to_thread(sheet.get_all_records)
        
        column_map = {
            "card": "G",
            "bank": "H",
            "sbp": "I",
            "fio": "J"
        }
        column = column_map[bank_info]

        for i, row in enumerate(data, start=2):  
            if str(user_id) == str(row.get('id Партнера', '')):
                cell = f"{column}{i}"
                await asyncio.to_thread(sheet.update, cell, [[subject_to_change]])
                break  


        return        
        
        




    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False
    


async def get_username_by_id(bot: Bot, user_id: int) -> str | None:
    try:
        user = await bot.get_chat(user_id)
        return user.username
    except Exception as e:
        print(f"Ошибка при получении username: {e}")
        return None



async def write_to_contact_google_sheet(
    sheet_id: str,
    user_id: str,
    username: str,
    first_name: str,
    user_phone: str,
    text_to_send: str
) -> bool:

    try:
        

        sheet = await get_google_sheet(sheet_id, 4)
        
        if not user_phone.startswith("+"):
                user_phone = f"+{user_phone.lstrip('+')}"
                   
        # user_row = None
        # for i, row in enumerate(data, start=2):
        #         if str(user_id) == str(row.get('id Партнера', '')):
        #             user_row = i
        #             break
        
       
        # update_data = {
        #     'id Партнера': user_id,
        #     'ТГ Ник': f"@{username}",
        #     'Ссылка на партнера': f"https://t.me/{username}",
        #     'Имя': first_name or "",
        #     'Фамилия': last_name or "",
        #     'Номер телефона': user_phone or "",
        #     'Инормация для выплат Номер карты': bank_info_card_number or "",
        #     'Инормация для выплат Банк': bank_info_bank or "",
        #     'Инормация для выплат Номер телефона СБП': bank_info_sbp or "",
        #     'Инормация для выплат Имя получателя': bank_info_fio or "",
        #     'Статус': status or ""
        # }
       
        

        # if user_row:
        #     current_values = data[user_row-2]

        #     for key, value in update_data.items():
        #         if value is not None and value != "":
        #             current_values[key] = value
            
        #     row_values = [
        #         current_values.get('id Партнера', ''),
        #         current_values.get('ТГ Ник', ''),
        #         current_values.get('Ссылка на партнера', ''),
        #         current_values.get('Имя', ''),
        #         current_values.get('Фамилия', ''),
        #         current_values.get('Номер телефона', ''),
        #         current_values.get('Инормация для выплат Номер карты', ''),
        #         current_values.get('Инормация для выплат Банк', ''),
        #         current_values.get('Инормация для выплат Номер телефона СБП', ''),
        #         current_values.get('Инормация для выплат Имя получателя', ''),
        #         current_values.get('Статус', '')
        #     ]
            
        #     await asyncio.to_thread(sheet.update, f'A{user_row}:K{user_row}', [row_values])
        # else:
            
        new_row = [
            user_id,                                   
            first_name,
            user_phone,
            f"https://t.me/{username}",                 
            text_to_send,                         
            ]
        
        await asyncio.to_thread(sheet.append_row, new_row)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False