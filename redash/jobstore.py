try:
    import cPickle as pickle
except ImportError:
    import pickle

from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.util import datetime_to_utc_timestamp

class CustomSQLAlchemyJobStore(SQLAlchemyJobStore):
	def add_job(self, job):
		insert = self.jobs_t.insert().values(**{
			'id': job.id,
			'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
			'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol)
		})
		try:
			with self.engine.connect() as conn:
				conn.execute(insert)
		except IntegrityError:
			raise ConflictingIdError(job.id)

	def update_job(self, job):
		update = self.jobs_t.update().values(**{
			'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
			'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol)
		}).where(self.jobs_t.c.id == job.id)

		with self.engine.connect() as conn:
			result = conn.execute(update)
			if result.rowcount == 0:
				raise JobLookupError(id)
