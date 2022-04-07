import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config


chat_id = config('CHAT_ID')

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

client = Client()
client.login(config('USERNAME'),  config('PASSWORD'))


# bot.send_message(chat_id, 'Hello World')
# def instagram_view(request):
#     if request.user.is_authenticated:
#         user = request.user

#         c = Client()
#         c.login(user.username, user.pass_word)

#         user_id = c.user_id_from_username('_ielts9')
#         stories = c.user_stories(user_id, 2)

#         c.logout()

#         context = {'stories': stories}

#         return render(request, 'instagram.html', context=context)

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
    bot.send_message(message.chat.id, message.text, reply_markup=user_markup())

#     is_waiting_for_login = cursor.execute(f'SELECT WAITING_FOR_LOGIN FROM Users WHERE TG_ID = {message.chat.id};')

#     if list(is_waiting_for_login)[0][0]:
#         userpass = message.text

#         cursor.execute(f'UPDATE Users SET WAITING_FOR_LOGIN = 0 WHERE TG_ID = {message.chat.id};')
#         connection.commit()

#         bot.send_message(message.chat.id, f'...{userpass}...')

#     else:
#         bot.send_message(message.chat.id, message.text)


bot.infinity_polling()
