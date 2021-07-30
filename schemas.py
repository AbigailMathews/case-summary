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


class CaseBase(BaseModel):
    case_id: int
    narrative: str


class CaseCreate(CaseBase):
    pass


class Case(CaseBase):
    summaries: List[Summary] = []

    class Config:
        orm_mode = True
