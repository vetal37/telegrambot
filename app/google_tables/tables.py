# Подключаем библиотеки
import httplib2 
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from app.models import Teacher, Tables


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

ranges_id = "Лист1" + "!A2:A40"

results = service.spreadsheets().values().batchGet(spreadsheetId = "1sZUcqBWCswPwbUVH2Lt0X4toJp4DbPbWAtRC_TXV6Lg", 
                                                   ranges = ranges_id, 
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

