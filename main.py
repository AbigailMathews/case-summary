from typing import Optional

from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from config import get_settings, Settings
import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_new_summary(case: schemas.Case):
    return "Dummy summary"


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
