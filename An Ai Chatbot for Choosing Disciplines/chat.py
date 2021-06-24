from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.response_selection import get_random_response
import random
import csv
import os
import pandas as pd
from botConfig import myBotName, chatBG, botIcon, confidenceLevel

from dateTime import getTime, getDate

import logging
logging.basicConfig(level=logging.INFO)

application = Flask(__name__)

chatbotName = myBotName
print("Bot Name set to: " + chatbotName)
print("Background is " + chatBG)
print("Icon is " + botIcon)
print("Confidence level set to " + str(confidenceLevel))

try:
    file = open('BotLog.csv', 'r')
except IOError:
    file = open('BotLog.csv', 'w')

bot = ChatBot(
    "ChatBot",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch'
        },
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': confidenceLevel,
            'default_response': 'IDKresponse'
        }
    ],
    response_selection_method=get_random_response,
    input_adapter="chatterbot.input.VariableInputTypeAdapter",
    output_adapter="chatterbot.output.OutputAdapter",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database="botData.sqlite3"
)

bot.read_only=True
print("Bot Learn Read Only:" + str(bot.read_only))

class user:

    def __init__(self, process):
        self.process = 0

a = user(0)

@application.route("/")
def home():
    return render_template("index.html", botName = chatbotName, chatBG = chatBG, botIcon = botIcon)

@application.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    botReply = str(bot.get_response(userText))
    while(a.process == 1 or a.process == 2):
        if userText != "Exit" and a.process == 1:
            a.process = 2
            global interest
            interest = userText
            botReply = "What is your DSE score? You can type Exit to close the process"
            return botReply
        elif userText != "Exit" and a.process == 2:
            a.process = 0
            global DSEscore
            DSEscore = int(userText)
            botReply = recommendSystem(interest, DSEscore)
            return botReply
        elif userText == "Exit":
            a.process = 0
            botReply = ("The recommend process has been closed")
            return botReply
    else:
        if botReply == "startAcademicGuidance":
            a.process = 1
            botReply = "So What is you interested in? You can type Exit to close the process"
            return botReply
        elif botReply is "IDKresponse":
            botReply = str(bot.get_response('IDKnull'))
        elif botReply == "getTIME":
            botReply = getTime()
            print(getTime())
        elif botReply == "getDATE":
            botReply = getDate()
            print(getDate())
        with open('BotLog.csv', 'a', newline='') as logFile:
            if a.process == 0:
                newFileWriter = csv.writer(logFile)
                newFileWriter.writerow([userText, botReply])
                logFile.close()
                print("Logging to CSV file now")
    return botReply

def recommendSystem(interest, DSEscore):
    jupasData = pd.read_csv("./data/jupas_data.csv")
    try:
        recommend = jupasData[jupasData['lable 1'].str.contains(interest)]
    except IndexError:
        return("Sorry. I cannot find a suitable degree for you.")
    try:
        recommend = recommend.append(jupasData[jupasData['lable 2'].str.contains(interest, na = False)])
    except IndexError:
        return("Sorry. I cannot find a suitable degree for you.")
    recommend = recommend.drop_duplicates()
    try:
        recommend = recommend[recommend['score'] <= DSEscore]
    except IndexError:
        return("Sorry. I cannot find a suitable degree for you.")
    studyLevel = recommend['Study Level'].iloc[0]
    programmeName = recommend['Programme name'].iloc[0]
    university = recommend['University'].iloc[0]
    fyTuitionFee = recommend['First Year Tuition Fee'].iloc[0]
    admissionScore = str(recommend['score'].iloc[0])
    univUrls = recommend['urls'].iloc[0]
    return ("Your interest is " + interest +" and your DSE score is " + str(DSEscore) + "." +  "<br>I recommend you this programme " + studyLevel + '<br>"' + programmeName + '". from ' + university + "." + " <br>Its first year tuition fee is " + fyTuitionFee + " and the lowest admission score is " + admissionScore + ".<br>Here is the link for you to check more information." +  "<br><br><a href="" + univUrls + "">" + univUrls + "</a>")

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
