from kale import task


class PushToS3Task(task.Task):
    '''
    Defining Kale's class here just for pushing
    cls defination to SQS. actual function
    defination can be written in taskworkers
    '''
    max_retries = 3
    time_limit = 5
    queue = 'default'

    def run_task(self, *args, **kwargs):
        pass

