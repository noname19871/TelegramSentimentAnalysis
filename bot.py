import telebot

import Bayes
import linear

from database import DBThread
from queue import Queue
from TwitterSearch import *
from twiSearch import *

ts = TwitterSearch(
    consumer_key='2znnciYgoysnE44FErSrOCZVt',
    consumer_secret='9bzEOv6rzvVzKf7WzEqP7NXog8Y8ZxFlcqpVE59T9z2ASSDmZ4',
    access_token='979832438158446592-Ivp1hQyZyoew5whNbIm3ngZI0FmJvNz',
    access_token_secret='orqIHLtV2IPJP2JdCChfwVliooIOpNY0LnHlhucXWM7BU'
)

twi = twiSearch(ts)

token = '481955063:AAGwRfDppnW9FH2LeTUKb6OS9RquTbd3ijs'
bot = telebot.TeleBot(token)


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
    print(tonal / i)


work_queue = Queue()
db = DBThread(work_queue, "messages.db", bot)
db.start()


@bot.message_handler(commands=['search_twitter'])
def search(message):
    bot.send_message(message.chat.id, "Put tags:")
    bot.register_next_step_handler(message, process_search)


@bot.message_handler(commands=['start'])
def get_start(message):
    bot.send_message(message.chat.id, "for more information type /help")


@bot.message_handler(commands=['total_tonality'])
def get_stat(message):
    work_queue.put(("total_tonal", message.chat.id,))


@bot.message_handler(commands=['fatality'])
def get_fatality(message):
    work_queue.put(("fatality", message.chat.id))


# TODO callback for argument
@bot.message_handler(commands=['user_tonality'])
def get_user_tonality(message):
    work_queue.put(("user_tonality", message,))


@bot.message_handler(commands=['users_tonality'])
def get_users_tonality(message):
    work_queue.put(("users_tonality", message,))


@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, '/start - start_bot\n' \
                                      '/total_tonality - get total tonality\n' \
                                      '/fatality - clear database\n' \
                                      '/user_tonality - get user tonality\n' \
                                      '/users_tonality - get all users tonality\n' \
                                      '/help - get help\n' \
                                      '/stop - stop bot')


@bot.message_handler(commands=['stop'])
def get_stop(message):
    work_queue.put(("stop", message.chat.id,))


@bot.message_handler(content_types=["text"])
def insert_message(message):
    record = (message.message_id, message.from_user.id, message.chat.id, message.from_user.username,
              message.date, message.text, str((predict([message.text]))))
    print(record)
    work_queue.put(("insert", record,))


if __name__ == "__main__":
    bot.polling(none_stop=True)
