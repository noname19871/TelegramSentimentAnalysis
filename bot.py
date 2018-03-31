import telebot


import Bayes
import linear

from database import DBThread
from Bayes import predict
from queue import Queue


token = '481955063:AAGwRfDppnW9FH2LeTUKb6OS9RquTbd3ijs'
bot = telebot.TeleBot(token)


def predict(msg):
    if (((Bayes.predict(msg))[0][1] > 0.5) & ((linear.predict(msg))[0][1] > 0.5)) | (((Bayes.predict(msg))[0][1] < 0.5) & ((linear.predict(msg))[0][1] < 0.5)):
        return ((Bayes.predict(msg))[0][1] + (linear.predict(msg))[0][1]) / 2
    else:
        return 0.5


work_queue = Queue()
db = DBThread(work_queue, "messages.db")
db.start()


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):

    bot.send_message(message.chat.id, predict([message.text]))
    record = (message.message_id, message.from_user.id, message.chat.id, message.from_user.username,
              message.date, message.text, predict([message.text]))
    work_queue.put(("insert", record,))



if __name__ == "__main__":
    bot.polling(none_stop=True)
