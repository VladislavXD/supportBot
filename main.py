from telebot import TeleBot, types
import uuid
import os
from keep_alive import keep_alive

# Инициализация бота с токеном
bot = TeleBot(os.environ['TOKEN'])
# 7974154274:AAGfe2jBEBnMWbpqJbznP8C8krDEd7CxGNI

# ID вашего канала
channel_id = os.environ['CHANNEL_ID']
# -1002173356863

# ID администратора
admin_id = os.environ['ADMIN_ID']
# 902267980

# Словарь для временного хранения данных
temp_data = {}

keep_alive()
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Здравствуйте отправьте свое сообщение, оно скоро опобликуется на канале.')

@bot.message_handler(commands=['mess'])
def send_to_channel(message):
    commands_parts = message.text.split(' ', 1)

    if len(commands_parts) < 2:
        bot.send_message(message.chat.id, 'Укажите все аргументы, /mess сообщение')
        return

    # Отправляем сообщение администратору для подтверждения
    text_to_send = commands_parts[1]
    data_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор для данных
    temp_data[data_id] = text_to_send
    
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton("✅", callback_data=f'confirm_text:{data_id}')
    reject_button = types.InlineKeyboardButton("❌", callback_data=f'reject_text:{data_id}')
    markup.add(confirm_button, reject_button)
    
    bot.send_message(admin_id, f'Новое сообщение для отправки в канал:\n\n{text_to_send}', reply_markup=markup)
    bot.send_message(message.chat.id, 'Сообщение отправлено. Ожидайте подтверждения администратора.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Отправляем фото администратору для подтверждения
    photo_id = message.photo[-1].file_id
    caption = message.caption if message.caption else ''
    data_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор для данных
    temp_data[data_id] = {'photo_id': photo_id, 'caption_photo': caption}
    
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton("✅", callback_data=f'confirm_photo:{data_id}')
    reject_button = types.InlineKeyboardButton("❌", callback_data=f'reject_photo:{data_id}')
    markup.add(confirm_button, reject_button)
    
    bot.send_photo(admin_id, photo_id, caption=f'Новое фото для отправки в канал:\n\n{caption}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: any(call.data.startswith(prefix) for prefix in ['confirm_text:', 'reject_text:', 'confirm_photo:', 'reject_photo:']))
def handle_confirmation(call):
    action, data_id = call.data.split(':', 1)

    if action == 'confirm_text':
        content = temp_data.get(data_id, '')
        bot.send_message(channel_id, f'{content}')
        bot.send_message(call.message.chat.id, 'Сообщение успешно отправлено в канал.')
        bot.send_message(admin_id, 'Сообщение успешно отправлено в канал.')
    elif action == 'reject_text':
        bot.send_message(call.message.chat.id, 'Сообщение отклонено администратором.')
    elif action == 'confirm_photo':
        data = temp_data.get(data_id, {})
        photo_id = data.get('photo_id', '')
        caption = data.get('caption_photo', '')
        bot.send_photo(channel_id, photo_id, caption=caption)
        bot.send_message(call.message.chat.id, 'Фото успешно отправлено в канал.')
    elif action == 'reject_photo':
        bot.send_message(call.message.chat.id, 'Фото отклонено администратором.')

    # Удаляем данные из временного хранилища после использования
    if data_id in temp_data:
        del temp_data[data_id]

    # Удаляем inline-кнопки после ответа
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_id = message.video.file_id
    caption = message.caption if message.caption else ''
    data_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор для данных
    temp_data[data_id] = {'video_id': video_id, 'caption_video': caption}
    
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton("✅", callback_data=f'confirm_video:{data_id}')
    reject_button = types.InlineKeyboardButton("❌", callback_data=f'reject_video:{data_id}')
    markup.add(confirm_button, reject_button)
    
    bot.send_video(admin_id, video_id, caption=f'Новое видео для отправки в канал:\n\n{caption}', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: any(call.data.startswith(prefix) for prefix in ['confirm_video:', 'reject_video:', 'confirm_text:', 'reject_text:']))
def handle_confirmation_video(call):
    action, data_id = call.data.split(':', 1)

    if action == 'confirm_text':
        content = temp_data.get(data_id, '')
        bot.send_message(channel_id, f'{content}')
        bot.send_message(call.message.chat.id, 'Сообщение успешно отправлено в канал.')
    elif action == 'reject_text':
        bot.send_message(call.message.chat.id, 'Сообщение отклонено администратором.')
    elif action == 'confirm_video':
        data = temp_data.get(data_id, {})
        video_id = data.get('video_id', '')
        caption = data.get('caption_video', '')
        bot.send_video(channel_id, video_id, caption=caption)
        bot.send_message(call.message.chat.id, 'Видео успешно отправлено в канал.')
    elif action == 'reject_video':
        bot.send_message(call.message.chat.id, 'Видео отклонено администратором.')

    # Удаляем данные из временного хранилища после использования
    if data_id in temp_data:
        del temp_data[data_id]

    # Удаляем inline-кнопки после ответа
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
@bot.message_handler(content_types=['text'])
def echo_all(message):
    bot.reply_to(message, 'Для отправки сообщения используйте команду /mess текст_сообщения')

if __name__ == '__main__':
    bot.polling(non_stop=True)
    