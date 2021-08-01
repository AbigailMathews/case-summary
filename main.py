from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Body, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

import openai
import os
import json

from config import get_settings, Settings
import crud
import models
import schemas
from database import SessionLocal, engine

from secrets import API_KEY, API_KEY_NAME, OPENAI_API_KEY

models.Base.metadata.create_all(bind=engine)

openai.api_key = OPENAI_API_KEY

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API Key'
        )

app = FastAPI(dependencies=[Security(get_api_key)])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_new_summary(case: schemas.Case):
    prompt = "I need to summarize the important points of the following story for a legal case: {}\n\nI create a brief, three-sentence summary:".format(
        case.narrative)

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.8,
        max_tokens=80,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        stop=["\n\n\n"]
    )

    return response.choices[0]['text']


async def get_new_keywords(case: schemas.Case):
    prompt = "A lawyer needs to choose keywords to classify the following text: {}\n\nThe lawyer lists the following 5 keywords:".format(
        case.narrative)

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.3,
        max_tokens=30,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.0,
        stop=["\n\n\n"]
    )
    return response.choices[0]['text']


@app.get('/')
async def root():
    return {'message': 'Hello OpenPolice'}


@app.get('/status')
async def get_status(settings: Settings = Depends(get_settings)):
    return {
        'environment': settings.environment,
        'testing': settings.testing
    }


@app.post('/cases/', response_model=schemas.Case)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case:
        return db_case
    return crud.create_case(db=db, case=case)


@app.get('/cases/{case_id}', response_model=schemas.Case)
def read_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case


@app.get('/cases/{case_id}/summaries', response_model=List[schemas.Summary])
def get_summaries_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found"
        )

    return db_case.summaries


@app.post('/cases/{case_id}/summaries', response_model=schemas.Summary)
async def create_summary_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found, post to /summaries to create new case and summary")

    new_summary = await(get_new_summary(db_case))

    return crud.create_summary(db=db, summary=new_summary, case_id=case_id)


@app.get('/cases/{case_id}/keywords', response_model=List[schemas.Keyword])
def get_keywords_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found"
        )

    return db_case.keywords


@app.post('/cases/{case_id}/keywords', response_model=schemas.Keyword)
async def create_keywords_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found, post to /keywords to create new case and keywords")

    new_keywords = await(get_new_keywords(db_case))

    return crud.create_keywords(db=db, keyword=new_keywords, case_id=case_id)


@app.post('/summaries', response_model=schemas.Summary)
async def create_summary(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case is None:
        db_case = crud.create_case(db=db, case=case)

    new_summary = await(get_new_summary(db_case))

    return crud.create_summary(db=db, summary=new_summary, case_id=db_case.case_id)


@app.post('/keywords', response_model=schemas.Keyword)
async def create_keywords(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case is None:
        db_case = crud.create_case(db=db, case=case)

    new_keywords = await(get_new_keywords(db_case))

    return crud.create_keywords(db=db, keyword=new_keywords, case_id=db_case.case_id)
