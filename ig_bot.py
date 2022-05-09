import signal
import threading
from time import sleep
from decouple import config
from datetime import datetime as dt

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import instagrapi
from instagrapi import Client


TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

EMOJI = {
    'username': '👤',
    'name': '🗣️',
    'bio': '📜',
    'time': '⏰',
    'date': '🗓️',
    'post': '🖼️',
    'follower': '👥',
    'following': '🫂',
    'private': '🔒',
    'public': '🔓',
    'verified': '✅',
    'notverified': '❎',
    'url': '🌐',
    'like': '❤️',
    'comment': '💬',
    'view': '👁️‍🗨️',
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
bot.send_message(config('CHAT_ID'), f"Hello {config('IG_USERNAME')}")


# KEYBOARD MARKUP GENERATOR
def IKMGenerator(items: list, row_width: int, callback: str, btn_get_all: bool = False, btn_back: bool = True, highlight_pk: int = None):
    keyboard_markup = InlineKeyboardMarkup()

    count = len(items)
    c = 0

    for i in range(count//row_width):
        row = []
        for j in range(row_width):
            if callback in ['story', 'post']:
                media_type = ''
                if items[c].media_type == 1:
                    media_type = EMOJI['photo']
                elif items[c].media_type == 2:
                    media_type = EMOJI['video']
                elif items[c].media_type == 8:
                    media_type = EMOJI['album']
                else:
                    media_type = EMOJI['notsupport']

                row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_{callback}_dl_{items[c].pk}'))

            elif callback == 'highlight':
                row.append(InlineKeyboardButton(items[c].title, callback_data=f'cb_{callback}_dl_{items[c].pk}'))

            c += 1

        keyboard_markup.add(*row, row_width=row_width)

    if count % row_width != 0:
        last_row = []
        for i in range(count % row_width):
            if callback in ['story', 'post']:
                media_type = ''
                if items[c].media_type == 1:
                    media_type = EMOJI['photo']
                elif items[c].media_type == 2:
                    media_type = EMOJI['video']
                elif items[c].media_type == 8:
                    media_type = EMOJI['album']
                else:
                    media_type = EMOJI['notsupport']

                last_row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_{callback}_dl_{items[c].pk}'))

            elif callback == 'highlight':
                last_row.append(InlineKeyboardButton(items[c].title, callback_data=f'cb_{callback}_dl_{items[c].pk}'))

            c += 1
        keyboard_markup.add(*last_row, row_width=count % row_width)

    if btn_get_all:
        if highlight_pk is not None:
            keyboard_markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data=f'cb_{callback}_all_{highlight_pk}'))
        else:
            keyboard_markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data=f'cb_{callback}_all'))
    if btn_back:
        keyboard_markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return keyboard_markup


def user_info_markup(pk):
    username = client.user_info(pk).username
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Story', callback_data='cb_story'),
               InlineKeyboardButton('Post', callback_data='cb_post'),
               InlineKeyboardButton('Highlight', callback_data='cb_highlight'),
               row_width=3)

    markup.add(InlineKeyboardButton('Send in Telegram', switch_inline_query=username),
               InlineKeyboardButton('Open in Instagram', url=f'https://www.instagram.com/{username}'))
    return markup


def send_group_files(chat_id, files_list):
    start = 0
    count = 10
    while start < len(files_list):
        files = files_list[start:start+count]
        try:
            bot.send_media_group(chat_id, files)
            sleep(0.3)
            start += count
            count = 10
        except:
            count -= 1


def send_story(chat_id, story_pk):
    story = client.story_info(story_pk)
    story_caption = f"{EMOJI['username']} {story.user.username}\n{EMOJI['date']} {dt.strftime(story.taken_at, '%A - %d %B %Y')}\n{EMOJI['time']} {dt.strftime(story.taken_at, '%H:%M')}\n\n#u{story.user.pk}"
    if story.media_type == 1:
        bot.send_photo(chat_id, story.thumbnail_url, caption=story_caption)
    elif story.media_type == 2:
        bot.send_video(chat_id, story.video_url, caption=story_caption)
    else:
        bot.send_message(chat_id, 'FORMAT NOT FOUND!')


