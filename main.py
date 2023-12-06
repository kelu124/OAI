from fastapi import FastAPI
import os
from pydantic import BaseModel
import OAI
import app_tools
from typing import List


app = FastAPI()
is_prod = os.environ.get('IS_HEROKU', None) 



default_tools = [
    {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        },
    {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }

]



default_messages = [{'role': 'system',
  'content': "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.\nDon't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
 {'role': 'user', 'content': "What's the weather like today in Dublin"},
 {'role': 'assistant',
  'content': None,
  'function_call': {'name': 'get_current_weather',
   'arguments': '{"location":"Dublin","format":"celsius"}'}},
 {'role': 'user', 'content': 'The city is Dublin'}]

class RequestAsk(BaseModel):
    context: str = "What is the size of the sun"
    question: str = "answer with the size in km"
    model: str = "gpt-3.5-turbo-1106"
    token: str = "TOK3N"
    overwrite: bool = False
    source: str = "api"

class RequestFct(BaseModel):
    context: str = "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
    question: str = "What's the weather like today"
    model: str = "gpt-3.5-turbo-1106"
    functions : List[dict] = default_tools
    overwrite: bool = False
    token: str = "TOK3N"
    source: str = "api"

class RequestFctEngine(BaseModel):
    messages: List[dict] = default_messages
    model: str = "gpt-3.5-turbo-1106"
    functions : List[dict] = app_tools.default_tools
    overwrite: bool = False
    token: str = "TOK3N"
    source: str = "api"

@app.post("/ask/")
async def ask(itemR: RequestAsk):

    if (itemR.token == os.environ.get('TOKEN')) or (not is_prod):
        h = OAI.Helper("fastapi","./cache")
        print("OVERWRITE",itemR.overwrite)
        ans = h.ask(itemR.context,itemR.question,v=itemR.model,ow=itemR.overwrite,src=itemR.source)
    else:
        ans = "Incorrect token "
    return {"answer":ans}



@app.post("/fct/")
async def fct(itemR: RequestFct):
    if (itemR.token == os.environ.get('TOKEN')) or (not is_prod):
        f = OAI.askFCT("demo_fct_fastapi","./cache")
        print("OVERWRITE",itemR.overwrite)
        messages, chat_response = f.askFct(itemR.context,itemR.question,itemR.functions,modelGPT=itemR.model,ow=itemR.overwrite,src=itemR.source)
        #ans = h.ask(itemR.context,itemR.question,v=itemR.model,ow=itemR.overwrite)
    else:
        messages = {}
        chat_response = ""
    return {"messages":messages,"answer":chat_response}

@app.post("/fctEngine/")
async def fctEngine(itemR: RequestFctEngine):
    if (itemR.token == os.environ.get('TOKEN')) or (not is_prod):
        f = OAI.askFCT("demo_fctengine_fastapi","./cache")
        print("OVERWRITE",itemR.overwrite)
        msgs, answer = f.askFtcEngine(itemR.messages,itemR.functions,modelGPT=itemR.model,ow=itemR.overwrite,src=itemR.source)
        #ans = h.ask(itemR.context,itemR.question,v=itemR.model,ow=itemR.overwrite)
    else:
        msgs = {}
        answer = ""
    return {"messages":msgs,"answer":answer}


@app.get("/version/")
async def versioned():
    return {"v": OAI.__version__}



@app.get("/")
async def root():
    return {"message": "Hello World","is_prod":is_prod,"TestSecret":os.environ.get('CACHE')}

