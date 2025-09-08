from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# class ApiKeys(Base):
#     __tablename__ = 'apikeys'

#     apikey:     Mapped[str] = mapped_column(String, primary_key=True, index=True)
#     is_active:  Mapped[bool] = mapped_column(Boolean, nullable=False)


class Miner(Base):
    __tablename__ = "miners"

    tag:        Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name:       Mapped[str] = mapped_column(String, nullable=False)
    model:      Mapped[str] = mapped_column(String, nullable=False)

    # References
    metrics:    Mapped[list["Metric"]] = relationship(back_populates="miner")


class Metric(Base):
    __tablename__ = "metrics"

    id:         Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    time:       Mapped[str] = mapped_column(DateTime)
    miner_tag:  Mapped[str] = mapped_column(ForeignKey("miners.tag"))
    hashrate:   Mapped[int] = mapped_column(Integer)
    power:      Mapped[int] = mapped_column(Integer)
    voltage:    Mapped[int] = mapped_column(Integer)
    
    # References
    miner:      Mapped[Miner] = relationship(back_populates="metrics")