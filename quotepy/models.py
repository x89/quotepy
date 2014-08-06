#!/usr/bin/env python
import werkzeug
import datetime
import hashlib
import uuid
import sys

from sqlalchemy import Integer, Column, String, DateTime, Enum
from sqlalchemy import create_engine, Text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base, declared_attr

# TODO fetch this from a config
engine = create_engine("sqlite:////tmp/quotepy.sqlite")
session = Session(engine)

class Base(object):
    """Base class which provides automated table names
    and a primary key column."""
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)

class HasDates(object):
    """Define attributes present on all dated content."""
    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

class Quote(HasDates, Base):
    quote_id = Column(String)

    raw = Column(Text)

    # We also need an accepted date
    acc_date = Column(DateTime)

    # We could have votes in a separate table but meh
    score = Column(Integer, default=0)

    status = Column(Enum("pending", "accepted", "removed"))

    def _create_id(self):
        # XXX This should organically grow as more is used, probably depending
        # on how often collissions occur.
        # Aside from that we should never repeat hashes which have been used before
        # without keeping the pastes in the database.
        return hashlib.sha224(str(uuid.uuid4())).hexdigest()[:8]

    def __init__(self, raw):
        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.quote_id = self._create_id()

        self.raw = raw
        self.status = "pending"

    def __repr__(self):
        return "<Quote(quote_id=%s)>" % (self.quote_id,)
