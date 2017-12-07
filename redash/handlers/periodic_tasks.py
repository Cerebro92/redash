from datetime import datetime

from flask import current_app, request

from redash import models
from redash.handlers.base import BaseResource
try:
    from taskworker import tasks
except ImportError:
    pass

# TODO
API_KEY = 'usNs3a8oxdZTIIy3BjelzfV8xXKe00UDF5Q16mhd'

class PeriodicTaskResource(BaseResource):
    def post(self, task_id):
        # logic to update periodic task
        payload = request.get_json()
        task = models.PeriodicTask.query.get(task_id)
        if payload.get('pause'):
            current_app.apscheduler.pause_job(task.task_id)
        elif payload.get('resume'):
            current_app.apscheduler.resume_job(task.task_id)
        return {'success': True}

    def get(self, task_id):
        task = models.PeriodicTask.query.get(task_id)
        return task.to_dict()

def publish(*args, **kwargs):
    return tasks.PushToS3Task.publish(None, *args, **kwargs)


class PeriodicTaskListResource(BaseResource):
    def get(self, *args, **kwargs):

        uts = models.PeriodicTask.query.all()
        return [ut.to_dict() for ut in uts]

    def post(self, *args, **kwargs):
        # call kale's job publish function here
        payload = request.get_json()

        # periodic Task params
        task_params = payload['periodictask']

        # pop trigger params
        trigger = task_params.pop('trigger', None)
        trigger_params = task_params.pop('trigger_params', {})
        trigger_params['trigger'] = trigger

        # query params
        query_params = payload.get('queryparams', {})

        # additional task params
        # task_params['created_at'] = datetime.now()

        import uuid
        import pickle
        task_id = unicode(uuid.uuid4())
        task_params['user_id'] = self.current_user.id
        task_params['task_id'] = task_id
        # task_params['params'] = pickle.dumps(query_params)

        # scheduler params
        scheduler_params = dict({
            'func': publish,
            'id': task_id,
            'name': task_params['name'],
            'args': (task_params['query_id'], API_KEY),
            'kwargs': query_params,
            }, **trigger_params)

        current_app.apscheduler.add_job(task_params, scheduler_params)
