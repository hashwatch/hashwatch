from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from schemas.metrics import Metrics
from schemas.miner import Miner
from services.miners import *
from .utilities import validate_api_key

router = APIRouter()


@router.post('/register', status_code=201)
async def handle_register_miner(miner: Miner, api_key: str = Depends(validate_api_key)):
    try:
        await miner_service.register_miner(miner)
        return {
            'message': 'Registered successfully'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/record', status_code=201)
async def record_metrics(miner_data: Metrics, api_key: str = Depends(validate_api_key)):
    try:
        await metric_service.record(miner_data)
        return {
            'message': 'Recorded successfully'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/devices', status_code=202)
async def get_devices(api_key: str = Depends(validate_api_key)):
    miners = await miner_service.get_miners()
    return [
        {
            'tag': m.tag,
            'name': m.name,
            'model': m.model,
            'is_active': await miner_service.is_active(m.tag)
        }
        for m in miners
    ]


@router.get('/{tag}/metrics', status_code=202)
async def get_current_metrics(tag: str, api_key: str = Depends(validate_api_key)):
    if not await miner_service.is_miner(tag):
        raise HTTPException(status_code=404, detail='No miner with such tag found')
    
    if not await miner_service.is_active(tag):
        return {
            'tag': tag,
            'active': False,
            'message': 'The miner is inactive'
        }

    metrics = await metric_service.get_last(tag)
    return {
        'tag': tag,
        'active': await miner_service.is_active(tag),
        'hashrate': metrics.hashrate,
        'power': metrics.power,
        'voltage': metrics.voltage,
        'time': metrics.time
    }


@router.get('/{tag}/history', status_code=202)
async def get_metric_history(tag: str, param: str = Query(...), last_hours: int = Query(24), points: int = Query(500), api_key: str = Depends(validate_api_key)):
    if not await miner_service.is_miner(tag):
        raise HTTPException(status_code=404, detail='No miner with such tag found')
    
    try:
        history = await metric_service.get_history(tag, param, last_hours, points)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'tag': tag,
        'active': await miner_service.is_active(tag),
        'param': param,
        'last_hours': last_hours,
        'points': len(history),
        'data': history
    }
