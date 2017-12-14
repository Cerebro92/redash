import uuid
from datetime import datetime

from flask import current_app, request

from redash import models
from redash import settings
from redash.handlers.base import BaseResource
from taskworker import tasks

def update_model(model, updates):
    for k, v in updates.items():
        setattr(model, k, v)

def create_or_update_job(job_params, user, action='create'):
    # periodic Task params
    # job_params = payload['periodicjob']
    # job_params = payload

    # pop trigger params
    trigger = job_params['trigger']
    trigger_params = job_params['triggerparams']
    trigger_params['trigger'] = trigger

    # query params
    query_params = job_params.get('queryparams', {})

    # scheduler params
    scheduler_params = dict({
        'func': publish,
        'name': job_params['name'],
        'args': (job_params['query_id'], settings.GLOBAL_API_KEY),
        'kwargs': dict(query_params, **{'name': job_params['name']}),
        }, **trigger_params)

    if action == 'create':
        # add schduler JOB ID
        scheduler_params['id'] = str(uuid.uuid4())
        job = current_app.apscheduler.add_job(**scheduler_params)
    else:
        scheduler_params['id'] = job_params['task']['id']
        job = current_app.apscheduler.modify_job(**scheduler_params)

    periodic_job_def = dict(
        name=job_params['name'],
        description=job_params['description'],
        user_id=user.id,
        task_id=job.id,
        query_id=job_params['query_id']
    )

    if action == 'create':
        periodic_job = models.PeriodicJob(**periodic_job_def)
        models.db.session.add(periodic_job)
        models.db.session.flush()
        models.db.session.commit()
    else:
        # ID
        job_id = job_params.get('id')
        if job_id:
            periodic_job = models.PeriodicJob.query.get(job_id)
            update_model(periodic_job, periodic_job_def)
            models.db.session.commit()

    return periodic_job


class PeriodicJobResource(BaseResource):
    def post(self, job_id):
        # logic to update periodic task
        payload = request.get_json()
        job = models.PeriodicJob.query.get(job_id)
        if payload.get('pause'):
            current_app.apscheduler.pause_job(job.task_id)
        elif payload.get('resume'):
            current_app.apscheduler.resume_job(job.task_id)
        else:
            job = create_or_update_job(payload, self.current_user,
                    action='update')

        return job.to_dict()

    def get(self, job_id):
        task = models.PeriodicJob.query.get(job_id)
        return task.to_dict()

def publish(*args, **kwargs):
    return tasks.PushToS3Task.publish(None, *args, **kwargs)


class PeriodicJobListResource(BaseResource):
    def get(self, *args, **kwargs):

        uts = models.PeriodicJob.query.all()
        return [ut.to_dict() for ut in uts]

    def post(self, *args, **kwargs):
        # create JOB
        job = create_or_update_job(request.get_json(), self.current_user,
                action='create')

        return job.to_dict()

