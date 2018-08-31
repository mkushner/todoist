# setup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from todoist.api import TodoistAPI

import xml.etree.ElementTree as XmlElementTree
import requests
import sys
import os
import io
import random
import google.cloud.proto.speech.v1.cloud_speech_pb2 as direct_gcall

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="YOUR_GA_CRED_FILE"

updater = Updater(
    token='YOUR_TG_API_TOKEN')  # API Telegram
dispatcher = updater.dispatcher

# command processing
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Tell me your next task')

#get msg
def audioMessage(bot, update):  

    request_audio = update.message.voice  # get message data/voice type
    if (request_audio):
        file_info = bot.get_file(request_audio.file_id)        
        telegram_response = requests.get(file_info.file_path)        

        if telegram_response:
            audio_content = telegram_response.content
        else:
            exit

        #Call audio recognition here
        voice_response_text = VoiceRecognitionG(audio_content) # using link to process voice file via Google (client library)

        if (voice_response_text == "No data responded"):
            bot.send_message(chat_id=update.message.chat_id, text='Task name not resolved, please try again')     
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Task to create: ' + voice_response_text )
            CreateTodoistTask(voice_response_text)             
         
    else:
        print("\nNo voice input provided, please try again")              

# GoogleCloud recognition
def VoiceRecognitionG(b_voice_data): 
    client = speech.SpeechClient()

    audio = direct_gcall.RecognitionAudio(content=b_voice_data)
    config = direct_gcall.RecognitionConfig(
        encoding = enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz = 48000,
        language_code = 'ru-RU',
        max_alternatives = 0)

    # Recognize speech content
    response = client.recognize(config, audio)
    
    if(response.results):
        print(response.results)
        for result in response.results:
            rec_voice = result.alternatives[0].transcript   
            return rec_voice
    else:
        rec_voice = "No data responded"
        return rec_voice    

def CreateTodoistTask (taskname):
    # initialize the API object

    token = 'YOUR_TD_TOKEN'
    api = TodoistAPI(token)

    # Create a new task
    api.items.add(taskname, None, date_string='today')

    # commit
    api.commit()


#Telegram API handler below
# handler
start_command_handler = CommandHandler('start', startCommand)
voice_message_handler = MessageHandler(Filters.voice, audioMessage)

# dispatcher handler
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(voice_message_handler)

# updale lookup
updater.start_polling(clean=True)

# exit Ctrl + C
updater.idle()