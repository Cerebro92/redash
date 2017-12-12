import requests
import urllib

from taskworker.refresh import get_fresh_query_result


def push_data_to_s3(client, body, bucket, key):
    r = client.put_object(Body=body, Bucket=bucket, Key=key)

    # print "Uploaded file to bucket: {} key: {} reponse: {}"\
    #        .format(bucket, key, r)

    return r

def generate_presigned_s3_url(client, bucket, key, expires_in, method):
    url = client.generate_presigned_url('get_object',
                        Params={'Bucket': bucket, 'Key': key},
                        ExpiresIn=expires_in,
                        HttpMethod=method)
    return url

def send_email(client, _from, to, cc, subject, body):
    """
    Email
    """
    response = client.send_email(
        Source = _from,
        Destination = {
            'ToAddresses': to,
            'CcAddresses': cc
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': body
                }
            }
        })
    try:
        status = response['ResponseMetadata']['HTTPStatusCode'] == 200
    except KeyError:
        status = False

    return status

def parametrize(d):
    for k, v in d.iteritems():
        if not k.startswith('p_'):
            d['p_' + k] = d.pop(k)
    return d

def adjust_param_dates(params):
    # custom function to add suffix in date as suffix
    # in ['start', end] time
    todays_date = datetime.now().replace(
            hour=0, minute=0, second=0,
            microsecond=0)
    yesterdays_date = todays_date - timedelta(days=1)

    for k in params:
        if k in ['start']:
            param[k] = '{} {}'.format(todays_date.strftime("%Y-%m-%d"),
                    params[k])
        elif k in ['end']:
            param[k] = '{} {}'.format(yesterdays_date.strftime("%Y-%m-%d"),
                    params[k])
    return params

def get_query_csv(query_id, api_key, **params):

    # parm adjustments
    params = adjust_param_dates(params)
    res = get_fresh_query_result(settings.REDASH_URL, query_id, api_key,
            parametrize(params))
    return res

def _fix_recipients_list(recipients_list):
    if isinstance(recipients_list, basestring):
        recipients_list = recipients_list.split(',')

    return recipients_list

