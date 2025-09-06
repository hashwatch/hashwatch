from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from schemas.metrics import MinerData
from schemas.miner import Miner
from services.miners import *
from .utilities import validate_api_key

router = APIRouter()


@router.post('/register')
async def handle_register_miner(miner: Miner, api_key: str = Depends(validate_api_key)):
    try:
        response = {
            'status': 200,
            'data': {}
        }
        response['data'] = await miner_service.register_miner(miner)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/record')
async def record_metrics(miner_data: MinerData, api_key: str = Depends(validate_api_key)):
    try:
        response = {
            'status': 200,
            'data': {}
        }
        response['data'] = await metric_service.record_metrics(miner_data)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/devices')
async def get_devices(api_key: str = Depends(validate_api_key)):
    response = {
        'status': 200,
        'data': {}
    }
    response['data'] = await miner_service.get_miners()
    return response


@router.get('/metrics')
async def get_metrics(api_key: str = Depends(validate_api_key)):
    response = {
        'status': 200, 
        'data': {}
    }

    miners = await miner_service.get_miners()
    for miner in miners:
        metrics = await metric_service.get_metrics(miner.tag)
        response['data'][miner.tag] = [m.dict() for m in metrics]

    return response
        

@router.get('/metrics/latest')
async def handle_get_latest_metrics(tag: Optional[str] = Query(None), api_key: str = Depends(validate_api_key)):
    response = {
        'status': 200,
        'data': {}
    }

    miners = await miner_service.get_miners()
    if tag:
        miners = [miner for miner in miners if miner.tag == tag]
    
    for miner in miners:
        metrics = await metric_service.get_metrics(miner.tag, limit=1)
        response['data'][miner.tag] = metrics[0]

    return response


@router.get('/metrics/{tag}')
async def handle_get_miner_metrics(tag: str, limit: Optional[int] = Query(1), api_key: str = Depends(validate_api_key)):
    response = {
        'status': 200,
        'data': {}
    }

    if not await miner_service.is_miner(tag):
        response['status'] = 400
        response['message'] = 'Miner is not found'
        return response

    metrics = await metric_service.get_metrics(tag=tag, limit=limit)
    response['data'][tag] = metrics

    return response