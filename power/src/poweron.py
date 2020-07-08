import json
import os
import sys
import time
from power_ops import PowerOps

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
    nodes = j['nodes']
    ops = PowerOps(cluster, nodes)

    # run tasks
    tasks = [
        ops.up_all_host,
        ops.wait_till_all_host_becoming_accesible,
        ops.wait_till_all_cvm_up,
        ops.wait_till_all_cvm_accessible,
        ops.up_cluster,
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

if __name__ == '__main__':
    main()
