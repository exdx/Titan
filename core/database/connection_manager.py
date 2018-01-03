import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey


db_name = 'core.db'
db_fullpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), db_name)

engine = create_engine('sqlite:///{}'.format(db_fullpath), connect_args={'check_same_thread': False}, echo=True)

metadata = MetaData()

OHLCV = Table('OHLCV', metadata,
              Column('ID', Integer, primary_key=True),
              Column('Exchange', String),
              Column('Pair', String),
              Column('Timestamp', String),
              Column('Open', Float),
              Column('High', Float),
              Column('Low', Float),
              Column('Close', Float),
              Column('Volume', Float),
              Column('Interval', String),
              )

TradingPairs = Table('TradingPairs', metadata,
                     Column('PairID', String, primary_key=True),
                     Column('BaseCurrency', String),
                     Column('QuoteCurrency', String),
                     )

TAIdentifier = Table('TAIdentifier', metadata,
                      Column('TA_ID', Integer),
                      Column('Description', String),
                      )

TAMovingAverage = Table ('TAMovingAverage', metadata,
                         Column('TA_Det_ID', Integer, primary_key=True),
                         Column('Pair', String),
                         Column('Time', String),
                         Column('Close', Float),
                         Column('INTERVAL', Integer),
                         Column('VALUE', Float),
                         )

TAVolumeChange = Table ('TAVolumeChange', metadata,
                         Column('TA_Det_ID', Integer, primary_key=True),
                         Column('Pair', String),
                         Column('Time', String),
                         Column('INTERVAL', Integer),
                         Column('VALUE', Float),
                         )

def drop_tables():
    print('Dropping tables...')
    metadata.drop_all(engine)

def create_tables():
    print('Creating tables...')
    metadata.create_all(engine)

def reset_db():
    print('Resetting database...')
    drop_tables()
    create_tables()