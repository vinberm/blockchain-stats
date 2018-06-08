#! /usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import flags

FLAGS = flags.FLAGS

_ENGINE = None
_MAKER = None

def get_session(autocommit=True, expire_on_commit=False):
	"""Helper method to grab session"""
	global _ENGINE
	global _MAKER
	if not _MAKER:
		if not _ENGINE:
			_ENGINE = create_engine(FLAGS.sql_connection,
				pool_size = FLAGS.sql_pool_size, 
				max_overflow = 20,
				pool_recycle=FLAGS.sql_idle_timeout,
				poolclass=QueuePool,
				echo=False)
		_MAKER = (sessionmaker(bind=_ENGINE,
			autocommit=autocommit,
			autoflush=False,
			expire_on_commit=expire_on_commit))
	session = _MAKER()
	return session

def session_begin():
	session = get_session()
	return session

def session_close():
	session = get_session()
	session.close()
	
