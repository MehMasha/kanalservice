from pprint import pprint
from time import sleep

import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError

# Вся работа с Google Sheets

CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа
spreadsheet_id = '1Ws3w92bQxSA-EWqaopwAjTiT1d7gXowf7g09ekOwaHY'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service_sheets = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
service_drive = apiclient.discovery.build('drive', 'v3', http=httpAuth)

# Получение id последнего изменения с помощью google drive
def get_last_revision_id():
    try:
        # Последовательный перебор всех страниц с изменениями, пока не будет достигнута последняя
        response = service_drive.revisions().list(fileId=spreadsheet_id).execute()
        page_token = response.get('nextPageToken')      
        while page_token is not None:
            response = service_drive.revisions().list(pageToken=page_token, fileId=spreadsheet_id).execute()
            page_token = response.get('nextPageToken')
        current_id = response['revisions'][-1]['id'] 

    except HttpError as error:
        print(F'An error occurred: {error}')
        current_id = None

    return current_id

# Функция для чтения всех данных из файла
def get_sheet_data():
    try:
        data = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='List1',
            majorDimension='ROWS'
        ).execute()
        data = data['values'][1:]
        # Преобразование в кортеж кортежей, все короткие и неполные строки отбрасываются, 
        # как и все то, что находится в других столбцах документа
        data = tuple((*row[:4], ) for row in data if len(row) >= 4 and '' not in row[:4])
        # print(data)
    except HttpError as error:
        print(F'An error occurred: {error}')
        data = None
    return data


if __name__ == '__main__':
    print(get_last_revision_id())
    print(get_sheet_data())
