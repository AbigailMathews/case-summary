
from fastapi import APIRouter, Depends

from config import get_settings, Settings

router = APIRouter(
    tags=["status"],
)


@router.get('/')
async def root():
    return {'message': 'Hello OpenPolice'}


@router.get('/status')
async def get_status(settings: Settings = Depends(get_settings)):
    return {
        'environment': settings.environment,
        'testing': settings.testing
    }
