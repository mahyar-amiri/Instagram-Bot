import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config
import instagrapi
from instagrapi import Client


chat_id = config('CHAT_ID')

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

client = Client()

is_authenticated = False
while not is_authenticated:
    is_authenticated = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))

bot.send_message(chat_id, f"Hello {config('IG_USERNAME')}")

#         user_id = c.user_id_from_username('_ielts9')
#         stories = c.user_stories(user_id, 2)
#         c.logout()


def user_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Story", callback_data="cb_story"),
               InlineKeyboardButton("Post", callback_data="cb_post"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_story":
        bot.answer_callback_query(call.id, "Answer is story")
    elif call.data == "cb_post":
        bot.answer_callback_query(call.id, "Answer is post")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello World')


@bot.message_handler(commands=['login'])
def bot_login(message):
    bot.send_message(message.chat.id, 'Enter USERNAME & PASSWORD')


@bot.message_handler(func=lambda message: True)
def answer_message(message):

    try:
        user_id = client.user_id_from_username(message.text)
        bot.reply_to(message, f'User: {message.text}\nid: {user_id}', reply_markup=user_markup())
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')

    # bot.send_message(message.chat.id, message.text)

#     if list(is_waiting_for_login)[0][0]:
#         userpass = message.text

#         cursor.execute(f'UPDATE Users SET WAITING_FOR_LOGIN = 0 WHERE TG_ID = {message.chat.id};')
#         connection.commit()

#         bot.send_message(message.chat.id, f'...{userpass}...')

#     else:
#         bot.send_message(message.chat.id, message.text)


bot.infinity_polling()
