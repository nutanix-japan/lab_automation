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

    # create tasks which depends on situation
    tasks = []
    print('check all hosts are down')
    if ops.is_all_host_down():
        print(' -> all hosts are down.')
        # nothing to do
    
    else:
        print(' -> 1 or more hosts are up.')
        print('check all cvms are down') 
        if ops.is_all_cvm_down():
            print(' -> all cvms are down.')
            tasks.append(ops.down_all_hosts)  
        else:
            print(' -> 1 or more cvms are up.')
            print('check cluster is up')
            if ops.is_cluster_up():
                print(' -> cluster is up')
                tasks.append(ops.down_over_cluster)
                tasks.append(ops.down_cluster)
            else:
                print(' -> cluster is down')
            tasks.append(ops.down_all_cvms)
            tasks.append(ops.down_all_hosts)

    # run tasks
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
