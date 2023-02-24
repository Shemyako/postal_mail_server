"""
Models were rewrited to SQLAlchemy Core from ORM, so it could work with async
"""


from sqlalchemy import Table, Integer, String, Boolean, \
    Column, DateTime, Date, ForeignKey, Float, BigInteger, MetaData
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

metadata = MetaData()


Base = declarative_base()

# Пользователь
customers = Table('customers', metadata,
    Column("tg_id", Integer(), primary_key=True),
    Column("phone", String(20), nullable=True),
    Column("status", Integer(), nullable=True)
)

# Создаваемые почтовые ящики
mails = Table('mails', metadata,
    Column("id", Integer(), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("owner", Integer(), ForeignKey('customers.tg_id')),
    Column("is_active", Boolean(), nullable=False)
)


# Письма, приходящие на почтовые ящики
messages = Table('messages', metadata,
    Column("id", Integer, primary_key=True),
    Column("mail", Integer, ForeignKey('mails.id')),
    Column("text", String(255), nullable=False),
    Column("from_user", String(255), nullable=False),
    Column("date", DateTime(), nullable=False)  
)