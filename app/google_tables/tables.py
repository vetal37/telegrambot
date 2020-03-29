# Подключаем библиотеки
import httplib2 
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from app.models import Teacher, Tables
import datetime
import time


CREDENTIALS_FILE = 'woven-environs-272314-a2f4d17f757a.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

def get_spreadsheet_id_from_database(): #TODO: variables for method
    link = Tables.url
    splitted = link.split("https://docs.google.com/spreadsheets/d/")
    link = splitted[1]
    splitted = link.split("/edit#gid=")
    spreadsheet_id = splitted[0]
    return spreadsheet_id

def get_link_id_from_database(): #TODO: variables for method
    link = Tables.url
    splitted = link.split("https://docs.google.com/spreadsheets/d/")
    link = splitted[1]
    splitted = link.split("/edit#gid=")
    list_id = int(splitted[1])
    return list_id


spreadsheet_id = get_spreadsheet_id_from_database()
list_id = get_link_id_from_database()

def get_sheet_name(spreadsheet_id, list_id):
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheet_id).execute()
    sheetList = spreadsheet.get('sheets')
    for sheet in sheetList:
        if sheet['properties']['sheetId'] == list_id:
            return sheet['properties']['title']


list_name = get_sheet_name(spreadsheet_id, list_id)
ranges_name = [list_name + "!A2:A40"]

results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheet_id, 
                                                   ranges = ranges_name, 
                                                   valueRenderOption = 'FORMATTED_VALUE',  
                                                   dateTimeRenderOption = 'FORMATTED_STRING').execute()
sheet_counter = len(results['valueRanges'][0]['values'])

ranges = {
    "range":
    {
        "sheetId": list_id,
        "startRowIndex": 1, # Со строки номер startRowIndex 
        "endRowIndex": sheet_counter,# по endRowIndex - 1 (endRowIndex не входит!)
        "startColumnIndex": 0, # Со столбца номер startColumnIndex 
        "endColumnIndex": 1 # по endColumnIndex - 1
    }}

def fill_in_date_in_table(spreadsheet_id, list_id, list_name):
    ranges = [list_name + "!A1:AAA1"]
    results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheet_id, 
                                                   ranges = ranges_name, 
                                                   valueRenderOption = 'FORMATTED_VALUE',  
                                                   dateTimeRenderOption = 'FORMATTED_STRING').execute()
    sheet_counter = len(results['valueRanges'][0]['values'])
    alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    for letter in alphabet:
        if sheet_counter < 27:
            cell_name = letter[sheet_counter]
        elif:
            cell_name = letter[sheet_counter // 26] + letter[sheet_counter % 26]
    cell_name = cell_name + "1"
    ranges = [list_name + "!" + cell_name]    
    date_input = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = {
                    "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                    "data": [
                            {"range": ranges,
                            "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                            "values": [time.strftime("%d.%m.%Y", datetime.date.today())]}
    ]
    }).execute()
    
