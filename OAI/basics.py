from dotenv import dotenv_values
import os
import openai
import time, json

import pandas as pd
import glob
from dotenv import dotenv_values
import os
import openai
from openai import OpenAI
import time 
import hashlib
import datetime
from pymongo import MongoClient

is_prod = os.environ.get('IS_HEROKU', None)


# HELPERS
def svt(N,c):
    with open(N, 'w', encoding='utf-8') as f:
        f.write(c)
    
def ldt(N):
    with open(N, "r", encoding='utf8') as f:
        c = f.read()
    return c
    
def hashme(STR):
    STR = str(STR)
    return str(hashlib.md5(STR.encode('utf-8')).hexdigest())


## Helper class
class Helper():

    def __init__(self, *args):
        if os.path.isfile(".env"): # os.environ.get('THEANSWERTOEVERYTHINGEVER')

            self.config = dotenv_values(".env")
            #OpenAI
            openai.api_key = self.config["OAI"]
            #Local cache
            GOTOCACHE = self.config["CACHE"]
            #Database
            self.PWD = self.config["PWD"]
            self.DBAdress = self.config["DB"]
            # To log questions
            self.cluster = MongoClient(self.DBAdress)
            self.db = self.cluster["OAI"]
            self.collection = self.db["OAI_Collection"]

            if not len(args):
                self.NAME = "local"
            else:
                self.NAME = args[0]
            if len(args) <= 1:
                self.PATH = GOTOCACHE
            else:
                self.PATH = args[1]
            
            self.DB = self.collection
            self.CLIENT = OpenAI(
                api_key=self.config["OAI"]
            )
        elif  is_prod :
            #OpenAI
            openai.api_key = os.environ.get('OAI')
            #Local cache
            GOTOCACHE = os.environ.get('CACHE')
            #Database
            self.PWD = os.environ.get('PWD')
            self.DBAdress = os.environ.get('DB')
            # To log questions
            self.cluster = MongoClient(self.DBAdress)
            self.db = self.cluster["OAI"]
            self.collection = self.db["OAI_Collection"]

            if not len(args):
                self.NAME = "local"
            else:
                self.NAME = args[0]
            if len(args) <= 1:
                self.PATH = GOTOCACHE
            else:
                self.PATH = args[1]
            
            self.DB = self.collection
            self.CLIENT = OpenAI(
                api_key=self.config["OAI"]
            )
        else:
            print("No passwords")







    def ask_GPT(self,system_intel, prompt,MODEL="gpt-3.5-turbo-1106"): 
        # Alternative "gpt-4"
        now = datetime.datetime.now() # current date and time2
        chat_messages = [{"role": "system", "content": system_intel},
                                            {"role": "user", "content": prompt}]
        response = self.CLIENT.chat.completions.create(
            model=MODEL,
            messages=chat_messages
        )
        now2 = datetime.datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S") + " --> " + now2.strftime("%m/%d/%Y, %H:%M:%S")
        print("Processing with",MODEL,":\t",date_time)	

        answer = json.loads(response.json())["choices"][0]["message"]["content"]
        return answer


    def ask(self,CONTEXT,Q,v="gpt-3.5-turbo-16k-0613",ow=False):
        STR = "Context: "+CONTEXT + "\n\n=========\n\nQuestion: "+ Q + "\n\n=========\n\nVersion: " + v
        ID = hashme(STR.encode('utf-8'))
        PATH = GOTOCACHE + ID
        #print(PATH)
        if ow:
            # Si on réécrit
            summary = self.ask_GPT(CONTEXT, Q, v)

            NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #print("saving after overwrite")
            self.DB.delete_many({"ID":ID})
            LOG = {"app":self.NAME,"query":STR, "ID":ID, "answer":summary, "when":NOW}
            self.DB.insert_one(LOG)
            svt(PATH,summary)
            log = "OW"
        else:
            CHECK_ONLINE = self.DB.find_one({"ID": ID})
            if CHECK_ONLINE:
                log = "Found cached online"
                summary = CHECK_ONLINE["answer"]
                # Si pas en local on sauve quand même
                if not os.path.exists(PATH):
                    svt(PATH,summary)
            else:
                # Rien en ligne
                # On check en local
                if not os.path.exists(PATH):
                    log = "loading from local file"
                    summary = self.ask_GPT(CONTEXT, Q, v)
                    svt(PATH,summary)
                else:
                    log = "Found cached locally"
                    summary = ldt(PATH)
                # On ajoute le résumé
                NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.DB.delete_many({"ID":ID})
                LOG = {"app":self.NAME,"query":STR, "ID":ID, "answer":summary, "when":NOW}
                self.DB.insert_one(LOG)
        
        return summary
