from sqlalchemy.orm import Session

import models
import schemas


def get_case(db: Session, case_id: int):
    return db.query(models.Case).filter(models.Case.case_id == case_id).first()


def create_case(db: Session, case: schemas.CaseCreate):
    db_case = models.Case(case_id=case.case_id, narrative=case.narrative)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def get_summary(db: Session, id: int):
    return db.query(models.Summary).filter(models.Summary.id == id).first()


def get_summaries(db: Session, case_id: int):
    return db.query(models.Summary).filter(models.Summary.case_id == case_id).all()


def create_summary(db: Session, summary: str, case_id: int):
    db_summary = models.Summary(summary=summary, case_id=case_id)
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


def get_keyword(db: Session, id: int):
    return db.query(models.Summary).filter(models.Summary.id == id).first()


def get_keywords(db: Session, case_id: int):
    return db.query(models.Keyword).filter(models.Keyword.case_id == case_id).all()


def create_keywords(db: Session, keyword: str, case_id: int):
    db_keyword = models.Keyword(keyword=keyword, case_id=case_id)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword
