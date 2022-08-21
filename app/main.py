from pprint import pprint
from time import sleep

from cb_usd import get_exchange_rate
from db_utils import create_table, fill_data, change_rub_price, change_db_data
from ss_utils import service_sheets, service_drive, spreadsheet_id, get_last_revision_id, get_sheet_data

# Функция для первого запуска и подключения к файлу 
def startup():
    is_connected = create_table()
    while not is_connected:
        is_connected = create_table()
        sleep(10)

# Функция, осталеживающая изменения курса и изменения в файле
def main():
    current_data = fill_data()

    revision_id = get_last_revision_id()
    exchange_rate = get_exchange_rate()

    while True:
        new_revision_id = get_last_revision_id()
        # Проверка изменения id последней версии
        if new_revision_id and new_revision_id != revision_id:
            revision_id = new_revision_id
            old_data = current_data
            current_data = get_sheet_data()
            print('change happend')
            change_db_data(old_data, current_data)


        new_exchange_rate = get_exchange_rate()
        # Проверка изменения курса
        if new_exchange_rate and new_exchange_rate != exchange_rate:
            exchange_rate = new_exchange_rate
            print('exchange rate changed')
            change_rub_price(exchange_rate)

        sleep(2)

# Запуск
if __name__ == '__main__':
    startup()
    main()