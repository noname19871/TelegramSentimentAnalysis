import telebot

from Bayes import predict

token = '407983248:AAGoNA--4lrX7FuflwW47Q7Z1Kdh83CMGBo'

bot = telebot.TeleBot(token)
data = []


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id,str(predict([message.text])[0][0]))


bot.polling(none_stop=True)