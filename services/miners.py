from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from database.crud import db
from database.models import Miner as MinerORM, Metric as MetricORM
from schemas.metrics import Metrics
from schemas.miner import Miner
from .config import THRESHOLD_SEC


cached_metrics: Dict[str, Metrics] = {}


class MinerService:
    async def get_miners(self) -> List[Miner]:
        miners = await db.get_all_miners()
        return [miner for miner in miners]
    

    async def register_miner(self, miner_in: Miner) -> Miner:
        miner = await db.get_miner(miner_in.tag)
        if miner:
            raise ValueError("Miner already exists")

        miner = await db.add_miner(
            tag=miner_in.tag,
            name=miner_in.name,
            model=miner_in.model,
        )

        return miner
    

    async def is_miner(self, tag: str) -> bool:
        return await db.is_miner_registered(tag)


    async def is_active(self, tag: str) -> bool:
        global cached_metrics

        last_seen = cached_metrics.get(tag)
        print(last_seen)
        if last_seen is None:
            last_seen = await db.get_last_seen(tag)
            if  last_seen is None:
                return False
        else:
            last_seen = last_seen.time

        print(datetime.now() - last_seen)
        return datetime.now() - last_seen < timedelta(seconds=THRESHOLD_SEC)


class MetricService:
    async def get_history(self, tag: str, param: str, last_hours: int = 24, points: int = 500) -> List[Dict]:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=last_hours)

        metrics = await db.get_metrics_by_miner_period(tag, start=start_time, end=end_time)
        if not all(hasattr(m, param) for m in metrics):
            raise ValueError(f"Invalid metric parameter: {param}")
        
        if len(metrics) > points:
            step = len(metrics) / points
            metrics = [metrics[int(i * step)] for i in range(points)]

        print('Metrics len is: ', len(metrics))

        return [
            {
                'time': m.time,
                'value': getattr(m, param)
            } 
            for m in metrics
        ]


    async def get_all(self, tag: str, limit: int = 100) -> List[Metrics]:
        metrics = await db.get_metrics_by_miner(tag, limit)
        result = []

        for m in metrics:
            miner_data = Metrics.from_orm(m)
            result.append(miner_data)

        return result
    

    async def get_last(self, tag: str) -> Optional[Metrics]:
        global cached_metrics

        latest_metrics = cached_metrics.get(tag)
        if latest_metrics is None:
            latest_metrics = await db.get_latest_metric(tag)

        if latest_metrics is not None:
            latest_metrics = Metrics.from_orm(latest_metrics)

        return latest_metrics
    

    async def record(self, metric_in: Metrics):
        global cached_metrics

        if not await db.is_miner_registered(metric_in.tag):
            raise ValueError("Unregistered miner")
        
        metric_in.time = datetime.now()
        cached_metrics[metric_in.tag] = metric_in

        await db.add_metric(
            tag=metric_in.tag,
            hashrate=metric_in.hashrate,
            power=metric_in.power,
            voltage=metric_in.voltage,
            time=metric_in.time
        )


miner_service = MinerService()
metric_service = MetricService()
