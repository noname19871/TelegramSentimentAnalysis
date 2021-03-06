import telebot
import sqlite3 as lite

import Bayes
import linear
import config

from queue import Queue
from twiSearch import twiSearch
from database import COLUMNS



twi = twiSearch(config.ts)

bot = telebot.TeleBot(config.token)

def get_st(message):
    db = lite.connect('message.db')
    command = "SELECT sum(tonal), count(tonal) FROM {} WHERE username='{}'".format('messages', message.text)
    c = db.cursor()

    user_from_db = c.execute(command)
    user = ([u for u in user_from_db])[0]
    if user[0] is None:
        bot.send_message(message.chat.id, "Такого пользователя нет в данном чате")
        return
    if not user[1] == 0:
        tonal = user[0] / user[1]
    else:
        tonal = 0.5
    bot.send_message(message.chat.id, "@{} - {}".format(message.text, tonal))
    db.close()

def predict(msg):
    if (((Bayes.predict(msg))[0][1] > 0.5) & ((linear.predict(msg))[0][1] > 0.5)) | (
            ((Bayes.predict(msg))[0][1] < 0.5) & ((linear.predict(msg))[0][1] < 0.5)):
        return ((Bayes.predict(msg))[0][1] + (linear.predict(msg))[0][1]) / 2
    else:
        return 0.5


def process_search(message):
    search = twi.search(list(message.text))
    tonal = 0
    i = 0
    for tweet in search:
        if not i == 5:
            tonal += (predict([tweet['text']]))
            print(i, " - ", tweet['text'])
            i += 1


work_queue = Queue()
# db = DB("messages.db")




@bot.message_handler(commands=['search_twitter'])
def search(message):
    bot.send_message(message.chat.id, "coming soon")
    # bot.register_next_step_handler(message, process_search)


@bot.message_handler(commands=['start'])
def get_start(message):
    db = lite.connect('message.db')
    c = db.cursor()
    create = "CREATE TABLE IF NOT EXISTS {} {}".format('messages', COLUMNS)
    c.execute(create)
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "for more information type /help")


@bot.message_handler(commands=['total_tonality'])
def get_stat(message):
    if message.from_user.id in config.admins:
        db = lite.connect('message.db')
        command = "SELECT sum(tonal), count(tonal) FROM {}".format('messages')
        c = db.cursor()
        stat = c.execute(command)
        stat = ([i for i in stat])[0]
        if not stat[1] == 0:
            tonal = stat[0] / stat[1]
        else:
            tonal = 0.5
        bot.send_message(message.chat.id, "Total tonality = {}".format(tonal))
        db.commit()
        db.close()
    else:
        bot.send_message(message.chat.id, 'you are not in admins list')


@bot.message_handler(commands=['fatality'])
def get_fatality(message):
    if message.from_user.id in config.admins:
        db = lite.connect('message.db')
        c = db.cursor()
        command = "DROP TABLE {}".format('messages')
        c.execute(command)
        command = "CREATE TABLE IF NOT EXISTS {} {}".format('messages', COLUMNS)
        c.execute(command)
        db.commit()
        db.close()
    else:
        bot.send_message(message.chat.id, 'you are not in admins list')


# TODO callback for argument
@bot.message_handler(commands=['user_tonality'])
def get_user_tonality(message):
    if message.from_user.id in config.admins:
        bot.send_message(message.chat.id, "Put username:")
        bot.register_next_step_handler(message, get_st)
    else:
        bot.send_message(message.chat.id, 'you are not in admins list')


@bot.message_handler(commands=['users_tonality'])
def get_users_tonality(message):
    if message.from_user.id in config.admins:
        db = lite.connect('message.db')
        c = db.cursor()
        str = "Статистика по пользователям:\n"
        command = "SELECT username, sum(tonal), count(tonal) FROM {} GROUP BY username".format('messages')
        users_from_db = c.execute(command)
        users = [u for u in users_from_db]
        users_tonal = []
        for user in users:
            if not user[2] == 0:
                tonal = user[1] / user[2]
            else:
                tonal = 0.5
            users_tonal.append((user[0], tonal,))
        for (i, user) in zip(range(1, len(users) + 1), sorted(users_tonal, key=lambda x: x[1], reverse=True)):
            str = "{}{} - @{}  {}\n".format(str, i, user[0], user[1])

        bot.send_message(message.chat.id, str)
        db.commit()
        db.close()
    else:
        bot.send_message(message.chat.id, 'you are not in admins list')



@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, '/start - start_bot\n' \
                                      '/total_tonality - get total tonality\n' \
                                      '/fatality - clear database\n' \
                                      '/user_tonality - get user tonality\n' \
                                      '/users_tonality - get all users tonality\n' \
                                      '/help - get help\n' \
                                      '/stop - stop bot')


# @bot.message_handler(commands=['stop'])
# def get_stop(message):
#     if message.from_user.id in config.admins:
#         work_queue.put(("stop", message.chat.id,))
#     else:
#         bot.send_message(message.chat.id, 'you are not in admins list')


@bot.message_handler(content_types=["text"])
def insert_message(message):
    db = lite.connect('message.db')
    record = (message.message_id, message.from_user.id, message.chat.id, message.from_user.username,
              message.date, message.text, str((predict([message.text]))))
    command = "insert into {} values {}".format('messages', record)
    c = db.cursor()
    c.execute(command)
    db.commit()
    db.close()


if __name__ == "__main__":
        try:
            bot.polling(none_stop=True)
        except:
            print("произошла какая-то ошибка")