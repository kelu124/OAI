from fastapi import FastAPI
import os


app = FastAPI()
is_prod = os.environ.get('IS_HEROKU', None)


@app.get("/")
async def root():
    return {"message": "Hello World","is_prod":is_prod,"TestSecret":os.environ.get('CACHE')}

