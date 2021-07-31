from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session

import openai
import os
import json

from config import get_settings, Settings
import crud
import models
import schemas
from database import SessionLocal, engine

from secrets import OPENAI_API_KEY

models.Base.metadata.create_all(bind=engine)

openai.api_key = OPENAI_API_KEY

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_new_summary(case: schemas.Case):
    prompt = """
    A lawyer receives the following case narrative and needs to create a summary:
    ###
    {}
    ###
    The lawyer submits the following three-sentence case summary:
    ###
    """.format(case.narrative)

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.4,
        max_tokens=300,
        top_p=1.0,
        frequency_penalty=0.6,
        presence_penalty=0.2,
        stop=["\n\n\n"]
    )

    return response.choices[0]['text']


async def get_keywords(case: schemas.Case):
    response = openai.Completion.create(
        engine="davinci",
        prompt="""
        Text: {}
        Keywords:
        """.format(case.narrative),
        temperature=0.3,
        stream=true,
        max_tokens=40,
        top_p=1,
        frequency_penalty=0.6,
        presence_penalty=0.4,
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


@app.post('/summaries', response_model=schemas.Summary)
async def create_summary(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case is None:
        db_case = crud.create_case(db=db, case=case)

    new_summary = await(get_new_summary(db_case))

    return crud.create_summary(db=db, summary=new_summary, case_id=db_case.case_id)
