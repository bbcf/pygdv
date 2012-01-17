# -*- coding: utf-8 -*-

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import tg
from sqlalchemy import create_engine
from celery.conf import conf

        


def init_model(url):
    engine = create_engine(url, echo=False)
    Session = sessionmaker(autoflush=False, autocommit=False,
                     extension=ZopeTransactionExtension(), bind=engine)
    return Session

# Import your model modules here.
from pygdv.model.constants import *
from pygdv.model.database import Project, Sequence
from pygdv.model.auth import User



DBSession = init_model(conf['BROKER_HOST'])