import flask
import json
import os
import requests
import subprocess
import threading
import traceback
import time
import uuid
from collections import OrderedDict

# params
HOST = os.environ['API_BULK_HOST']
PORT = int(os.environ['API_BULK_PORT'])
API_FOUNDATION_HOST = os.environ['API_FOUNDATION_HOST']
API_FOUNDATION_PORT = int(os.environ['API_FOUNDATION_PORT'])
API_EULA_HOST = os.environ['API_EULA_HOST']
API_EULA_PORT = int(os.environ['API_EULA_PORT'])
API_SETUP_HOST = os.environ['API_SETUP_HOST']
API_SETUP_PORT = int(os.environ['API_SETUP_PORT'])

DEBUG = True
POLLING_INTERVAL = 5

# app and state
app = flask.Flask('API BULK ACTIONS')
tasks = OrderedDict()


@app.route('/api/public/bulkactions/v1/tasks/')
def handle_tasks():
    # clean up tasks
    now = int(time.time())
    del_uuids = []
    for task in tasks.values():
        if now - task['timestamp_start'] > 3 * 24 * 60 * 60:
            del_uuids.append(task['uuid'])
    for del_uuid in del_uuids:
        del tasks[del_uuid]

    # create list
    task_list = []
    for task_original in tasks.values():
        task = {}
        for key, value in task_original.items():
            if key == 'log':
                continue
            task[key] = value
        task['log'] = 'please specify task uuid to get log'
        task_list.append(task)

    # sort by timestamp. New(large) -> Old(small)
    task_list.sort(key=lambda task: task['timestamp_start'], reverse=True)
    return flask.jsonify(task_list)


@app.route('/api/public/bulkactions/v1/tasks/<task_uuid>')
def handle_task(task_uuid):
    if task_uuid not in tasks:
        d = {'error': 'resource not found'}
        return flask.jsonify(d, 404)

    task_original = tasks[task_uuid]
    task = {}
    for key, value in task_original.items():
        if key == 'log':
            continue
        task[key] = value
    task['log'] = '\n'.join(task_original['log'])
    return flask.jsonify(task)


@app.route('/api/public/bulkactions/v1/foundation', methods=['POST'])
def handle_run():
    try:
        data = json.loads(flask.request.get_data().decode())
        name = f'foundation-eula-setup for {data["cluster"]["name"]}'
        task_uuid = str(uuid.uuid4())
        parent_task_uuid = data['parent_uuid'] if ('parent_uuid' in data) else ''
        
        data['parent_uuid'] = task_uuid
        json_string = json.dumps(data)
        urls = [
            f'http://{API_FOUNDATION_HOST}:{API_FOUNDATION_PORT}/api/public/foundation/v1/run',
            f'http://{API_EULA_HOST}:{API_EULA_PORT}/api/public/eula/v1/run',
            f'http://{API_SETUP_HOST}:{API_SETUP_PORT}/api/public/setup/v1/run',
        ]
        t = threading.Thread(target=do_bulkaction, args=(name, task_uuid, parent_task_uuid, urls, json_string))
        t.start()
        return flask.jsonify({'uuid': task_uuid})
    except Exception as e:
        print(traceback.format_exc())
        return flask.jsonify({'error': str(e)}), 500


def do_bulkaction(name, task_uuid, parent_task_uuid, urls, json_string):
    # prepare
    tasks[task_uuid] = {
        'name': name,
        'uuid': task_uuid,
        'parent_uuid': parent_task_uuid,
        'log': [''] * len(urls),
        'progress': 0,
        'timestamp_start': int(time.time()),
        'timestamp_end': -1,
        'finished': False,
        'success': False,
    }

    # handle each actions
    for index, url in enumerate(urls):
        try:
            # create child task
            result = requests.post(url, data=json_string)
            if not result.ok:
                raise Exception('create child task result: not ok')
            child_task_url = result.json()['task_url']
            time.sleep(POLLING_INTERVAL)

            # polling child task
            while True:
                result = requests.get(child_task_url)
                if not result.ok:
                    raise Exception('polling child task result: not ok')
                j = result.json()
                tasks[task_uuid]['log'][index] = j['log']

                if j['finished']:
                    if not j['success']:
                        raise Exception('child task failed')
                    break

                time.sleep(POLLING_INTERVAL)

        except Exception as e:
            error_log = 'calling api server failed.\n'
            error_log += f'url: {url}\n'
            error_log += f'reason: {str(e)}\n'
            error_log += 'abort.'
            print(error_log, flush=True)
            tasks[task_uuid]['log'][index] += error_log
            break

        if index == len(urls) -1:
            tasks[task_uuid]['success'] = True

    # end
    tasks[task_uuid]['timestamp_end'] = int(time.time())
    tasks[task_uuid]['finished'] = True





if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
