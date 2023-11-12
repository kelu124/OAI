from .basics import *

import openai 
from dotenv import dotenv_values
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from dotenv import dotenv_values
import os
import openai
import time 
import pandas as pd
import glob
from dotenv import dotenv_values
import os
import openai
import time 
import hashlib
import datetime
from pymongo import MongoClient


#OpenAI
config = dotenv_values(".env")
openai.api_key = config["OAI"]
#Local cache
GOTOCACHE = config["CACHE"]
#Database
PWD = config["PWD"]
DB = config["DB"]
# To log questions
cluster = MongoClient(DB)
db = cluster["OAI"]
collection = db["OAI_Collection"]



GPT_MODEL = "gpt-3.5-turbo-1106"

class askFCT():
    def __init__(self, *args):
        if not len(args):
            self.NAME = "local"
        else:
            self.NAME = args[0]
        if len(args) <= 1:
            self.PATH = GOTOCACHE
        else:
            self.PATH = args[1]
        
        self.DB = collection


    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self,messages, functions=None, function_call=None, model=GPT_MODEL):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + openai.api_key,
        }
        json_data = {"model": model, "messages": messages}
        if functions is not None:
            json_data.update({"functions": functions})
        if function_call is not None:
            json_data.update({"function_call": function_call})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
        
    def pretty_print_conversation(self,messages):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        
        for message in messages:
            if message["role"] == "system":
                print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "user":
                print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and message.get("function_call"):
                print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and not message.get("function_call"):
                print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "function":
                print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


    def askFct(self,CONTEXT,Q,functions,modelGPT=GPT_MODEL,ow=False):
        messages = []
        messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.\n"+CONTEXT})
        messages.append({"role": "user", "content": Q})

        MSG =  ""
        for msg in messages:
            MSG += msg["role"]+": "+msg["content"]+"\n\n=========\n\n"
        MSG += "\n\n=========\nFUNCTION\n=========\n\n"+ str(functions)
        ID =hashme(MSG)

        PATH = GOTOCACHE + ID
        if ow:
            # Si on réécrit
            chat_response = self.chat_completion_request(
                messages, functions, model=modelGPT
            )
            try:
                summary = chat_response.json()["choices"][0]["message"]
            except:
                print(chat_response.json())
            svt(PATH,json.dumps(summary))
            NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            LOG = {"app":self.NAME,"query":MSG, "ID":ID, "answer":summary, "when":NOW}
            self.DB.insert_one(LOG)

        else:
            CHECK_ONLINE = self.DB.find_one({"ID": ID})
            if CHECK_ONLINE:
                summary = CHECK_ONLINE["answer"]
                # Si pas en local on sauve quand même
                if not os.path.exists(PATH):
                    svt(PATH,json.dumps(summary))
            else:
                # Rien en ligne
                # On check en local
                if not os.path.exists(PATH):
                    chat_response = self.chat_completion_request(
                        messages, functions, model=modelGPT
                    )
                    summary = chat_response.json()["choices"][0]["message"]

                    svt(PATH,json.dumps(summary))
                else:
                    summary = json.loads(ldt(PATH))
                # On ajoute le résumé
                NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                LOG = {"app":self.NAME,"query":MSG, "ID":ID, "answer":summary, "when":NOW}
                self.DB.insert_one(LOG)

        
        return summary
