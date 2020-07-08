import json
import os
import sys
import time
from client_foundation import NutanixFoundationClient


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
    fvm = j['fvm']
    foundation = j['foundation']
    ops = Ops(cluster, nodes, fvm, foundation)

    # run ops tasks
    tasks = [
        ops.connect_to_fvm,
        ops.check_ipmi_mac,
        ops.check_ipmi_ip,
        ops.set_foundation_settings,
        ops.configure_ipmi_ip,
        ops.pre_check,
        ops.start_foundation,
        ops.poll_progress
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

    def __init__(self, cluster, nodes, fvm, foundation):
        # cluster
        self.external_ip = cluster['external_ip']
        self.cluster_name = cluster['name']
        self.netmask = cluster['netmask']
        self.gateway = cluster['gateway']
        self.name_server = cluster['name_server']
        self.ntp_server = cluster['ntp_server']

        # nodes
        self.nodes = nodes

        # fvm
        self.fvm = fvm

        # foundation
        self.aos_version = foundation['aos_version']
        self.nos_package = ''
        for nos_package in fvm["nos_packages"]:
            if nos_package['version'] == self.aos_version:
                self.nos_package = nos_package['file']
        if self.nos_package == '':
            raise Exception('choosed aos image does not exist.')

    def connect_to_fvm(self):
        print('connect_to_fvm()')
        ips = self.fvm['ips']
        user = self.fvm['user']
        password = self.fvm['password']
        print('candidates: {}'.format(ips))
        print('credential: {}, {}'.format(user, password))

        found = False
        for ip in ips:
            try:
                client = NutanixFoundationClient(ip, user, password)

                (success, result) = client.get_progress()
                if not success:
                    raise Exception(
                        'failed to get progress. {}'.format(json.dumps(result)))
                if not result['imaging_stopped']:
                    raise Exception('imaging now')

                (success, nos_packages) = client.get_nos_packages()
                if not success:
                    raise Exception(
                        'failed to get nos packages. {}'.format(json.dumps(result)))
                if not self.nos_package in nos_packages:
                    raise Exception(
                        'nos package {} is not in fvm'.format(self.aos_version))

                print('fvm:{} is ready'.format(ip))
                self.client = client
                found = True
                break
            except Exception as e:
                print('fvm:{} is not ready. Reason "{}"'.format(ip, e))

        return found

    def check_ipmi_mac(self):
        print('check_ipmi_mac()')
        problem_mac_list = []
        for node in self.nodes:
            position = node['position'].upper()
            print('node position: {}'.format(position))

            # MAC address check
            ipmi_mac = node['ipmi_mac']
            result = self.client.does_mac_exist(ipmi_mac, 'eth0')
            if not result:
                print('ipmi mac "{}" does not exist on the segment'.format(ipmi_mac))
                problem_mac_list.append(ipmi_mac)
            else:
                text = 'ipmi mac "{}" exists on the segment'.format(ipmi_mac)
            print(text)

        return len(problem_mac_list) == 0

    def check_ipmi_ip(self):
        print('check_ipmi_ip()')
        problem_ip_list = []
        for node in self.nodes:
            position = node['position'].upper()
            print('node position: {}'.format(position))

            ipmi_mac = node['ipmi_mac'].lower()
            ipmi_ip = node['ipmi_ip']
            (success, result) = self.client.get_mac_from_ip(ipmi_ip)
            exist = result['exist']
            found_mac = result['mac'].lower()

            if not result['exist']:
                print('ipmi ip "{}" does not exist'.format(ipmi_ip))
            elif ipmi_mac == found_mac:
                print('the ipmi already has ip "{}"'.format(ipmi_ip))
            else:
                print('ipmi ip "{}" is already used by another host "{}".'.format(
                    ipmi_ip, found_mac))
                problems.append(ipmi_ip)

        return len(problem_ip_list) == 0

    def set_foundation_settings(self):
        print('reset foundation vm')
        (success, result) = self.client.reset_state()
        if not success:
            print('failed to reset')
            return False

        print('get nic address list')
        (success, nics) = self.client.get_nics()
        if not success:
            print("Failed to get nic list")
            return False

        primary_nic = ''
        for (nic, nic_info) in nics.items():
            if nic_info['name'].lower() == 'eth0':
                primary_nic = nic
                break
        if primary_nic == '':
            print('foundation vm has no eth0')
            return False

        print('set eth0 as primary nic')
        (success, result) = self.client.choose_primary_nic(primary_nic)
        if not success:
            print('failed to set eth0 as primary nic')
            return False
        return True

    def get_nodeinfo_list(self):
        nodeinfo_list = []
        for node in self.nodes:
            nodeinfo = (node['ipmi_mac'], node['ipmi_ip'], node['host_ip'],
                        node['cvm_ip'], node['host_name'], node['position'])
            nodeinfo_list.append(nodeinfo)
        return nodeinfo_list

    def configure_ipmi_ip(self):
        print('configure ipmi ip. may take few minutes')
        nodeinfo_list = self.get_nodeinfo_list()
        (success, result) = self.client.ipmi_config(
            self.netmask, self.gateway, nodeinfo_list, self.cluster_name,
            self.external_ip, self.name_server, self.ntp_server, self.nos_package)

        if not success:
            print('failed to configure ipmi ip. reason "{}"'.format(
                result['error']))
        return success

    def pre_check(self):
        print('pre check. may take few minutes')
        nodeinfo_list = self.get_nodeinfo_list()
        (success, result) = self.client.pre_check(
            self.netmask, self.gateway, nodeinfo_list, self.cluster_name,
            self.external_ip, self.name_server, self.ntp_server, self.nos_package)

        if not success:
            print('failed to pre check. reason "{}"'.format(result['error']))
        return success

    def start_foundation(self):
        print('kick imaging nodes')
        nodeinfo_list = self.get_nodeinfo_list()
        (success, result) = self.client.image_nodes(
            self.netmask, self.gateway, nodeinfo_list, self.cluster_name,
            self.external_ip, self.name_server, self.ntp_server, self.nos_package)
        if not success:
            print('failed to kick imaging. reason "{}"'.format(
                result['error']))
        return success

    def poll_progress(self):
        count = 0
        max_count = 5
        aggregate_percent = 0
        ABORTED = -1
        STOPPED = -2
        ERROR = -3
        print('keep pooling progress till end(finish or error)')
        while True:
            try:
                (success, result) = self.client.get_progress()
                if not success:
                    raise

                aggregate_percent = result['aggregate_percent_complete']
                print('progress: {}'.format(aggregate_percent))
                if aggregate_percent == 100:
                    break
                else:
                    if 'abort_session' in result:
                        if result['abort_session'] == True:
                            aggregate_percent = ABORTED
                            break
                    elif result['imaging_stopped'] == True:
                        aggregate_percent = STOPPED
                        break
                count = 0

            except:
                count += 1
                if count > max_count:
                    aggregate_percent = ERROR
                    break

            time.sleep(5)

        if aggregate_percent == ABORTED:
            print('imaging was aborted')
        elif aggregate_percent == STOPPED:
            print('imaging was stopped')
        elif aggregate_percent == ERROR:
            print('imaging failed with unexpected error')
        else:
            return True
        return False


if __name__ == '__main__':
    main()
