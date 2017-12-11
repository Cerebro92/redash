from datetime import datetime

from kale import task
from taskworker import *
from taskworker.utils import *
from taskworker.utils import _fix_recipients_list

# TODO move these settings to config file
BUCKET = 'dev-dwh-redash-query-results'
S3_URL_EXPIRY_TIME = 60 * 60 * 24 * 10

EMAIL_FROM = 'noreply@delhivery.com'
EMAIL_SUBJECT = 'Daily NDR report'
EMAIL_BODY = 'Link: {}'

class PushToS3Task(task.Task):
    '''
    Defining Kale's class here just for pushing
    cls defination to SQS. actual function
    defination can be written in taskworkers
    '''
    max_retries = 3
    time_limit = 5
    queue = 'default'

    def run_task(self, query_id, api_key, **params):
        try:
            mail_to = params.get('emails')
            print params
            raw_payload = get_query_csv(query_id, api_key, **params)

            key = 'report_{}.csv'.format(datetime.now().strftime('%Y_%m_%d'))

            # push to S3
            push_data_to_s3(s3_client, raw_payload, BUCKET, key)

            # generate presigned URL
            url = generate_presigned_s3_url(s3_client, BUCKET,
                    key, S3_URL_EXPIRY_TIME, 'GET')

            EMAIL_TO = _fix_recipients_list(mail_to)
            EMAIL_CC = []
            is_sent = send_email(ses_client, EMAIL_FROM, EMAIL_TO,
                                EMAIL_CC, EMAIL_SUBJECT,
                                EMAIL_BODY.format(url))

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

