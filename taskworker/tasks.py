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
    time_limit = 30 * 60
    queue = settings.TASK_SQS_QUEUE

    def run_task(self, query_id, api_key, **params):
        try:
            print params
            mail_to = params.pop('emails', None)
            s3_path = params.pop('_s3_path', None)

            raw_payload = get_query_csv(query_id, api_key, **params)

            key = '{}/report_{}.csv'.format(str(query_id),
                    datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

            s3_bucket, s3_path_prefix = s3_path.split('/', 1)
            if not s3_bucket:
                s3_bucket = settings.REPORTS_S3_BUCKET

            if s3_path_prefix:
                key = '{}/{}'.format(s3_path_prefix, key)

            print s3_bucket, key

            # push to S3
            push_data_to_s3(s3_client, raw_payload, s3_bucket, key)

            # generate s3 signed URL, if emails provided
            if mail_to:
                # generate presigned URL
                url = generate_presigned_s3_url(s3_read_client, s3_bucket,
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
            else:
                print 'Emails not provided'
        except Exception as e:
            print e
            print str(e)
            print 'EXCEPTION'
            import traceback
            traceback.print_exc()

