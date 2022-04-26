import signal
from decouple import config

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import instagrapi
from instagrapi import Client

chat_id = config('CHAT_ID')

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

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
    'album': '🖼️🎞️',
    'notsupport': '❌',
    'download': '📥',
    'upload': '📤',
    'back': '🔙',
}

# CREATE AND LOGIN WITH CLIENT
client = Client()

try:
    print(f"[INFO] Try to login as {config('IG_USERNAME')}")
    client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))
    print(f"[INFO] Successfully logged in as {config('IG_USERNAME')}")

except instagrapi.exceptions.PleaseWaitFewMinutes as e:
    print(f'[INFO] Error')
    exit(1)


# ASK BEFORE EXIT AND LOGOUT
def exit_handler(signum, frame):
    res = input("\n Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        client.logout()
        exit(1)


signal.signal(signal.SIGINT, exit_handler)

# SEND START MESSAGE
bot.send_message(chat_id, f"Hello {config('IG_USERNAME')}")


def user_info_markup(pk):
    username = client.user_info(pk).username
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Story', callback_data='cb_story'),
               InlineKeyboardButton('Post', callback_data='cb_post'),
               InlineKeyboardButton('Highlight', callback_data='cb_highlight'),
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
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


def user_post_markup(posts):
    markup = InlineKeyboardMarkup()

    count = len(posts)
    c = 0

    for i in range(count//3):
        row = []
        for j in range(3):
            media_type = ''
            if posts[c].media_type == 1:
                media_type = EMOJI['photo']
            elif posts[c].media_type == 2:
                media_type = EMOJI['video']
            elif posts[c].media_type == 8:
                media_type = EMOJI['album']
            else:
                media_type = EMOJI['notsupport']

            row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_post_dl_{c}'))
            c += 1

        markup.add(*row, row_width=3)

    if count % 3 != 0:
        last_row = []
        for i in range(count % 3):
            media_type = ''
            if posts[c].media_type == 1:
                media_type = EMOJI['photo']
            elif posts[c].media_type == 2:
                media_type = EMOJI['video']
            elif posts[c].media_type == 8:
                media_type = EMOJI['album']
            else:
                media_type = EMOJI['notsupport']

            last_row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_post_dl_{c}'))
            c += 1
        markup.add(*last_row, row_width=count % 3)

    markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data='cb_post_all'))
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


