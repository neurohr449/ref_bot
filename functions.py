import os
import gspread
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
            video_10=row_data[19],
            )