def send_media(chat_id, media_pk):
    post = client.media_info(media_pk)

    try:
        post_views = f"{EMOJI['view']} {post.view_count:,}\n" if post.media_type == 2 else ''
        post_taken_at = f"{EMOJI['date']} {dt.strftime(post.taken_at, '%A - %d %B %Y')}\n{EMOJI['time']} {dt.strftime(post.taken_at, '%H:%M')}"
        post_caption = f"{post.caption_text}\n\n{EMOJI['username']} {post.user.username}\n{post_taken_at}\n{EMOJI['like']} {post.like_count:,}\n{EMOJI['comment']} {post.comment_count:,}\n{post_views}\n#u{post.user.pk}"
        if post.media_type == 1:
            bot.send_photo(chat_id, post.thumbnail_url, caption=post_caption)
        elif post.media_type == 2:
            bot.send_video(chat_id, post.video_url, caption=post_caption)
        elif post.media_type == 8:

            slides_list = []
            for slide_num, resource in enumerate(post.resources):
                caption = post_caption if slide_num == 0 else None
                if resource.media_type == 1:
                    slides_list.append(types.InputMediaPhoto(resource.thumbnail_url, caption=caption))
                elif resource.media_type == 2:
                    slides_list.append(types.InputMediaVideo(resource.video_url, caption=caption))

            send_group_files(chat_id, slides_list)

        else:
            bot.send_message(chat_id, 'FORMAT NOT FOUND!')

    except:
        bot.send_message(chat_id, 'CAN NOT UPLOAD LARGE MEDIA!')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    caption = call.message.caption
    user_id = caption[caption.find('#u')+2:]

    if call.data == 'cb_back':
        bot.answer_callback_query(call.id, 'Back to user info!')
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=user_info_markup(user_id))

    # Story
    elif call.data == 'cb_story':
        stories = client.user_stories(user_id)
        if len(stories) == 0:
            bot.answer_callback_query(call.id, 'User has no story!')
        else:
            bot.answer_callback_query(call.id, 'Select Story')
            bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=IKMGenerator(stories, 5, 'story', True))

    elif call.data.startswith('cb_story_dl_'):
        pk = int(call.data.replace('cb_story_dl_', ''))
        bot.answer_callback_query(call.id, f'Get Story {pk}')
        send_story(call.from_user.id, pk)

    elif call.data == 'cb_story_all':
        bot.answer_callback_query(call.id, 'Get all Stories!')
        stories = client.user_stories(user_id)

        stories_list = []
        for number, story in enumerate(stories):
            story_caption = f"{EMOJI['username']} {story.user.username}\n{EMOJI['date']} {dt.strftime(story.taken_at, '%A - %d %B %Y')}\n{EMOJI['time']} {dt.strftime(story.taken_at, '%H:%M')}\nStory Number: {number+1}\n\n#u{story.user.pk}"
            if story.media_type == 1:
                stories_list.append(types.InputMediaPhoto(story.thumbnail_url, caption=story_caption))
            elif story.media_type == 2:
                stories_list.append(types.InputMediaVideo(story.video_url, caption=story_caption))
            else:
                bot.send_message(call.from_user.id, f'FORMAT NOT FOUND!\nHighlight: {highlight.title}\nStory Number: {number+1}')

        send_group_files(call.from_user.id, stories_list)

    # Post
    elif call.data == 'cb_post':
        posts = client.user_medias(user_id, 15)
        if len(posts) == 0:
            bot.answer_callback_query(call.id, 'User has no post!')
        else:
            bot.answer_callback_query(call.id, 'Select Post')
            bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=IKMGenerator(posts, 3, 'post'))

    elif call.data.startswith('cb_post_dl_'):
        pk = int(call.data.replace('cb_post_dl_', ''))
        bot.answer_callback_query(call.id, f'Get Post {pk}')
        send_media(call.from_user.id, pk)

    # Highlight
    elif call.data == 'cb_highlight':
        highlights = client.user_highlights(user_id)
        if len(highlights) == 0:
            bot.answer_callback_query(call.id, 'User has no highlight!')
        else:
            bot.answer_callback_query(call.id, 'Select Highlight')
            bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=IKMGenerator(highlights, 3, 'highlight'))

    elif call.data.startswith('cb_highlight_dl_'):
        pk = int(call.data.replace('cb_highlight_dl_', ''))
        bot.answer_callback_query(call.id, f'Select Story from Highlight {pk}')
        highlight = client.highlight_info(pk)
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=IKMGenerator(highlight.items, 5, 'story', True, highlight_pk=highlight.pk))

    elif call.data.startswith('cb_story_all_'):
        pk = int(call.data.replace('cb_story_all_', ''))
        bot.answer_callback_query(call.id, f'Get all Stories from Highlight {pk}')
        highlight = client.highlight_info(pk)

        stories_list = []
        for number, story in enumerate(highlight.items):
            story_caption = f"{EMOJI['username']} {story.user.username}\n{EMOJI['date']} {dt.strftime(story.taken_at, '%A - %d %B %Y')}\n{EMOJI['time']} {dt.strftime(story.taken_at, '%H:%M')}\nHighlight: {highlight.title}\nStory Number: {number+1}\n\n#u{story.user.pk}"
            if story.media_type == 1:
                stories_list.append(types.InputMediaPhoto(story.thumbnail_url, caption=story_caption))
            elif story.media_type == 2:
                stories_list.append(types.InputMediaVideo(story.video_url, caption=story_caption))
            else:
                bot.send_message(call.from_user.id, f'FORMAT NOT FOUND!\nHighlight: {highlight.title}\nStory Number: {number+1}')

        send_group_files(call.from_user.id, stories_list)


