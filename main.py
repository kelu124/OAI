from fastapi import FastAPI
import os
from pydantic import BaseModel
import OAI

app = FastAPI()
is_prod = os.environ.get('IS_HEROKU', None)

class RequestAsk(BaseModel):
    context: str = "What is the size of the sun"
    question: str = "answer with the size in km"
    model: str = "gpt-3.5-turbo-1106"
    token: str = "TOKEN"
    overwrite: bool = False

@app.post("/ask/")
async def ask(itemR: RequestAsk):

    if (itemR.token == os.environ.get('TOKEN')) or (not is_prod):
        h = OAI.Helper("fastapi","./cache")
        print("OVERWRITE",itemR.overwrite)
        ans = h.ask(itemR.context,itemR.question,v=itemR.model,ow=itemR.overwrite)
    else:
        ans = "Incorrect token "
    return {"answer":ans}


@app.get("/")
async def root():
    return {"message": "Hello World","is_prod":is_prod,"TestSecret":os.environ.get('CACHE')}

