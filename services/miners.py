from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from database.crud import db
from database.models import Miner as MinerORM, Metric as MetricORM
from schemas.metrics import Metrics
from schemas.miner import Miner
from .config import THRESHOLD_SEC


cached_metrics: Dict[str, Metrics] = {}


async def get_miners() -> List[Miner]:
    miners = await db.get_all_miners()
    return [miner for miner in miners]


async def register_miner(miner_in: Miner) -> Miner:
    miner = await db.get_miner(miner_in.tag)
    if miner:
        raise ValueError("Miner already exists")

    miner = await db.add_miner(
        tag=miner_in.tag,
        name=miner_in.name,
        model=miner_in.model,
    )

    return miner


async def is_registered(miner_tag: str) -> bool:
    return await db.is_miner_registered(miner_tag)


async def is_active(tag: str) -> bool:
    global cached_metrics

    last_seen = cached_metrics.get(tag)
    if last_seen is None:
        last_seen = await db.get_last_seen(tag)
        if  last_seen is None:
            return False
    else:
        last_seen = last_seen.time

    return datetime.now() - last_seen < timedelta(seconds=THRESHOLD_SEC)


async def get_metric_history(tag: str, param: str, last_hours: int = 24, points: int = 500) -> List[Dict]:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=last_hours)

    metrics = await db.get_metrics_by_miner_period(tag, start=start_time, end=end_time)
    if not all(hasattr(m, param) for m in metrics):
        raise ValueError(f"Invalid metric parameter: {param}")
    
    if len(metrics) > points:
        step = len(metrics) / points
        metrics = [metrics[int(i * step)] for i in range(points)]

    return [
        {
            'time': m.time,
            'value': getattr(m, param)
        } 
        for m in metrics
    ]


async def get_all_metrics(tag: str, limit: int = 100) -> List[Metrics]:
    metrics = await db.get_metrics_by_miner(tag, limit)
    result = []

    for m in metrics:
        miner_data = Metrics.from_orm(m)
        result.append(miner_data)

    return result


async def get_last_metrics(tag: str) -> Optional[Metrics]:
    global cached_metrics

    latest_metrics = cached_metrics.get(tag)
    if latest_metrics is None:
        latest_metrics = await db.get_latest_metric(tag)

    if latest_metrics is not None:
        latest_metrics = Metrics.from_orm(latest_metrics)

    return latest_metrics


async def record_metrics(metrics: Metrics):
    global cached_metrics

    if not await db.is_miner_registered(metrics.tag):
        raise ValueError("Unregistered miner")
    
    metrics.time = datetime.now()
    cached_metrics[metrics.tag] = metrics

    await db.add_metric(
        tag=metrics.tag,
        hashrate=metrics.hashrate,
        power=metrics.power,
        voltage=metrics.voltage,
        time=metrics.time
    )