@bot.inline_handler(lambda query: len(query.query) != 0)
def inline_query(query):
    try:
        try:
            user_info = client.user_info_by_username(query.query)
            caption = '\n\n'.join([
                f"{EMOJI['username']} Username: {user_info.username}",
                f"{EMOJI['name']} FullName: {user_info.full_name}",
                f"{EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}",
                f"{EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} {'Verified Account' if user_info.is_verified else 'Not Verified Account'}",
                f"{EMOJI['bio']} Biography: {user_info.biography}",
                f"{EMOJI['post']} {user_info.media_count} Posts",
                f"{EMOJI['follower']} {user_info.follower_count:,} Followers",
                f"{EMOJI['following']} {user_info.following_count:,} Followings",
                f"{EMOJI['url']} {user_info.external_url if user_info.external_url else ''}",
                f"#u{user_info.pk}"
            ])
            r = types.InlineQueryResultPhoto('1', user_info.profile_pic_url, user_info.profile_pic_url, title=user_info.username, description=user_info.full_name, caption=caption,)

        except instagrapi.exceptions.UserNotFound as e:
            r = types.InlineQueryResultArticle('1', f'Not Found', input_message_content=types.InputTextMessageContent(query.query))

        bot.answer_inline_query(query.id, [r])

    except Exception as e:
        print(e)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello World')


@bot.message_handler(commands=['login'])
def bot_login(message):
    is_logged_in = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))
    bot.send_message(message.chat.id, f"{'Logged in' if is_logged_in else 'Can not log in'}")


@bot.message_handler(commands=['logout'])
def bot_login(message):
    is_logged_out = client.logout()
    bot.send_message(message.chat.id, f"{'Logged out' if is_logged_out else 'Can not log out'}")


@bot.message_handler(func=lambda message: True)
def answer_message(message):
    text = message.text
    try:
        if text.startswith('eval '):
            bot.reply_to(message, f'{eval(text[5:])}')

        # Get link
        elif 'instagram.com/' in text:
            # Story
            if 'stories' in text:
                pk = client.story_pk_from_url(text)
                send_story(message.chat.id, pk)

            # Post
            elif any(media in text for media in ['/p/', '/tv/', '/reel/']):
                pk = client.media_pk_from_url(text)
                send_media(message.chat.id, pk)

            else:
                bot.send_message(message.chat.id, 'URL NOT FOUND!')

        # Search for Username
        else:
            user_info = client.user_info_by_username(text)
            caption = '\n\n'.join([
                f"{EMOJI['username']} Username: {user_info.username}",
                f"{EMOJI['name']} FullName: {user_info.full_name}",
                f"{EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}",
                f"{EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} {'Verified Account' if user_info.is_verified else 'Not Verified Account'}",
                f"{EMOJI['bio']} Biography: {user_info.biography}",
                f"{EMOJI['post']} {user_info.media_count} Posts",
                f"{EMOJI['follower']} {user_info.follower_count:,} Followers",
                f"{EMOJI['following']} {user_info.following_count:,} Followings",
                f"{EMOJI['url']} {user_info.external_url if user_info.external_url else ''}",
                f"#u{user_info.pk}"
            ])
            bot.send_photo(message.chat.id, user_info.profile_pic_url, caption, reply_markup=user_info_markup(user_info.pk))
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        pass  # CHECK FOR NEW STORIES , POSTS , DMS , ...
