from typing import List
from database.crud import db
from database.models import Miner as MinerORM, Metric as MetricORM
from schemas.metrics import MinerData
from schemas.miner import Miner


class MinerService:
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
        miner = await db.get_miner(tag)
        return miner is not None


    async def get_miners(self) -> List[Miner]:
        miners = await db.get_all_miners()
        return [miner for miner in miners]


class MetricService:
    async def record_metrics(self, metric_in: MinerData) -> MinerData:
        miner = await db.get_miner(metric_in.tag)
        if not miner:
            raise ValueError("Unregistered miner")

        metric = await db.add_metric(
            tag=metric_in.tag,
            hashrate=metric_in.hashrate,
            power=metric_in.power,
            voltage=metric_in.voltage,
        )

        return metric

    async def get_metrics(self, tag: str, limit: int = 100) -> List[MinerData]:
        metrics = await db.get_metrics_by_miner(tag, limit)
        result = []

        for m in metrics:
            miner_data = MinerData(
                tag=m.miner_tag,
                hashrate=m.hashrate,
                power=m.power,
                voltage=m.voltage
            )
            result.append(miner_data)

        return result


miner_service = MinerService()
metric_service = MetricService()
