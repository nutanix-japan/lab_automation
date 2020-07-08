import json
import sys
import threading
import time
import os
import traceback
from client_setup import NutanixSetupClient


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
    containers = j['containers']
    networks = j['networks']
    ipam_networks = j['ipam_networks']
    images = j['images']
    ops = Ops(cluster, containers, networks, ipam_networks, images)

    # run ops tasks
    tasks = [
        ops.connect_to_prism,
        ops.set_language,
        ops.delete_unused_containers,
        ops.create_containers,
        ops.delete_unused_networks,
        ops.create_networks,
        ops.create_ipam_networks,
        ops.create_images,
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
    def __init__(self, cluster, containers, networks, ipam_networks, images):
        self.session = None
        self.ip = cluster['external_ip']
        self.user = cluster['user']
        self.password = cluster['password']
        self.language = cluster['language']

        self.containers = containers
        self.networks = networks
        self.ipam_networks = ipam_networks
        self.images = images

    def connect_to_prism(self):
        print('ip={}, user={}, password={}'.format(
            self.ip, self.user, self.password))
        try:
            self.session = NutanixSetupClient(
                self.ip, self.user, self.password)
            return True
        except:
            print("failed to connect to prism")
        return False

    def set_language(self):
        print(f'language={self.language}')
        language = self.language.lower()
        lmap = {'en-us': 'en-US', 'ja-jp': 'ja-JP', 'zh-cn': 'zh-CN'}
        if language not in ['en-us', 'ja-jp', 'zh-cn']:
            print('failed to set language. {} not in {}'.format(
                self.language, ['en-US', 'ja-JP', 'zh-CN']))
            return False

        (success, result) = self.session.change_language(
            'admin', lmap[language])
        if not success:
            print("failed to set language. reason '{}'".format(
                result['error']))
        return success

    def delete_unused_containers(self):
        print('delete_unused_containers()')
        (success, existing_containers) = self.session.get_container_names()
        if not success:
            print("get container names failed.")
            return False

        for existing_container in existing_containers:
            (success, container_info) = self.session.get_container_info(
                existing_container)
            if not success:
                print("get container info failed")
                return False
            if container_info['usage'] != '0':
                continue

            (success, _) = self.session.delete_container(existing_container)
            if not success:
                print("delete container failed")
                return False
            else:
                print("delete container '{}'".format(existing_container))
        return True

    def create_containers(self):
        print('create_containers()')
        (success, existing_containers) = self.session.get_container_names()
        if not success:
            print("get container names failed.")
            return False

        task_list = []
        for container in self.containers:
            name = container['name']
            if name in existing_containers:
                continue
            (success, taskuuid) = self.session.create_container(name)
            if not success:
                print('create container failed')
                return False
            else:
                print("create container '{}'".format(name))
            task_list.append(taskuuid)

        # wait till end
        self.wait_tasks(task_list)
        return True

    def delete_unused_networks(self):
        print('delete_unused_networks()')
        (success, existing_networks) = self.session.get_network_names()
        if not success:
            print("session.get_network_names()")
            return False

        task_list = []
        for existing_network in existing_networks:
            (success, used) = self.session.is_network_used(existing_network)
            if not success:
                print("session.is_network_used() failed.")
                return False
            if used:
                continue

            (success, taskuuid) = self.session.delete_network(existing_network)
            if not success:
                print("session.delete_network() failed.")
                return False
            else:
                print("delete network '{}'".format(existing_network))
            task_list.append(taskuuid)

        self.wait_tasks(task_list)
        return True

    def create_networks(self):
        print('create_networks()')
        (success, existing_networks) = self.session.get_network_names()
        if not success:
            print("session.get_network_names() failed.")
            return False

        task_list = []
        for network in self.networks:
            name = network['name']
            vlan = network['vlan']
            if name in existing_networks:
                continue
            (success, taskuuid) = self.session.create_network(name, vlan)
            if not success:
                print("session.create_network() failed.")
                return False
            else:
                print("create network '{}'".format(name))
            task_list.append(taskuuid)

        self.wait_tasks(task_list)
        return True

    def create_ipam_networks(self):
        print('create_ipam_networks()')
        (success, hypervisor) = self.session.get_hypervisor()
        if not success:
            print("session.get_hypervisor() failed.")
            return False
        if hypervisor.lower() != 'ahv':
            return True

        (success, existing_networks) = self.session.get_network_names()
        if not success:
            print("session.get_network_names() failed.")

        task_list = []
        for ipam_network in self.ipam_networks:
            name = ipam_network['name']
            if name in existing_networks:
                continue

            vlan = ipam_network['vlan']
            network = ipam_network['network']
            prefix = ipam_network['prefix']
            gateway = ipam_network['gateway']
            pools = ipam_network['pools']
            dns = ipam_network['dns']
            (success, taskuuid) = self.session.create_network_managed(name, vlan, network,
                                                                      prefix, gateway, pools, dns)
            if not success:
                print("session.create_network_managed() failed.")
                return False
            else:
                print("create ipam network '{}'".format(name))
            task_list.append(taskuuid)

        self.wait_tasks(task_list)
        return True

    def create_images(self):
        print('create_images()')
        (success, existing_images) = self.session.get_image_names()
        if not success:
            print("session.get_image_names() failed.")
            return False

        (success, containers) = self.session.get_container_names()
        if not success:
            print("session.get_container_names() failed.")
            return False

        task_list = []
        for image in self.images:
            name = image['name']
            container = image['container']
            url = image['url']

            if name in existing_images:
                continue
            if container not in containers:
                print("container does not exist.")
                return False

            (success, taskuuid) = self.session.upload_image(url, container, name)
            if not success:
                print("session.upload_image() failed.")
                return False
            task_list.append(taskuuid)

        self.wait_tasks(task_list)
        return True

    def wait_tasks(self, uuids, interval=5):
        first = True
        while(True):
            (success, tasks) = self.session.get_tasks_status()
            if not success:
                print(tasks)
                continue
                #raise Exception('Error happens on getting tasks status.')

            finished = True
            for task in tasks:
                if task['uuid'] in uuids:
                    if first:
                        print(
                            'Wait till all tasks end. Polling interval {}s.'.format(interval))
                        first = False
                    print('{} {}% : {}'.format(
                        task['method'], task['percent'], task['uuid']))
                    finished = False
                else:
                    # Child or other task
                    pass

            if finished:
                break
            else:
                print('--')
            time.sleep(interval)

        if not first:
            print('All tasks end.')

if __name__ == '__main__':
    main()
