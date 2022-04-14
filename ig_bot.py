import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config
import instagrapi
from instagrapi import Client


chat_id = config('CHAT_ID')

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

client = Client()

EMOJI = {
    'username': '👤',
    'name': '🗣️',
    'bio': '📜',
    'post': '🖼️',
    'follower': '👥',
    'following': '🫂',
    'private': '🔒',
    'public': '🔓',
    'verified': '✅',
    'notverified': '❎',
    'url': '🌐',
    'video': '🎞️',
    'photo': '🖼️',
    'notsupport': '❌',
    'download': '📥',
    'upload': '📤',
    'back': '🔙',
}

is_authenticated = False
while not is_authenticated:
    is_authenticated = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))


bot.send_message(chat_id, f"Hello {config('IG_USERNAME')}")


def user_info_markup(pk):
    username = client.user_info(pk).username
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
        row = []
        for j in range(5):
            media_type = ''
            if stories[c].media_type == 1:
                media_type = EMOJI['photo']
            elif stories[c].media_type == 2:
                media_type = EMOJI['video']
            else:
                media_type = EMOJI['notsupport']

            row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_story_dl_{c}'))
            c += 1

        markup.add(*row, row_width=5)

    if count % 5 != 0:
        last_row = []
        for i in range(count % 5):
            media_type = ''
            if stories[c].media_type == 1:
                media_type = EMOJI['photo']
            elif stories[c].media_type == 2:
                media_type = EMOJI['video']
            else:
                media_type = EMOJI['notsupport']

            last_row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_story_dl_{c}'))
            c += 1
        markup.add(*last_row, row_width=count % 5)

    markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data='cb_story_all'))
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_story_back'))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    caption = call.message.caption
    user_id = caption[caption.find('#u')+2:]

    if call.data == 'cb_story':

        stories = client.user_stories(user_id)

        if len(stories) == 0:
            bot.answer_callback_query(call.id, 'User has no story!')
        else:
            bot.answer_callback_query(call.id, 'Select Story')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_story_markup(stories))

    elif call.data == 'cb_story_back':
        bot.answer_callback_query(call.id, 'Back to user info!')
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_info_markup(user_id))

    elif call.data.startswith('cb_story_dl_'):
        number = int(call.data.replace('cb_story_dl_', ''))

        bot.answer_callback_query(call.id, f'Get Story {number+1}!')

        stories = client.user_stories(user_id)

        story = stories[number]
        if story.media_type == 1:
            bot.send_photo(call.from_user.id, story.thumbnail_url, caption=f'Story Number: {number+1}\n#u{user_id}')
        elif story.media_type == 2:
            bot.send_video(call.from_user.id, story.video_url, caption=f'Story Number: {number+1}\n#u{user_id}')
        else:
            bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')

    elif call.data == 'cb_story_all':
        bot.answer_callback_query(call.id, 'Get all Stories!')

        stories = client.user_stories(user_id)

        for number, story in enumerate(stories):
            if story.media_type == 1:
                bot.send_photo(call.from_user.id, story.thumbnail_url, caption=f'Story Number: {number+1}\n#u{user_id}')
            elif story.media_type == 2:
                bot.send_video(call.from_user.id, story.video_url, caption=f'Story Number: {number+1}\n#u{user_id}')
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
                       f'''
                       {EMOJI['username']} Username: {user_info.username}
                       {EMOJI['name']} FullName: {user_info.full_name}
                       {EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}
                       {EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} Verify: {'Verified' if user_info.is_verified else 'Not Verified'}
                       {EMOJI['bio']} Biography: {user_info.biography}
                       {EMOJI['post']} Posts: {user_info.media_count}
                       {EMOJI['follower']} Followers: {user_info.follower_count:,}
                       {EMOJI['following']} Followings: {user_info.following_count:,}
                       {EMOJI['url']} URL: {user_info.external_url}
                       #u{user_info.pk}
                       '''.replace('                       ', '\n'), reply_markup=user_info_markup(user_info.pk))
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')


bot.infinity_polling(skip_pending=True)
