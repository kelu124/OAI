from dotenv import dotenv_values
import os, hashlib, json
import openai
from openai import OpenAI 
from pymongo import MongoClient
import gzip

is_prod = os.environ.get('IS_HEROKU', None)

def downloadDB(pathout):
    config = dotenv_values(".env")
    DBAdress = config["DB"]
    cluster = MongoClient(DBAdress)
    db = cluster["OAI"]
    DB = db["OAI_Collection"]
    allDBItems = {}
    allLogs = DB.find()
    for log in list(allLogs):
        allDBItems[log["ID"]] = log
        allDBItems[log["ID"]]["_id"] = str(allDBItems[log["ID"]]["_id"])
    json_bytes = json.dumps(allDBItems).encode('utf-8')           
    with gzip.open(pathout, 'w') as fout:   
        fout.write(json_bytes)
    return pathout

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

def getDB(ID):
    config = dotenv_values(".env")
    DBAdress = config["DB"]
    cluster = MongoClient(DBAdress)
    db = cluster["OAI"]
    DB = db["OAI_Collection"]
    DB.find_one({"ID": ID})

class APIBase():

    def __init__(self, *args):

        if os.path.isfile(".env"): # os.environ.get('THEANSWERTOEVERYTHINGEVER')

            self.config = dotenv_values(".env")
            #OpenAI
            openai.api_key = self.config["OAI"]
            #Local cache
            self.GOTOCACHE = self.config["CACHE"]
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
                self.PATH = self.GOTOCACHE
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
            self.GOTOCACHE = os.environ.get('CACHE')
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
                self.PATH = self.GOTOCACHE
            else:
                self.PATH = args[1]
            
            self.DB = self.collection
            self.CLIENT = OpenAI(
                api_key=openai.api_key
            )
        else:
            print("No passwords -- you need to have a .env file nearby")