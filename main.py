import os
import logging
import tempfile
from pydub import AudioSegment
import speech_recognition
from telegram import Update, ChatAction
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext


recognizer = speech_recognition.Recognizer()
cache_dir = tempfile.mkdtemp()


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, I'm listening...")


def voice_to_text(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    file_id = update.message.voice.file_id
    file_name_ogg = f'{cache_dir}/{file_id}.ogg'
    file_name_flac = f'{cache_dir}/{file_id}.flac'
    voice_file = context.bot.get_file(file_id)
    voice_file.download(file_name_ogg)
    AudioSegment.from_ogg(file_name_ogg).export(file_name_flac, format='flac')
    vtt_file = speech_recognition.AudioFile(file_name_flac)
    with vtt_file as source:
        vtt_audio = recognizer.record(source)
    vtt_text = recognizer.recognize_google(vtt_audio)
    context.bot.send_message(chat_id=update.effective_chat.id, text=vtt_text)


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')

bot_token = os.environ['TELEGRAM_API_TOKEN']

updater = Updater(token=bot_token, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_to_text))

updater.start_polling()
