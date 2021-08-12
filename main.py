from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

import models
from database import engine, SessionLocal

from secrets import API_KEY, API_KEY_NAME

from api import status, cases, summaries, keywords


models.Base.metadata.create_all(bind=engine)

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API Key'
        )


description = """
OpenPolice Summary and Keyword Generation API uses GPT-3 to generate case summaries. 🚀

## Cases

You can **Create Cases** with a case number and a summary.
You can also **Get Cases**, **Get Case Summaries** and **Get Case Keywords** for cases by supplying a case number.

## Summaries

**Create Summaries** either by providing an already-created case id, or create a case and summary together by posting to /summaries

## Keywords

**Create Keywords** either by providing an already-created case id, or create a case and keywords together by posting to /keywords

"""

app = FastAPI(
    title="OpenPolice AI Case Summaries",
    description=description,
    version="0.0.1",
    contact={
        "name": "Abigail Mathews",
        "url": "https://abigailmathews.com",
        "email": "hi@abigailmathews.com",
    },
    dependencies=[Security(get_api_key)]
)

app.include_router(cases.router)
app.include_router(summaries.router)
app.include_router(keywords.router)
app.include_router(status.router)
