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


def user_info_markup(username):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Story', callback_data='cb_story'),
               InlineKeyboardButton('Post', callback_data='cb_post'),
               InlineKeyboardButton('Open in Instagram', url=f'https://www.instagram.com/{username}'))
    return markup


def user_story_markup(stories):
    markup = InlineKeyboardMarkup()

    count = len(stories)
    c = 0

    for i in range(count//5):
        markup.add(InlineKeyboardButton(f'{stories[c].media_type}-{c+1}', callback_data=f'cb_story_{c}'),
                   InlineKeyboardButton(f'{stories[c+1].media_type}-{c+2}', callback_data=f'cb_story_{c+1}'),
                   InlineKeyboardButton(f'{stories[c+2].media_type}-{c+3}', callback_data=f'cb_story_{c+2}'),
                   InlineKeyboardButton(f'{stories[c+3].media_type}-{c+4}', callback_data=f'cb_story_{c+3}'),
                   InlineKeyboardButton(f'{stories[c+4].media_type}-{c+5}', callback_data=f'cb_story_{c+4}'),
                   row_width=5)
        c += 5

    if count % 5 != 0:
        last_row = []
        for i in range(count % 5):
            c += 1
            last_row.append(InlineKeyboardButton(f'{c}', callback_data=f'cb_story_{c}'))
        markup.add(*last_row, row_width=count % 5)

    markup.add(InlineKeyboardButton('Get all', callback_data='cb_story_all'))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'cb_story':
        bot.answer_callback_query(call.id, 'Select Story')

        caption = call.message.caption
        user_id = caption[caption.find('#u')+2:]
        stories = client.user_stories(user_id)

        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_story_markup(stories))

    elif call.data == 'cb_story_all':
        bot.answer_callback_query(call.id, 'Get all Stories!')

        caption = call.message.caption
        user_id = caption[caption.find('#u')+2:]
        stories = client.user_stories(user_id)

        for story in stories:
            if story.media_type == 1:
                bot.send_photo(call.from_user.id, story.thumbnail_url)
            elif story.media_type == 2:
                bot.send_video(call.from_user.id, story.video_url)
            else:
                bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')

    elif call.data == 'cb_post':
        bot.answer_callback_query(call.id, 'Select Post')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello World')


@bot.message_handler(commands=['login'])
def bot_login(message):
    bot.send_message(message.chat.id, 'Enter USERNAME & PASSWORD')


@bot.message_handler(func=lambda message: True)
def answer_message(message):

    try:
        user_info = client.user_info_by_username(message.text)
        bot.send_photo(message.chat.id, user_info.profile_pic_url,
                       f'Username: {user_info.username}\n\nFullName: {user_info.full_name}\n\nBiography: {user_info.biography}\n\nPosts: {user_info.media_count}\n\nFollowers: {user_info.follower_count}\n\nFollowings: {user_info.following_count}\n\n#u{user_info.pk}', reply_markup=user_info_markup(user_info.username))
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')


bot.infinity_polling()
