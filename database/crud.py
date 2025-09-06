import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

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


    async def add_metric(self, tag: str, hashrate: int, power: int, voltage: int) -> Metric:
        async with self.SessionLocal() as session:
            metric = Metric(
                miner_tag=tag,
                hashrate=hashrate,
                power=power,
                voltage=voltage,
            )
            session.add(metric)
            await session.commit()
            await session.refresh(metric)
            return metric


    async def get_metrics_by_miner(self, tag: str, limit: int = 100) -> List[Metric]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Metric)
                .where(Metric.miner_tag == tag)
                .order_by(Metric.time.desc())
                .limit(limit)
            )
            return result.scalars().all()


db = Database()