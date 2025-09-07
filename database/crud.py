import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, delete
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from .config import DB_PATH
from .models import Base, Miner, Metric


class Database:
    def __init__(self):
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{DB_PATH}",
            echo=False,
        )   
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


    async def close(self):
        await self.engine.dispose()


    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    #
    #   Miners
    #
    async def add_miner(self, tag: str, name: str, model: str) -> Miner:
        async with self.SessionLocal() as session:
            miner = Miner(tag=tag, name=name, model=model)
            session.add(miner)
            await session.commit()
            await session.refresh(miner)
            return miner


    async def get_miner(self, tag: str) -> Optional[Miner]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Miner).where(Miner.tag == tag)
            )
        return result.scalar_one_or_none()


    async def get_all_miners(self) -> List[Miner]:
        async with self.SessionLocal() as session:
            result = await session.execute(select(Miner))
            return result.scalars().all()


    # async def delete_miner(self, tag: str):
    #     async with self.SessionLocal() as session:
    #         stmt = delete(Miner).where(Miner.tag == tag)
    #         await session.execute(stmt)

    #
    #   Metrics
    #
    async def add_metric(self, tag: str, hashrate: int, power: int, voltage: int, time: datetime):
        async with self.SessionLocal() as session:
            metric = Metric(
                miner_tag=tag,
                hashrate=hashrate,
                power=power,
                voltage=voltage,
                time=time
            )
            session.add(metric)
            await session.commit()
            await session.refresh(metric)


    async def get_metrics_by_miner_period(self, tag: str, start: datetime, end: datetime) ->  List[Metric]:
        async with self.SessionLocal() as session:
            stmt = (
                select(Metric)
                .where(Metric.miner_tag == tag)
                # .where(Metric.time >= start)
                # .where(Metric.time <= end)
                .order_by(Metric.time.asc())
            )
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            return metrics


    async def get_metrics_by_miner(self, tag: str, limit: int = 100) -> List[Metric]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Metric)
                .where(Metric.miner_tag == tag)
                .order_by(Metric.time.desc())
                .limit(limit)
            )
            return result.scalars().all()
        

    async def get_latest_metric(self, tag: str) -> Optional[Metric]:
        metrics = await self.get_metrics_by_miner(tag, limit=1)
        return metrics[0] if metrics else None


    async def get_metrics_downsamples(tag: str, start: datetime, end: datetime, target_points: int) -> List[Metric]:
        pass


    #
    #   Utilities
    #
    async def get_last_seen(self, tag: str) -> Optional[datetime]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Metric)
                .where(Metric.miner_tag == tag)
                .order_by(Metric.time.desc())
                .limit(1)
            )

            metric = result.scalars().first()
            return metric.time if metric else None



    async def is_miner_registered(self, tag: str) -> bool:
        miner = await self.get_miner(tag)
        return miner is not None


    async def prune_old_metrics(self, older_than: datetime):
        async with self.SessionLocal() as session:
            stmt = (
                delete(Metric)
                .where(Metric.time < older_than)
            )
            await session.execute(stmt)
            await session.commit()


db = Database()