from time import sleep, time
import threading
import datetime

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import telebot
import pytz

# Токен телеграм бота и создание объекта TeleBot
TOKEN = "5522597576:AAHsn0qdvClGL_7sCy3Q44cEyKQg_JxusUI"
bot = telebot.TeleBot(TOKEN)

# Установка часового пояса для отслеживания времени
tz = pytz.timezone('Europe/Moscow')

# Файл для записи chat_id всех пользователей бота
with open('users.txt', 'r') as file:
    users = [int(chat_id.strip()) for chat_id in file.readlines()]

# обработчик команды /start ил /go, сохранение chat_id пользователя
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users.append(chat_id)
        with open('users.txt', 'a') as file:
            file.write(str(chat_id) + '\n')
    msg = bot.send_message(chat_id, 'Теперь Вы подписаны на уведомления о ближайших поставках')

# Функция для получения сегодняшних и ближайших поставок
def check_messages(date):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        date_today = date.strftime("%Y-%m-%d")

        select_today_query = f"SELECT * FROM test_data WHERE SUPPLY_DATE = '{date_today}';"
        cursor.execute(select_today_query)
        supply_today = cursor.fetchall()

        date_week1 = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        date_week2 = (date + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        select_near_query = f"SELECT * FROM test_data WHERE SUPPLY_DATE BETWEEN '{date_week1}' AND '{date_week2}';"
        cursor.execute(select_near_query)
        supply_near = cursor.fetchall()


        print(supply_today, supply_near)
        connection.commit()

        if connection:
            cursor.close()
            connection.close() 

    except (Exception, Error) as error:
        print("Error:", error)
        supply_today = None
        supply_near = None
    
    return supply_today, supply_near

# Функция для проверки текущего времени и отправки сообщений о поставках в нужное время
def send_notifications():
    while True:
        if str (datetime.datetime.now(tz).strftime("%H")) == "10":
            date = datetime.datetime.now(tz)
            supply_today, supply_near = check_messages(date)
            if supply_today:
                text = ''
                for supply in supply_today:
                    text += f'id - {supply[0]}, № заказа - {supply[1]}, стоимость - {supply[2]}\n\n'
                for user_id in users:
                    bot.send_message(user_id, 'Поставки сегодня:')
                    bot.send_message(user_id, text)
            if supply_near:
                text = ''
                for supply in supply_near:
                    text += f'id - {supply[0]}, № заказа - {supply[1]}, дата - {supply[3].strftime("%d.%m.%Y")}, стоимость - {supply[2]}\n\n'
                for user_id in users:
                    bot.send_message(user_id, 'Поставки в течение недели:')
                    bot.send_message(user_id, text)
            sleep(65 * 60)
        sleep(60)

# Запуск отслеживания дат поставок
t = threading.Thread(target=send_notifications)
t.start()

# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)  
        except Exception as e:
            sleep(3)
            print(e)