import json
import sys
import logging
import threading
import time
import os
import traceback
from client_eula import NutanixEulaClient


def main():
    # cd to script dir
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # parse command
    j = Parser.get_json()
    Parser.check_json(j)

    # create ops
    cluster = j['cluster']
    eula = j['eula']
    ops = Ops(cluster, eula)

    # run ops tasks
    tasks = [
        ops.set_password,
        ops.connect_to_prism,
        ops.set_eula,
        ops.set_initial_pulse,
        ops.set_initial_alert,
    ]
    for task in tasks:
        task_name = task.__name__
        print(task_name)
        if not task():
            print(f'task "{task_name}" failed. abort.')
            exit(1)


class Parser:
    @classmethod
    def get_json(cls):
        # load text
        text = ''
        if len(sys.argv) == 3:
            option = sys.argv[1].lower()
            if option == '-j':
                text = sys.argv[2]
            elif option == '-f':
                try:
                    with open(sys.argv[2], 'r') as fin:
                        text = fin.read()
                except:
                    print('file read error')
                    exit('-1')

        # has text
        if text == '':
            print('args error. ')
            print(' -f <json-file>')
            print(" -j '<json-string>'")
            exit('-1')

        # text -> json
        try:
            j = json.loads(text)
        except:
            print('json load error')
            exit(-1)
        return j

    @classmethod
    def check_json(cls, j):
        ...


class Ops:
    def __init__(self, cluster, eula):

        self.session = None
        self.ip = cluster['external_ip']
        self.user = cluster['user']
        self.password = cluster['password']

        self.initial_password = eula['initial_password']
        self.eula_user = eula['user']
        self.eula_company = eula['company']
        self.eula_title = eula['title']
        self.enable_pulse = eula['enable_pulse']

    def set_password(self):
        print(
            f'ip={self.ip}, initial_password={self.initial_password}, password={self.password}')
        (success, result) = NutanixEulaClient.change_default_system_password(
            self.ip, self.user, self.initial_password, self.password)
        if not success:
            print(f'failed to initialize prism password.')
            print(result)
        return success

    def connect_to_prism(self):
        print(f'ip={self.ip}, user={self.user}, password={self.password}')
        try:
            self.session = NutanixEulaClient(self.ip, self.user, self.password)
            return True
        except:
            print("failed to connect to prism")
        return False

    def set_eula(self):
        print(
            f'user={self.eula_user}, company={self.eula_company}, title={self.eula_title}')
        (success, result) = self.session.set_eula(
            self.eula_user, self.eula_company, self.eula_title)
        if not success:
            print(f"set eula failed. reason '{result['error']}'")
        return success

    def set_initial_pulse(self):
        print('enable={}'.format(self.enable_pulse))
        (success, result) = self.session.set_initial_pulse_enable(self.enable_pulse)
        if not success:
            print(f"set pulse failed. reason '{result['error']}'")
        return success

    def set_initial_alert(self):
        print('disable default nutanix email')
        (success, result) = self.session.disable_default_nutanix_email()
        if not success:
            print(f"set alert failed. reason '{result['error']}'")
        return success


if __name__ == '__main__':
    main()
