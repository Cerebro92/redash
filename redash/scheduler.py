from flask_apscheduler import APScheduler

from redash import models

class CustomAPScheduler(APScheduler):
    def add_job(self, task_params, scheduler_params):
        job = super(CustomAPScheduler, self).add_job(**scheduler_params)
        # TODO check, job is created ?
        periodic_task = models.PeriodicTask(**task_params)
        models.db.session.add(periodic_task)
        models.db.session.commit()
        return job

    def get_jobs(self, *args, **kwargs):
       jobs = super(CustomAPScheduler, self).get_jobs(*args, **kwargs)

       # TODO
       # fetch user information from user_job table
       # and add this info in jobs list
       # and return
       return jobs