def user_highlight_markup(highlights):
    markup = InlineKeyboardMarkup()

    count = len(highlights)
    c = 0

    for i in range(count//5):
        row = []
        for j in range(5):
            row.append(InlineKeyboardButton(f'{highlights[c].title}', callback_data=f'cb_highlight_dl_{highlights[c].pk}'))
            c += 1

        markup.add(*row, row_width=5)

    if count % 5 != 0:
        last_row = []
        for i in range(count % 5):
            last_row.append(InlineKeyboardButton(f'{highlights[c].title}', callback_data=f'cb_highlight_dl_{highlights[c].pk}'))
            c += 1
        markup.add(*last_row, row_width=count % 5)

    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    caption = call.message.caption
    user_id = caption[caption.find('#u')+2:]

    if call.data == 'cb_back':
        bot.answer_callback_query(call.id, 'Back to user info!')
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_info_markup(user_id))

    # Story
    elif call.data == 'cb_story':
        stories = client.user_stories(user_id)

        if len(stories) == 0:
            bot.answer_callback_query(call.id, 'User has no story!')
        else:
            bot.answer_callback_query(call.id, 'Select Story')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_story_markup(stories))

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

    # Post
    elif call.data == 'cb_post':
        posts = client.user_medias(user_id, 9)

        if len(posts) == 0:
            bot.answer_callback_query(call.id, 'User has no post!')
        else:
            bot.answer_callback_query(call.id, 'Select Post')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_post_markup(posts))

    elif call.data.startswith('cb_post_dl_'):
        number = int(call.data.replace('cb_post_dl_', ''))
        bot.answer_callback_query(call.id, f'Get Post {number+1}!')

        posts = client.user_medias(user_id, number+1)

        post = posts[number]
        if post.media_type == 1:
            bot.send_photo(call.from_user.id, post.thumbnail_url, caption=f'{post.caption_text}\n\nLikes: {post.like_count}\nComments: {post.comment_count}\n\nPost Number: {number+1}\n#u{user_id}')
        elif post.media_type == 2:
            bot.send_video(call.from_user.id, post.video_url, caption=f'{post.caption_text}\n\nLikes: {post.like_count}\nComments: {post.comment_count}\nViews: {post.view_count}\n\nPost Number: {number+1}\n#u{user_id}')
        elif post.media_type == 8:
            for slide_num, resource in enumerate(post.resources):
                if resource.media_type == 1:
                    bot.send_photo(call.from_user.id, resource.thumbnail_url, caption=f'{post.caption_text}\n\nLikes: {post.like_count}\nComments: {post.comment_count}\n\nPost Number: {number+1}\nSlide: {slide_num+1}\n#u{user_id}')
                elif resource.media_type == 2:
                    bot.send_video(call.from_user.id, resource.video_url, caption=f'{post.caption_text}\n\nLikes: {post.like_count}\nComments: {post.comment_count}\n\nPost Number: {number+1}\nSlide: {slide_num+1}\n#u{user_id}')

        else:
            bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')

    # Highlight
    elif call.data == 'cb_highlight':
        highlights = client.user_highlights(user_id)

        if len(highlights) == 0:
            bot.answer_callback_query(call.id, 'User has no highlight!')
        else:
            bot.answer_callback_query(call.id, 'Select Highlight')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_highlight_markup(highlights))

    elif call.data.startswith('cb_highlight_dl_'):
        highlight_pk = int(call.data.replace('cb_highlight_dl_', ''))

        highlight = client.highlight_info(highlight_pk)

        bot.answer_callback_query(call.id, f'Select Story from Highlight!')
        print(highlight, '*\n'*5, highlight.items)
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_story_markup(highlight.items))


@bot.inline_handler(lambda query: len(query.query) != 0)
def inline_query(query):
    try:
        try:
            user_info = client.user_info_by_username(query.query)
            r = types.InlineQueryResultPhoto('1', user_info.profile_pic_url, user_info.profile_pic_url, title=f'{user_info.username}', description=f'{user_info.full_name}',
                                             caption=f'''
                                             {EMOJI['username']} Username: {user_info.username}
                                             {EMOJI['name']} FullName: {user_info.full_name}
                                             {EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}
                                             {EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} Verify: {'Verified' if user_info.is_verified else 'Not Verified'}
                                             {EMOJI['bio']} Biography: {user_info.biography}
                                             {EMOJI['post']} Posts: {user_info.media_count}
                                             {EMOJI['follower']} Followers: {user_info.follower_count:,}
                                             {EMOJI['following']} Followings: {user_info.following_count:,}
                                             {EMOJI['url']} URL: {user_info.external_url if user_info.external_url else ''}
                                             #u{user_info.pk}
                                             '''.replace('                                             ', '\n'))

        except instagrapi.exceptions.UserNotFound as e:
            r = types.InlineQueryResultArticle('1', f'Not Found', input_message_content=types.InputTextMessageContent(query.query))

        bot.answer_inline_query(query.id, [r])

    except Exception as e:
        print(e)


@ bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello World')


@ bot.message_handler(commands=['login'])
def bot_login(message):
    is_logged_in = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))
    bot.send_message(message.chat.id, f"{'Logged in' if is_logged_in else 'Can not log in'}")


@ bot.message_handler(commands=['logout'])
def bot_login(message):
    is_logged_out = client.logout()
    bot.send_message(message.chat.id, f"{'Logged out' if is_logged_out else 'Can not log out'}")


@ bot.message_handler(func=lambda message: True)
def answer_message(message):

    try:
        if message.text.startswith('eval '):
            bot.reply_to(message, f'{eval(message.text[5:])}')
        else:
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
                        {EMOJI['url']} URL: {user_info.external_url if user_info.external_url else ''}
                        #u{user_info.pk}
                        '''.replace('                       ', '\n'), reply_markup=user_info_markup(user_info.pk))
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')


bot.infinity_polling(skip_pending=True)
