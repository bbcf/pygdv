from sqlalchemy import *
from migrate import *
from pygdv.model import DeclarativeBase
from sqlalchemy.types import *
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

DeclarativeBase = declarative_base()
metadata = MetaData()


class Job(DeclarativeBase):
    __tablename__ = 'Job'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)
    _created = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=True)
    status = Column(Unicode(255))
    ext_task_id = Column(VARCHAR(255), unique=True)
    data = Column(Text())
    output = Column(VARCHAR(255))

# new jobs Column
bioscript_url = Column('bioscript_url', VARCHAR(255))
traceback = Column('traceback', Text, nullable=True)
# delete jobs Column
data = Column('data', Text())
output = Column('output', VARCHAR(255))


results_table = Table('Bresult', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('job_id', Integer, ForeignKey('Job.id', ondelete="CASCADE"), nullable=False),
    #relationship('Job'),
    Column('output_type', VARCHAR(255)),
    Column('is_file', Boolean, default=True, nullable=False),
    Column('path', VARCHAR(255), nullable=True),
    Column('name', VARCHAR(255), nullable=True),
    Column('data', Text, nullable=True),
    Column('is_track', Boolean, default=False, nullable=False),
    Column('track_id', Integer, ForeignKey('Track.id'), nullable=True)
    )


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    job_table = Table('Job', metadata, autoload=True)
    track_table = Table('Track', metadata, autoload=True)
    bioscript_url.create(job_table)
    traceback.create(job_table)
    job_table.c.data.drop()
    job_table.c.output.drop()
    results_table.create()


def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    job_table = Table('Job', metadata, autoload=True)
    data.create(job_table)
    output.create(job_table)
    job_table.c.bioscript_url.drop()
    job_table.c.traceback.drop()
    results_table.drop()
