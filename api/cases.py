from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal
from utils.utils import get_db

router = APIRouter(
    tags=["cases"],
)


@router.post('/cases/', response_model=schemas.Case)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case.case_id)
    if db_case:
        return db_case
    return crud.create_case(db=db, case=case)


@router.get('/cases/{case_id}', response_model=schemas.Case)
def read_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case


@router.get('/cases/{case_id}/summaries', response_model=List[schemas.Summary])
def get_summaries_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found"
        )

    return db_case.summaries


@router.get('/cases/{case_id}/keywords', response_model=List[schemas.Keyword])
def get_keywords_for_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(
            status_code=404, detail="Case not found"
        )

    return db_case.keywords
