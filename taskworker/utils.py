import requests
import urllib


def push_data_to_s3(client, body, bucket, key):
    r = client.put_object(Body=body, Bucket=bucket, Key=key)

    print "Uploaded file to bucket: {} key: {} reponse: {}".format(bucket, key, r)

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

REFRESH_URL = 'http://127.0.0.1:5000/api/queries/{}/refresh?api_key={}&'
RESULT_STATUS_URL = 'http://127.0.0.1:5000/api/jobs/{}?api_key={}'
RESULT_URL = 'http://127.0.0.1:5000/api/queries/{}/results/{}.csv?api_key={}'

def parametrize(d):
    for k, v in d.iteritems():
        if not k.startswith('p_'):
            d['p_' + k] = d.pop(k)
    return d

def get_query_csv(query_id, api_key, **params):

    # parmas modifications
    for k in ['start', 'end']:
        if params.get(k):
            params[k] = '2017-11-22 ' + params[k]

    # fetch JOB ID
    response = requests.post(\
            REFRESH_URL.format(query_id, api_key) +
            urllib.urlencode(parametrize(params)))

    print response.json()
    job_id = response.json()['job']['id']

    # Fetch Query Result ID
    # TODO make better
    query_result_id = None
    _wait_sec = 0
    while (not query_result_id):
        response = requests.get(RESULT_STATUS_URL.format(job_id, api_key))
        import time
        # time.sleep(_wait_sec)
        _wait_sec += 1
        print response.json()
        query_result_id = response.json()['job']['query_result_id']

    # Response
    response = requests.get(RESULT_URL.format(query_id, query_result_id, api_key))
    print response.text
    return response.text

def _fix_recipients_list(recipients_list):
    if isinstance(recipients_list, basestring):
        recipients_list = recipients_list.split(',')

    return recipients_list

