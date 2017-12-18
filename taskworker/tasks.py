from datetime import datetime

from kale import settings, task

from taskworker import *
from taskworker.utils import *
from taskworker.utils import _fix_recipients_list


class PushToS3Task(task.Task):
    '''
    Kale's class implementation
    '''
    max_retries = 3
    time_limit = 20
    queue = settings.TASK_SQS_QUEUE

    def run_task(self, query_id, api_key, **params):
        try:
            mail_to = params.pop('emails', None)
            print params
            raw_payload = get_query_csv(query_id, api_key, **params)

            key = '{}/report_{}.csv'.format(str(query_id),
                    datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

            # push to S3
            push_data_to_s3(s3_client, raw_payload, settings.REPORTS_S3_BUCKET, key)

            # generate presigned URL
            url = generate_presigned_s3_url(s3_read_client, settings.REPORTS_S3_BUCKET,
                    key, settings.S3_URL_EXPIRY_TIME, 'GET')

            EMAIL_TO = _fix_recipients_list(mail_to)
            EMAIL_CC = []
            EMAIL_SUBJECT = params.pop('name', settings.EMAIL_SUBJECT)
            is_sent = send_email(ses_client, settings.EMAIL_FROM, EMAIL_TO,
                            EMAIL_CC, EMAIL_SUBJECT,
                            settings.EMAIL_BODY.format(url))

            if is_sent:
                print 'Mail sent'
            else:
                print 'ISSUE'
        except Exception as e:
            print e
            print str(e)
            print 'EXCEPTION'
            import traceback
            traceback.print_exc()

