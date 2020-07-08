import flask
import json
import os
import subprocess
import threading
import time
import uuid
from collections import OrderedDict

# params
HOST = os.environ['API_SETUP_HOST']
PORT = int(os.environ['API_SETUP_PORT'])
DEBUG = True
COMMAND = "python3 -u setup.py -j '{}'"

# app and state
app = flask.Flask('API SETUP')
tasks = OrderedDict()


@app.route('/api/public/setup/v1/tasks/')
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


@app.route('/api/public/setup/v1/tasks/<task_uuid>')
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


@app.route('/api/public/setup/v1/run', methods=['POST'])
def handle_run():
    data = json.loads(flask.request.get_data().decode())
    name = f'setup for {data["cluster"]["name"]}'
    task_uuid = str(uuid.uuid4())
    parent_task_uuid = data['parent_uuid'] if 'parent_uuid' in data else ''

    json_string = json.dumps(data)
    t = threading.Thread(target=do_setup, args=(name, task_uuid, parent_task_uuid, json_string))
    t.start()
    return flask.jsonify({
            'uuid': task_uuid,
            'task_url': f'http://{HOST}:{PORT}/api/public/setup/v1/tasks/{task_uuid}'
        })


def do_setup(name, task_uuid, parent_task_uuid, json_string):
    # prepare
    tasks[task_uuid] = {
        'name': name,
        'uuid': task_uuid,
        'parent_uuid': parent_task_uuid,
        'log': [],
        'progress': 0,
        'timestamp_start': int(time.time()),
        'timestamp_end': -1,
        'finished': False,
        'success': False,
    }
    cmd = COMMAND.format(json_string)
    print(cmd)

    # run
    try:
        for line in get_lines(cmd=cmd):
            print(f'{task_uuid}: {line}', flush=True)
            tasks[task_uuid]['log'].append(line)
        tasks[task_uuid]['success'] = True
    except:
        # command returns non 0 exit code
        tasks[task_uuid]['success'] = False

    # end
    tasks[task_uuid]['timestamp_end'] = int(time.time())
    tasks[task_uuid]['finished'] = True


def get_lines(cmd):
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline()
        if line:
            yield line.decode().rstrip()
        if not line and proc.poll() is not None:
            break
    if proc.returncode != 0:
        raise Exception('failed')


if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
