"""
Module contains function to refresh Redash API results

modeled after:
https://gist.github.com/arikfr/e3e434d8cfd7f331d499ccf351abbff9
"""

import requests
import time


def poll_job(s, redash_url, job):
    # TODO: add timeout
    while job['status'] not in (3,4):
        response = s.get('{}/api/jobs/{}'.format(redash_url, job['id']))
        job = response.json()['job']
        time.sleep(1)

    if job['status'] == 3:
        return job['query_result_id']

    return None

def get_fresh_query_result(redash_url, query_id, api_key, params):
    s = requests.Session()
    s.headers.update({'Authorization': 'Key {}'.format(api_key)})

    response = s.post('{}/api/queries/{}/refresh'.format(redash_url, query_id), params=params)

    if response.status_code != 200:
        raise Exception('Refresh failed.')

    result_id = poll_job(s, redash_url, response.json()['job'])

    if result_id:
        response = s.get('{}/api/queries/{}/results/{}.csv'.format(redash_url, query_id, result_id))
        if response.status_code != 200:
            raise Exception('Failed getting results.')
    else:
        raise Exception('Query execution failed.')

    # return response.json()['query_result']['data']['rows']
    return response.text

