from pprint import pprint

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from ss_utils import get_sheet_data
from cb_usd import get_exchange_rate

# Функция для изначального создания таблицы и проверки подключения к бд
def create_table():
    connection = None
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        delete_table_query = 'DROP TABLE IF EXISTS test_data'
        cursor.execute(delete_table_query)
        # 5 столбцов, id - первичный ключ
        create_table_query = '''CREATE TABLE test_data
                            (ID INT PRIMARY KEY NOT NULL,
                            ORDER_NUM           INT NOT NULL,
                            PRICE_USD       REAL,
                            SUPPLY_DATE     DATE,
                            PRICE_RUB       REAL); '''
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()
        return True

    except (Exception, Error) as error:
        print("Ошибка", error)            
        return False

# Функция для заполнения таблицы первоночальными данными из файла
def fill_data():
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        data = get_sheet_data()
        coeff = get_exchange_rate()
        insert_query = "INSERT INTO test_data(ID, ORDER_NUM, PRICE_USD, SUPPLY_DATE) VALUES(%s, %s, %s, TO_DATE(%s, 'DD.MM.YYYY'));"
        # Сначала по одному записываются данные из файла на случай некорректных типов данных
        for row in data:
            try: 
                cursor.execute(insert_query, row)
            except(Exception, Error) as error:
                print("Error trying to put values in db:", error)

        set_rub_query = f'UPDATE test_data SET PRICE_RUB = PRICE_USD * {coeff}'
        # Дальше добавляеются данные в столбец со стоимостью в рублях по курсу
        cursor.execute(set_rub_query)

        connection.commit()
        cursor.close()
        connection.close()

    except (Exception, Error) as error:
        print("Error:", error)
        data = None
    
    return data
            
# Функция для изменения данных о стоимости в рублях
def change_rub_price(exchange_rate):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        update_query = f'UPDATE test_data SET PRICE_RUB = PRICE_USD * {exchange_rate}'
        cursor.execute(update_query)

        connection.commit()

        cursor.close()
        connection.close()

    except (Exception, Error) as error:
        print("Error:", error)
        
# Функция для изменения данных в бд, когда поменялись данные в файле
def change_db_data(old_data, new_data):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        # Два словаря с id - ключами
        new_data_dict = { row[0] : (*row[1:], )  for row in new_data}
        old_data_dict = { row[0] : (*row[1:], )  for row in old_data}
        # Множества новых и старых id
        new_ids = set(new_data_dict.keys())
        old_ids = set(old_data_dict.keys())

        
        delete_ids = old_ids - new_ids
        # Удаляем те строки, id которых больше нет в файле
        if delete_ids:
            delete_query = 'DELETE FROM test_data WHERE ID = %s'
            for order_id in delete_ids:
                cursor.execute(delete_query, (order_id, ))

        insert_ids = new_ids - old_ids
        # Добавляем строки, id которых не было раньше
        if insert_ids:
            coeff = get_exchange_rate()
            insert_query = f"""INSERT INTO test_data(ID, ORDER_NUM, PRICE_USD, SUPPLY_DATE) 
                            VALUES(%s, %s, %s, TO_DATE(%s, 'DD.MM.YYYY'));"""
            set_price_query = f'UPDATE test_data SET PRICE_RUB = PRICE_USD * {coeff} WHERE ID = %s'
            for order_id in insert_ids:
                cursor.execute(insert_query, (order_id, *new_data_dict[order_id]))
                cursor.execute(set_price_query, (order_id, ))
        
        same_ids = new_ids.intersection(old_ids)
        # Для совпадающих id проверяем, поменялось ли что-нибудь
        if same_ids:
            coeff = get_exchange_rate()
            update_query = """UPDATE test_data SET 
                            ORDER_NUM = %s, PRICE_USD = %s, SUPPLY_DATE = TO_DATE(%s, 'DD.MM.YYYY')
                            WHERE ID = %s"""
            set_price_query = f'UPDATE test_data SET PRICE_RUB = PRICE_USD * {coeff} WHERE ID = %s'                
            for order_id in same_ids:
                # Если старые данные по этому id не совпадают с текущими, то меняем их в бд
                if new_data_dict[order_id] != old_data_dict[order_id]:
                    cursor.execute(update_query, (*new_data_dict[order_id], order_id))
                    cursor.execute(set_price_query, (order_id, ))

        connection.commit()

        cursor.close()
        connection.close()

    except (Exception, Error) as error:
        print("Error:", error)
            

if __name__ == '__main__':
    create_table()