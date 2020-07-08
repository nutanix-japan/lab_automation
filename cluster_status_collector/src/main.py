import functools
import glob
import json
import os
import requests
import sys
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

import umongo
from client_foundation import NutanixFoundationClient

STATUS_CHECK_INTERVAL = 60
NUM_STATUS_CHECK_THREADS = 3

# change flush param to True for container threads
print = functools.partial(print, flush=True)


def main():
    # cd to script dir
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    mc_cluster, mc_cluster_status = get_mongo_collections()
    clusters = load_clusters()
    register_clusters(clusters, mc_cluster)
    loop_collecting_clusters_status(clusters, mc_cluster_status)


def get_mongo_collections():
    client = umongo.get_mongo_client()

    # initialize
    for db in client.list_databases():
        if db['name'] == 'cluster':
            client.drop_database('cluster')
            break

    # create db and collection
    mc_cluster = client['cluster']['clusters']
    mc_cluster_status = client['cluster']['clusters_status']
    return mc_cluster, mc_cluster_status


def load_clusters():
    clusters = []
    files = glob.glob('clusters/*')
    for file in files:
        try:
            with open(file, 'r') as fin:
                text = fin.read()
            j = json.loads(text)
            name = j['cluster']['name']
            cluster_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, name))
            j['name'] = name
            j['uuid'] = cluster_uuid
            clusters.append(j)
        except:
            print(f'loading json failed at "{file}". Skip.')
            print(traceback.format_exc())
    return clusters


def register_clusters(clusters, mc_cluster):
    print('register clusters')
    for cluster in clusters:
        print(f'- {cluster["name"]}')
    umongo.bulk_replace_upsert(
        collection=mc_cluster, key='uuid', docs=clusters)


def loop_collecting_clusters_status(clusters, mc_cluster_status):
    while(True):
        start = int(time.time())

        try:
            with ThreadPoolExecutor(max_workers=NUM_STATUS_CHECK_THREADS, thread_name_prefix="cluster_status_collector") as executor:
                for cluster in clusters:
                    executor.submit(update_cluster_status,
                                    cluster, mc_cluster_status)
        except:
            print(traceback.format_exc())

        end = int(time.time())

        elapsed_time = end - start
        print(f'elapsed time: {elapsed_time}')
        if elapsed_time < STATUS_CHECK_INTERVAL:
            time.sleep(STATUS_CHECK_INTERVAL - elapsed_time)


def update_cluster_status(cluster, mc_cluster_status):
    fvm_images = []
    for nos_package in cluster['fvm']['nos_packages']:
        fvm_images.append(nos_package['version'])

    cluster_ = cluster['cluster']
    name = cluster_['name']
    nodes = cluster['nodes']
    fvm = cluster['fvm']
    ops = Ops(cluster_, nodes, fvm)
    print(f'{name}: connected to fvm')
    success = ops.connect_to_fvm()
    if not success:
        d = {
            'success': False,
            'fvms': fvm['ips'],
            'name': cluster['name'],
            'uuid': cluster['uuid'],
            'timestamp': int(time.time())
        }

    else:
        ipmi_mac_status = ops.get_ipmi_mac_status()
        print(f'{name}: got ipmi mac status')
        ipmi_ip_status = ops.get_ipmi_ip_status()
        print(f'{name}: got ipmi ip status')
        host_ip_status = ops.get_host_ip_status()
        print(f'{name}: got host ip status')
        cvm_ip_status = ops.get_cvm_ip_status()
        print(f'{name}: got cvm ip status')
        prism_ip_status = ops.get_prism_ip_status()
        print(f'{name}: got prism ip status')
        prism_credential_status = ops.get_prism_credential_status()
        print(f'{name}: got prism credential status')

        d = {
            'success': True,
            'name': cluster['name'],
            'uuid': cluster['uuid'],
            'ipmi_mac_status': ipmi_mac_status,
            'ipmi_ip_status': ipmi_ip_status,
            'host_ip_status': host_ip_status,
            'cvm_ip_status': cvm_ip_status,
            'prism_ip_status': prism_ip_status,
            'prism_credential_status': prism_credential_status,
            'fvms': fvm['ips'],
            'fvm_images': fvm_images,
            'timestamp': int(time.time())
        }

    register_cluster_status(d, mc_cluster_status)


def register_cluster_status(cluster_status, mc_cluster_status):
    print(f'register cluster status: {cluster_status["name"]}')
    umongo.bulk_replace_upsert(mc_cluster_status, 'uuid', [cluster_status])


class Ops:

    def __init__(self, cluster, nodes, fvm):
        # cluster
        self.external_ip = cluster['external_ip']
        self.user = cluster['user']
        self.password = cluster['password']

        # nodes
        self.nodes = nodes

        # fvm
        self.fvm = fvm

    def connect_to_fvm(self):
        ips = self.fvm['ips']
        user = self.fvm['user']
        password = self.fvm['password']
        found = False
        for ip in ips:
            try:
                client = NutanixFoundationClient(ip, user, password)
                (success, result) = client.get_progress()
                if not success:
                    continue
                self.client = client
                found = True
                break
            except Exception as e:
                ...

        return found

    def get_ipmi_mac_status(self):
        mac_list = []
        for node in self.nodes:
            ipmi_mac = node['ipmi_mac']
            (success, result) = self.client.does_mac_exist(ipmi_mac, 'eth0')
            if not success:
                mac_list.append({'mac': ipmi_mac, 'exist': False})
            else:
                exist = result['exist']
                mac_list.append({'mac': ipmi_mac, 'exist': exist})
        return mac_list

    def get_ip_status(self, ip_list):
        new_ip_list = []
        for ip in ip_list:
            (success, result) = self.client.get_mac_from_ip(ip)
            if not success:
                new_ip_list.append({'ip': ip, 'exist': False})
            else:
                exist = result['exist']
                new_ip_list.append({'ip': ip, 'exist': exist})
        return new_ip_list

    def get_ipmi_ip_status(self):
        ip_list = []
        for node in self.nodes:
            ip_list.append(node['ipmi_ip'])
        return self.get_ip_status(ip_list)

    def get_host_ip_status(self):
        ip_list = []
        for node in self.nodes:
            ip_list.append(node['host_ip'])
        return self.get_ip_status(ip_list)

    def get_cvm_ip_status(self):
        ip_list = []
        for node in self.nodes:
            ip_list.append(node['cvm_ip'])
        return self.get_ip_status(ip_list)

    def get_prism_ip_status(self):
        (success, result) = self.client.get_mac_from_ip(self.external_ip)
        if not success:
            return False
        exist = result['exist']
        return exist

    def get_prism_credential_status(self):
        session = requests.Session()
        session.auth = (self.user, self.password)
        session.verify = False
        session.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})

        try:
            url = f'https://{self.external_ip}:9440/PrismGateway/services/rest/v1/cluster'
            resp = session.get(url, timeout=(5, 15))
            return resp.ok
        except:
            return False


if __name__ == '__main__':
    main()
