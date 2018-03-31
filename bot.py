import telebot

import Bayes
import linear

token = '407983248:AAGoNA--4lrX7FuflwW47Q7Z1Kdh83CMGBo'

bot = telebot.TeleBot(token)


def predict(msg):
    if (((Bayes.predict(msg))[0][1] > 0.5) & ((linear.predict(msg))[0][1] > 0.5)) | (((Bayes.predict(msg))[0][1] < 0.5) & ((linear.predict(msg))[0][1] < 0.5)):
        return ((Bayes.predict(msg))[0][1] + (linear.predict(msg))[0][1]) / 2
    else:
        return 0.5


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, predict([message.text]))


bot.polling(none_stop=True)