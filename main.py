import os
import logging
import tempfile
from random import randint
import wave
import librosa
import soundfile
import numpy as np
import deepspeech
from pydub import AudioSegment
import speech_recognition
from speech_recognition import UnknownValueError
from telegram import Update, ChatAction
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext


recognizer = speech_recognition.Recognizer()
# stt_model = deepspeech.Model("./model/en-US/deepspeech-0.8.2-models.tflite")
cache_dir = tempfile.mkdtemp()

# cache_dir = '/home/tobias/Downloads/audiobot_tests'
unknown_value_msgs = [
    "Stop talking nonsense!",
    "That's just gibberish...",
    "Bazoo, bazoo, bazoo? That's what it sounds when you're talking right nooow"
]


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, I'm listening...")


def voice_to_text(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    file_id = update.message.voice.file_id
    file_name_ogg = f'{cache_dir}/{file_id}.ogg'
    file_name_out = f'{cache_dir}/{file_id}.flac'
    voice_file = context.bot.get_file(file_id)
    voice_file.download(file_name_ogg)
    # audio_data, sr = librosa.load(file_name_ogg, sr=16000)
    # librosa.resample(audio_data, sr, 16000)
    # soundfile.write(file_name_out, audio_data, 16000, format='flac', subtype='PCM_24')
    segment = AudioSegment.from_ogg(file_name_ogg)
    # segment.set_frame_rate(16000)
    segment.export(file_name_out, format='flac')
    vtt_file = speech_recognition.AudioFile(file_name_out)
    with vtt_file as source:
        vtt_audio = recognizer.record(source)
    # wave_file = wave.open(file_name_out, 'r')
    # rate = wave_file.getframerate()
    # print(f'rate: {rate}')
    # vtt_text = recognizer.recognize_sphinx(vtt_audio, language="de-DE")
    vtt_text = "Something went wrong"
    try:
        vtt_text = recognizer.recognize_google_cloud(vtt_audio)
    except UnknownValueError as e:
        print(e)
        vtt_text = unknown_value_msgs[randint(0, len(unknown_value_msgs) - 1)]
    except Exception as e:
        print("Unexpected error!")
        print(e)
    # vtt_text.
    # frames = wave_file.getnframes()
    # buffer = wave_file.readframes(frames)
    # batch = np.frombuffer(buffer, dtype=np.int16)
    # print(f'rate: {rate}, model rate: {stt_model.sampleRate()}')
    # print(f'frame count: {frames}')
    #result = stt_model.sttWithMetadata(batch).transcripts[0]
    #result_text = ''.join([t.text for t in result.tokens])
    #print(f'confidence: {result.confidence}; text: "{result_text}')
    # result_text = stt_model.stt(batch)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=vtt_text)
    os.remove(file_name_ogg)
    os.remove(file_name_out)


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')

bot_token = os.environ['TELEGRAM_API_TOKEN']

updater = Updater(token=bot_token, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_to_text))

updater.start_polling()
