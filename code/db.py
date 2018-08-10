#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
import sqlalchemy.types
import logging
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class User(Base):
    __tablename__ = "USER"

    ID = Column(Integer, primary_key=True)
    AREA = Column(String)
    FOLLOWERS_COUNT = Column(Integer)
    MEDIA_TYPE = Column(String)
    MEDIA_ID = Column(Integer)
    DESCRIPTION = Column(String)
    VERIFIED_CONTENT = Column(String)
    SCREEN_NAME = Column(String)
    VISIT_COUNT_RECENT = Column(Integer)
    USER_AUTH_INFO = Column(String)
    NAME = Column(String)
    BIG_AVATAR_URL = Column(String)
    GENDER = Column(Integer)
    UGC_PUBLISH_MEDIA_ID = Column(String)
    FOLLOWINGS_COUNT = Column(Integer)
    ST = Column(Integer) #0 inited 1 filled 2 mlc data

class Content(Base):
    __tablename__ = "CONTENT"

    ID = Column(Integer, primary_key=True)
    PUBLISH_TIME = Column(Integer)
    CREATOR_UID = Column(Integer)
    MEDIA_ID = Column(Integer)
    SOURCE = Column(String)
    TITLE = Column(String)
    CITY = Column(String)
    IMAGE_LIST = Column(String)
    KEYWORDS = Column(String)
    LABEL = Column(String)
    CATEGORIES = Column(String)
    TAG = Column(String)
    URL = Column(String)
    ST = Column(Integer)
    DETAIL = Column(String)


class MyDB(object):
    def __init__(self):
        logging.info("database init")
        self.engine = create_engine("sqlite:///toutiao.db", pool_recycle=3600, echo=False)
        self.make_session = sessionmaker(bind=self.engine)
        self.metadata = MetaData(self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logging.info("create database tables")

if __name__ == "__main__":
    '''直接运行此文件来创建数据库'''
    mydb = MyDB()
    mydb.create_tables()
    print "DONE"