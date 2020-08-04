"""
Имя бота "test43969_bot"

Бот умеет:

1. Сохранять аудиосообщения из диалогов в базу данных (СУБД или на диск) по идентификаторам пользователей.
2. Конвертирует все аудиосообщения в формат wav с частотой дискретизации 16kHz
Формат записи: uid —> [audio_message_0, audio_message_1, ..., audio_message_N].
3. Определяет есть ли лицо на отправляемых фотографиях или нет, сохраняет только те, где оно есть
"""

import telebot
import pydub
import face_recognition
import os
import sqlite3

bot = telebot.TeleBot('1399489811:AAGrCfMGZiXl7XTd7gt6QtNzFiX5sDguSaE')


def create_dir():
    """Создает директории, в которые будут сохранятся фотографии и аудиосообщения"""
    try:
        os.mkdir(os.getcwd() + '/received')
        os.mkdir(os.getcwd() + '/received/photos')
        os.mkdir(os.getcwd() + '/received/voice')
    except:
        pass


create_dir()


@bot.message_handler(content_types=['voice'])
def receive_audio(message):
    """Сохраняет аудиосообщеня на диск"""
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src = os.getcwd() + '/received/voice/' + str(message.voice.file_id) + '.ogg'
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    set_voice(src)
    save_voice_to_db(message.from_user.id, message.voice.file_id)
    os.remove(src)


def set_voice(file):
    """Конвертирует аудиосообщения в формат .wav и изменяет частоту дискретизации на 16kHz"""
    voice = pydub.AudioSegment.from_file(file, format="ogg").set_frame_rate(16000)
    voice.export(file[:-4] + '.wav', format="wav")


def save_voice_to_db(user_id, file_id):
    """Добавляет аудиосообщения в базу данных"""
    db = sqlite3.connect('bot.db')
    cur = db.cursor()

    try:
        messages = cur.execute(f"SELECT audo_message_N FROM audio WHERE uid == {user_id}")
        number_of_message = int(list(messages)[-1][0][14:]) + 1
    except:
        number_of_message = 0

    cur.execute("INSERT INTO audio VALUES (?, ?, ?)", (user_id, 'audio_message_' + str(number_of_message), file_id))
    db.commit()
    db.close()


@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    """Сохраняет фотографии на диск"""
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = os.getcwd() + '/received/photos/' + file_info.file_id + file_info.file_path[-4:]

    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    if not face_photo_check(src):
        os.remove(src)


def face_photo_check(photo):
    """Проверяет фотографии на наличие в них лиц"""
    image = face_recognition.load_image_file(photo)
    return face_recognition.face_locations(image)


bot.polling()