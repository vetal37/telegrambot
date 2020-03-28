# Подключаем библиотеки
import httplib2 
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from app.models import Teacher, Table
CREDENTIALS_FILE = 'woven-environs-272314-a2f4d17f757a.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])


def get_spreadsheet_id_from_database():
    link = Table.url
    splitted = link.split("https://docs.google.com/spreadsheets/d/")
    link = splitted[1]
    splitted = link.split("/edit#gid=")
    spreadsheet_id = splitted[0]
    list_id = int(splitted[1])
    return spreadsheet_id


def get_link_id_from_database():
    link = Table.url
    splitted = link.split("https://docs.google.com/spreadsheets/d/")
    link = splitted[1]
    splitted = link.split("/edit#gid=")
    list_id = int(splitted[1])
    return list_id


spreadsheet_id = get_spreadsheet_id_from_database()
list_id = get_link_id_from_database()

results = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()