from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
import crud
from utils.utils import get_db

import openai
from secrets import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY


router = APIRouter(
    tags=["summaries"],
)


async def get_new_summary(case: schemas.Case):
    prompt = "I need to summarize the important points of the following story for a legal case: {}\n\nI create a brief, three-sentence summary:".format(
        case.narrative)

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.8,
        max_tokens=80,
        frequency_penalty=0.2,
        presence_penalty=0.2
    )

    return response.choices[0]['text']


@router.post('/cases/{case_id}/summaries', response_model=schemas.Summary)
async def create_summary_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found, post to /summaries to create new case and summary")

    new_summary = await(get_new_summary(db_case))

    return crud.create_summary(db=db, summary=new_summary, case_id=case_id)


@router.post('/summaries', response_model=schemas.Summary)
async def create_summary(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case is None:
        db_case = crud.create_case(db=db, case=case)

    new_summary = await(get_new_summary(db_case))

    return crud.create_summary(db=db, summary=new_summary, case_id=db_case.case_id)
