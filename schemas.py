from typing import List, Optional

from pydantic import BaseModel


class SummaryBase(BaseModel):
    pass


class SummaryCreate(SummaryBase):
    pass


class Summary(SummaryBase):
    id: int
    case_id: int
    summary: str

    class Config:
        orm_mode = True


class KeywordBase(BaseModel):
    pass


class KeywordCreate(KeywordBase):
    pass


class Keyword(KeywordBase):
    id: int
    case_id: int
    keyword: str

    class Config:
        orm_mode = True


class CaseBase(BaseModel):
    case_id: int
    narrative: str


class CaseCreate(CaseBase):
    pass


class Case(CaseBase):
    summaries: List[Summary] = []
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True
