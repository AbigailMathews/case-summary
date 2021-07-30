from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel

from config import get_settings, Settings

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello OpenPolice'}


@app.get('/status')
async def get_status(settings: Settings = Depends(get_settings)):
    return {
        'environment': settings.environment,
        'testing': settings.testing
    }
