import telebot
from database import DB, DBThread
from Bayes import predict
from queue import Queue

token = '481955063:AAGwRfDppnW9FH2LeTUKb6OS9RquTbd3ijs'
bot = telebot.TeleBot(token)
work_queue = Queue()
db = DBThread(work_queue, "messages.db")
db.start()


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, str(predict([message.text])[0][1]))
    record = (message.message_id, message.from_user.id, message.chat.id, message.from_user.username,
              message.date, message.text, predict([message.text])[0][1])
    work_queue.put(("insert", record,))


if __name__ == "__main__":
    bot.polling(none_stop=True)
