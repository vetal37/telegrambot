from sqlalchemy import Table, Column, Integer, String, MetaData
meta = MetaData()

students = Table(
   'student', meta,
   Column('id', Integer, primary_key=True, unique=True),
   Column('name', String(80)),
   Column('phone', String(20)),
)