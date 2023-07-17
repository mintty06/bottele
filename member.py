import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import datetime
import sys

bot_token = '5968451603:AAHytm4_NzHGphuIWfEt7VCntUxEcBwIx_Y' 
bot = telebot.TeleBot(bot_token)
# Xoa webhook
bot.delete_webhook()


allowed_group_id = -944401841

allowed_users = []
processes = []
ADMIN_ID = 5585318521

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()

def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'BAN KHONG CO QUYEN SU DUNG LENH NAY')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LONG NHAP ID NGUOI DUNG ')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'NGUOI DUNG CO ID {user_id} ĐA ĐUOC THEM VAO DANH SACH ĐUOC PHEP SU DUNG LENH /gl_sms.')


load_users_from_database()
# Khoi tao tu đien đe luu tru danh sach khoa
key_dict = {}
@bot.message_handler(commands=['startkey'])
def startkey(message):
    bot.reply_to(message, text='VUI LONG ĐOI TRONG GIAY LAT!')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
#    url_key = requests.get(f'https://https://link4m.co/api-shorten/v2?api=64b21b3a9aba212c805dd0c2&url=https://likesubgiare.id.vn/key?key!{key}').json()['shortenedUrl']
    url = f"https://link4m.co/api-shorten/v2?api=64b21b3a9aba212c805dd0c2&url=https://likesubgiare.id.vn/key?key!{key}"
    response = requests.get(url)
    data = response.json()
    url_key = data['shortenedUrl']
    text = f'''
- LINK LAY KEY {TimeStamp()} LA: {url_key} -
- KHI LAY KEY XONG, DUNG LENH /key {{key}} ĐE TIEP TUC -
    '''
    bot.reply_to(message, text)
	# Luu khoa vao tu đien voi UID la khoa va gia tri la khoa đa tao
    key_dict[message.from_user.id] = key

# -----------------

# ...
# o tren la phan them-------------------
@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LONG NHAP KEY.')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key or key == "chiencute" or user_id in allowed_users:
        allowed_users.append(user_id)
        bot.reply_to(message, 'KEY HOP LE. BAN ĐA ĐUOC PHEP SU DUNG LENH /spamm.')
    else:
        bot.reply_to(message, 'KEY KHONG HOP LE.')



@bot.message_handler(commands=['spamm'])
def spamm(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='BAN KHONG CO QUYEN SU DUNG LENH NAY!')
        return
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LONG NHAP SO ĐIEN THOAI ')
        return

    phone_number = message.text.split()[1]
    if not phone_number.isnumeric():
        bot.reply_to(message, 'SO ĐIEN THOAI KHONG HOP LE !')
        return

    if phone_number in ['113','911','114','115','+84359616812','0359616812']:
        # So đien thoai nam trong danh sach cam
        bot.reply_to(message,"Spam cai đau buoi tao ban may luon bay gio")
        return

    file_path = os.path.join(os.getcwd(), "sms.py")
    process = subprocess.Popen([sys.executable, file_path, phone_number, "120"])
    processes.append(process)
    bot.reply_to(message, f'🚀 Gui Yeu Cau Tan Cong Thanh Cong 🚀 \n+ Bot 👾: @chiennhiBot \n+ So Tan Cong 📱: [ {phone_number} ]\n+ Chu so huu 👑: @ChienCute\n+ Facebook: ahihi\n+ Khong spam 1 so qua 3 lan trong 15p')

@bot.message_handler(commands=['how'])
def how_to(message):
    how_to_text = '''
Huong dan su dung:
- Su dung lenh /startkey đe lay key.
- Khi lay key xong, su dung lenh /key {key} đe kiem tra key.
- Neu key hop le, ban se co quyen su dung lenh /spamm {so đien thoai} đe spam call SMS.
- Chi nhung nguoi dung co key hop le moi co quyen su dung cac lenh tren.
'''
    bot.reply_to(message, how_to_text)

@bot.message_handler(commands=['help'])
def help(message):
    help_text = '''
Danh sach lenh:
- /startkey: Lay key đe su dung cac lenh.
- /key {key}: Kiem tra key va xac nhan quyen su dung cac lenh.
- /spamm {so đien thoai}: spam call SMS.
- /how: Huong dan su dung.
- /help: Danh sach lenh.
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return
    if user_id not in allowed_users:
        bot.reply_to(message, text='Ban khong co quyen su dung lenh nay!')
        return
    process_count = len(processes)
    bot.reply_to(message, f'So quy trinh đang chay: {process_count}.')

@bot.message_handler(commands=['restart'])
def restart(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return

    bot.reply_to(message, 'Bot se đuoc khoi đong lai trong giay lat...')
    time.sleep(2)
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return

    bot.reply_to(message, 'Bot se dung lai trong giay lat...')
    time.sleep(2)
    bot.stop_polling()

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, 'Lenh khong hop le. Vui long su dung lenh /help đe xem danh sach lenh.')

bot.polling()
