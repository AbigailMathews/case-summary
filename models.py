from sqlalchemy import Column, ForeignKey, Integer, UnicodeText, Unicode
from sqlalchemy.orm import relationship

from database import Base


class Case(Base):
    __tablename__ = 'cases'

    case_id = Column(Integer, primary_key=True, index=True)
    narrative = Column(UnicodeText)

    summaries = relationship('Summary', back_populates='case')
    keywords = relationship('Keyword', back_populates='case')


class Summary(Base):
    __tablename__ = 'summaries'

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'))
    summary = Column(UnicodeText)

    case = relationship('Case', back_populates='summaries')


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'))
    keyword = Column(Unicode)

    case = relationship('Case', back_populates='keywords')
