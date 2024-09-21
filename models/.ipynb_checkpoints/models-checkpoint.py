from sqlalchemy.sql import func
from datetime import datetime, timedelta

try:
    from sqlalchemy.orm import declarative_base
except:
    from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, String, DateTime, Enum, Index, Boolean, Integer, Date, Interval
from models import utils
from models.consts import TaxiTypes


BASE = declarative_base(cls=utils.Model)

SCHEMA = 'scrapping'

STATUS_ENUM = Enum(TaxiTypes, name='TaxiTypes', schema=SCHEMA, create_type=True)


class DimFiles(BASE):  # Data Model / Model
    __tablename__ = 'dim_files'

    uri = Column(String, primary_key=True, )
    type = Column(String, nullable=False, )
    date = Column(Integer, nullable=True)
    downloaded = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index(
            'idx_users', 'uri',
        ),
        {'extend_existing': True, 'schema': SCHEMA, }
    )


# 'iso': 'ETH',
#   'name': 'Ethereum',
#   'slug': 'ethereum',
#   'ingestionStart': '2015-08-09',
#   'interval': '1d',
class DimCoin(BASE):  # Data Model / Model
    __tablename__ = 'dim_coins'

    iso = Column(String, primary_key=True, )
    name = Column(String, nullable=False, )
    slug = Column(Integer, nullable=True)
    ingestion_start = Column(Date, nullable=False, default=False)
    interval = Column(Interval, nullable=False, default=timedelta(days=1))
    
    active = Column(Boolean, nullable=False, default=False)
    collected = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index(
            'idx_users', 'uri',
        ),
        {'extend_existing': True, 'schema': SCHEMA, }
    )
