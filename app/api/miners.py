from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.schemas.metrics import Metrics
from app.schemas.miner import Miner
from app.services.miners import *
from .utilities import validate_api_key

router = APIRouter()


@router.post('/register', status_code=201)
async def handle_register_miner(miner: Miner, api_key: str = Depends(validate_api_key)):
    try:
        await register_miner(miner)
        return {
            'message': 'Registered successfully'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/record', status_code=201)
async def handle_record_metrics(miner_data: Metrics, api_key: str = Depends(validate_api_key)):
    try:
        await record_metrics(miner_data)
        return {
            'message': 'Recorded successfully'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/devices', status_code=202)
async def handle_get_devices(api_key: str = Depends(validate_api_key)):
    miners = await get_miners()
    return [
        {
            'tag': m.tag,
            'name': m.name,
            'model': m.model,
            'is_active': await is_active(m.tag)
        }
        for m in miners
    ]


@router.get('/{tag}/metrics', status_code=202)
async def handle_get_current_metrics(tag: str, api_key: str = Depends(validate_api_key)):
    if not await is_registered(tag):
        raise HTTPException(status_code=404, detail='No miner with such tag found')
    
    if not await is_active(tag):
        return {
            'tag': tag,
            'active': False,
            'message': 'The miner is inactive'
        }

    metrics = await get_last_metrics(tag)
    return {
        'tag': tag,
        'active': await is_active(tag),
        'hashrate': metrics.hashrate,
        'power': metrics.power,
        'voltage': metrics.voltage,
        'time': metrics.time
    }


@router.get('/{tag}/history', status_code=202)
async def handle_get_metric_history(tag: str, param: str = Query(...), last_hours: int = Query(24), points: int = Query(500), api_key: str = Depends(validate_api_key)):
    if not await is_registered(tag):
        raise HTTPException(status_code=404, detail='No miner with such tag found')
    
    try:
        history = await get_metric_history(tag, param, last_hours, points)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'tag': tag,
        'active': await is_active(tag),
        'param': param,
        'last_hours': last_hours,
        'points': len(history),
        'data': history
    }
