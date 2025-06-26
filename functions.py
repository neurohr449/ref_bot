import os
import gspread
import asyncio
from google.oauth2.service_account import Credentials
from aiogram.fsm.context import FSMContext



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

async def get_table_data(sheet_id, worksheet, state: FSMContext):
    
    if worksheet == 0:
        range_name = "B2:V2"
        value = await get_google_sheet_data(sheet_id, range_name, worksheet)
        row_data = value[0]
        await state.update_data(
            notification_chat=row_data[0],
            reg_1=row_data[1],
            reg_2=row_data[2],
            reg_3=row_data[3],
            send_client_1=row_data[4],
            send_client_2=row_data[5],
            send_client_3=row_data[6],
            client_status=row_data[7],
            ref_link_1=row_data[8],
            ref_link_2=row_data[9],
            bank_1=row_data[10],
            bank_2=row_data[11],
            bank_3=row_data[12],
            bank_4=row_data[13],
            partner_chat=row_data[14],
            tos=row_data[15],
            add_partner_1=row_data[16],
            add_partner_2=row_data[17],
            add_partner_3=row_data[18],
            add_partner_4=row_data[19],
            add_partner_5=row_data[20]
            )
    elif worksheet == 1:
        range_name = "A2:T2"
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
async def check_user_reg(sheet_id, user_id):
    sheet = await get_google_sheet(sheet_id, 2)
    data = await asyncio.to_thread(sheet.get_all_records)
    
    if not data or not isinstance(data, list):
        return False
    
    for row in data:  
        if str(user_id) == str(row.get('id Партнера', '')):
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
    first_name: str,
    last_name: str,
    user_phone: str,
    bank_info_card_number: str = None,
    bank_info_bank: str = None,
    bank_info_sbp: str = None,
    bank_info_fio: str = None
) -> bool:

    try:
        if not username:
            print("Ошибка: username обязателен")
            return False

        sheet = await get_google_sheet(sheet_id, 2)
        data = await asyncio.to_thread(sheet.get_all_records)
        
                   
        user_row = None
        for i, row in data:  
                if str(user_id) == str(row.get('id Партнера', '')):
                    user_row = i
                    break
        
       
        update_data = {}
        
        if not user_row:
            update_data = {
                'id Партнера': user_id,
                'ТГ Ник': f"@{username}",
                'Имя': first_name,
                'Фамилия': last_name,
                'Номер телефона': user_phone,
                'Инормация для выплат Номер карты': bank_info_card_number or "",
                'Инормация для выплат Банк': bank_info_bank or "",
                'Инормация для выплат Номер телефона СБП': bank_info_sbp or "",
                'Инормация для выплат Имя получателя': bank_info_fio or ""
            }
        

        if user_row:
            current_values = data[user_row-2]

            for key in update_data:
                current_values[key] = update_data[key]
            
            row_values = [
                current_values.get('id Партнера', ''),                              # A
                current_values.get('ТГ Ник', ''),                                   # B
                current_values.get('Имя', ''),                                      # C
                current_values.get('Фамилия', ''),                                  # D
                current_values.get('Номер телефона', ''),                           # E
                current_values.get('Инормация для выплат Номер карты', ''),         # F                                       
                current_values.get('Инормация для выплат Банк', ''),                # G
                current_values.get('Инормация для выплат Номер телефона СБП', ''),  # H
                current_values.get('Инормация для выплат Имя получателя', '')       # I   
            ]
            
            await asyncio.to_thread(sheet.update, f'A{user_row}:S{user_row}', [row_values])
        else:
            
            new_row = [
                user_id,                                     # A Дата
                f"@{username}",                              # B ТГ Ник
                first_name or "",                            # C Имя
                last_name,                                   # D Фамилия
                user_phone,                                  # E Номер телефона
                bank_info_card_number or "",                 # F Инормация для выплат Номер карты
                bank_info_bank or "",                        # G Инормация для выплат Банк
                bank_info_sbp or "",                         # H Инормация для выплат Номер телефона СБП
                bank_info_fio or "",                         # I Инормация для выплат Имя получателя
                ]
            
            await asyncio.to_thread(sheet.append_row, new_row)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False
    

async def write_to_lead_google_sheet(
    sheet_id: str,
    first_name: str,
    ref_phone: str,
    user_id: str,
    username: str
) -> bool:

    try:
        sheet = await get_google_sheet(sheet_id, 3)
        data = await asyncio.to_thread(sheet.get_all_records)
        
        for row in data:
            if str(ref_phone) == str(row.get('Номер телефона', '')):
                return 

        ref_id = ref_phone

        status = "Рекомендация в работе"
               
        
            
        new_row = [
            ref_id,                                     # A id Реферала
            first_name,                                 # B Имя
            ref_phone or "",                            # C Номер телефона
            user_id,                                    # D id Партнера
            f"https://t.me/{username}" or "" ,          # E Ссылка на партнера    
            status                                      # F Статус
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
        for row in data:  
            if str(user_id) == str(row.get('id Партнера', '')) and lead_status == str(row.get('Статус', '')):
                ref_name = str(row.get('Имя', ''))
                ref_phone = str(row.get('Номер телефона', ''))
                ref_status.append(f"{ref_name}, {ref_phone}\n")
                
        
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
        
        for row in data:  
            if str(user_id) == str(row.get('id Партнера', '')):
                
                if bank_info == "card":
                    await asyncio.to_thread(sheet.update, f'F{row}', [subject_to_change])
                elif bank_info == "bank":
                    await asyncio.to_thread(sheet.update, f'G{row}', [subject_to_change])
                elif bank_info == "sbp":
                    await asyncio.to_thread(sheet.update, f'H{row}', [subject_to_change])
                elif bank_info == "fio":
                    await asyncio.to_thread(sheet.update, f'I{row}', [subject_to_change])


        return        
        
        




    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False