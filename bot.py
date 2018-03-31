import telebot
from database import DB, DBThread
from Bayes import predict
from queue import Queue

token = '481955063:AAGwRfDppnW9FH2LeTUKb6OS9RquTbd3ijs'
bot = telebot.TeleBot(token)
work_queue = Queue()
db = DBThread(work_queue, "messages.db", bot)
db.start()


@bot.message_handler(commands=['statistics'])
def get_stat(message):
    bot.send_message(message.chat.id, "Total tonal: ")
    work_queue.put(("total_tonal", message.chat.id,))


@bot.message_handler(content_types=["text"])
def insert_message(message):
    record = (message.message_id, message.from_user.id, message.chat.id, message.from_user.username,
              message.date, message.text, (predict([message.text]))[0][1])
    work_queue.put(("insert", record,))


if __name__ == "__main__":
    bot.polling(none_stop=True)
