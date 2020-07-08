'''
Python lib for Nutanix Foundation VM.
 - Rest API
 - Paramiko

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

import datetime
import json
import logging
import paramiko
import requests
from requests.exceptions import RequestException
import traceback
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


###
# Foundation Client
###

class NutanixFoundationClient:

    def __init__(self, ip, username, password, timeout_connection=5, timeout_read=3600):
        TIMEOUT = (timeout_connection, timeout_read)

        # Test IP and Port reachability
        is_port_open = True
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout_connection)  # seconds
            s.connect((ip, 8000))
            s.shutdown(2)
        except:
            is_port_open = False
        if not is_port_open:
            raise Exception(
                'Unable to connect Nutanix Cluster "{}". Please check ip and port.'.format(ip))

        # Make session
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        session.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})
        response = session.get(
            'http://{}:8000/foundation/version'.format(ip), timeout=TIMEOUT)
        if not response.ok:
            raise Exception(
                'Able to connect, but unable to login. Please check credential.')

        session.ip = ip
        session.username = username
        session.password = password
        session.TIMEOUT = TIMEOUT
        self.session = session

    def reset_state(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/reset_state', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def abort_session(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/abort_session', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def get_version(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/version', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def does_mac_exist(self, mac_address, nic):
        error_dict = {}
        try:
            words = mac_address.split(':')
            # add 0 on each octets if it is missed
            for i in range(len(words)):
                if len(words[i]) == 0:
                    words[i] = '0' + words[i]
            # reverse 7th bit on first octet
            w0 = bin(int(words[0], 16))[2:]
            w0 = '0' * (8-len(w0)) + w0
            if w0[6] == '0':
                w0 = w0[:6] + '1' + w0[7]
            else:
                w0 = w0[:6] + '0' + w0[7]
            words[0] = hex(int(w0, 2))[2:]
            # make ipv6 link local address
            linklocal_address = 'fe80::{}{}:{}ff:fe{}:{}{}'.format(*words)

            # make paramiko session
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.session.ip, username=self.session.username,
                           password=self.session.password)

            # try ping and checking mac address existance
            command = 'ping6 -I {} {} -c 3'.format(nic, linklocal_address)
            stdin, stdout, stderr = client.exec_command(command)
            exist = False
            for line in stdout:
                if 'packets transmitted' in line:
                    if not '0 received' in line:
                        exist = True
            stdout.close()
            stdin.close()
            stderr.close()
            client.close()
            return (True, {'exist': exist})

        except Exception as exception:
            if client:
                client.close()
            handle_error(exception, error_dict)
            return (False, error_dict)

    def get_mac_from_ip(self, ip_address):
        error_dict = {}
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.session.ip, username=self.session.username,
                           password=self.session.password)
            command = 'ping {} -c 2'.format(ip_address)
            stdin, stdout, stderr = client.exec_command(command)
            exist = False
            for line in stdout:
                if 'packets transmitted' in line:
                    if not '0 received' in line:
                        exist = True
                    break
            if not exist:
                stdout.close()
                stdin.close()
                stderr.close()
                client.close()
                return (True, {'exist': False, 'mac': ''})

            stdin, stdout, stderr = client.exec_command('/sbin/arp')
            mac = ''
            for line in stdout:
                line = line.lower()
                if ip_address in line:
                    words = line.split()
                    mac = words[2]

            stdout.close()
            stdin.close()
            stderr.close()
            client.close()
            exist = mac != ''
            return (True, {'exist': exist, 'mac': mac})

        except Exception as exception:
            print(traceback.format_exc())
            handle_error(exception, error_dict)
            return (False, error_dict)

    def get_nos_packages(self):
        error_dict = {}
        try:
            response_dict = get(
                self.session, '/enumerate_nos_packages', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def get_nics(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/list_nics', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def choose_primary_nic(self, nic):
        error_dict = {}
        try:
            body_dict = {
                "primary_nic": nic
            }
            response_dict = post(
                self.session, '/primary_nic', body_dict, error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def discover_nodes(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/discover_nodes')
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def get_progress(self):
        error_dict = {}
        try:
            response_dict = get(self.session, '/progress', error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def ipmi_config(self,
                    netmask, gateway,  # page1
                    nodeinfo_list,    # page2
                    cluster_name, external_ip, name_server, ntp_server,  # page3
                    nos_package  # page4
                    ):
        error_dict = {}
        try:
            body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
                                           cluster_name, external_ip, name_server, ntp_server, nos_package)
            response_dict = post(
                self.session, '/ipmi_config', body_dict, error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def pre_check(self,
                  netmask, gateway,  # page1
                  nodeinfo_list,    # page2
                  cluster_name, external_ip, name_server, ntp_server,  # page3
                  nos_package  # page4
                  ):
        error_dict = {}
        try:
            body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
                                           cluster_name, external_ip, name_server, ntp_server, nos_package)
            response_dict = post(
                self.session, '/pre_check', body_dict, error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def image_nodes(self,
                    netmask, gateway,  # page1
                    nodeinfo_list,    # page2
                    cluster_name, external_ip, name_server, ntp_server,  # page3
                    nos_package  # page4
                    ):
        error_dict = {}
        try:
            body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
                                           cluster_name, external_ip, name_server, ntp_server, nos_package)
            response_dict = post(
                self.session, '/image_nodes', body_dict, error_dict)
            return (True, response_dict)
        except Exception as exception:
            handle_error(exception, error_dict)
            return (False, error_dict)

    def _get_jsonbody(self,
                      netmask, gateway,  # page1
                      nodeinfo_list,    # page2
                      cluster_name, external_ip, name_server, ntp_server,  # page3
                      nos_package  # page4
                      ):
        body_dict = {
            "ui_skip_network_setup": True,
            "cvm_gateway": gateway,
            "ui_nic": "eth0",
            "blocks": [
                {
                    "ui_test_name": "Manual-1",
                    "block_id": None,
                    "ui_block_id": "",
                    "nodes": []
                }
            ],
            "ui_is_installing_secondary_hypervisor": False,
            "hypervisor_netmask": netmask,
            "bond_lacp_rate": None,
            "ipmi_netmask": netmask,
            "ui_is_installing_cvm": True,
            "hyperv_sku": None,
            "ui_have_vlan": False,
            "bond_mode": "",
            "cvm_netmask": netmask,
            "nos_package": nos_package,
            "hypervisor_gateway": gateway,
            "hypervisor_iso": {
                "kvm": {
                    "checksum": None,
                    "filename": "AHV bundled with AOS (version 4.6+)"
                }
            },
            "ipmi_gateway": gateway,
            "clusters": [
                {
                    "cluster_external_ip": external_ip,
                    "cluster_init_successful": None,
                    "redundancy_factor": 2,
                    "cluster_name": cluster_name,
                    "cvm_ntp_servers": ntp_server,
                    "cluster_members": [],
                    "timezone": "Asia/Tokyo",
                    "cvm_dns_servers": name_server,
                    "cluster_init_now": True
                }
            ],
            "hypervisor": "kvm",
            "ui_is_installing_hypervisor": True
        }

        for (ipmi_mac, ipmi_ip, host_ip, cvm_ip, host_name, position) in nodeinfo_list:
            # add cluster member
            cluster_members = body_dict['clusters'][0]['cluster_members']
            cluster_members.append(cvm_ip)
            # add node
            node_info = {
                "ipv6_address": None,
                "is_bare_metal": True,
                "image_successful": None,
                "image_now": True,
                "ipv6_interface": None,
                "nos_version": "99.0",
                "ipmi_ip": ipmi_ip,
                "hardware_attributes_override": {},
                "node_position": position.upper(),
                "is_selected": True,
                "hypervisor_hostname": host_name,
                "cvm_gb_ram": 32,
                "compute_only": False,
                "ipmi_password": "ADMIN",
                "ipmi_configure_now": True,
                "hypervisor_ip": host_ip,
                "ipmi_user": "ADMIN",
                "ipmi_mac": ipmi_mac,
                "hypervisor": "kvm",
                "cvm_ip": cvm_ip
            }
            nodes = body_dict['blocks'][0]['nodes']
            nodes.append(node_info)
        return body_dict


########
# Utility
########

class IntendedException(Exception):
    pass


def get(session, url, error_dict):
    if not url.startswith('/'):
        url = '/' + url
    response = session.get('http://{}:8000/foundation{}'.format(session.ip, url),
                           timeout=session.TIMEOUT)

    if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException(
            'Receive unexpected response code "{}".'.format(response.status_code))
    try:
        return response.json()
    except:
        return {'text': response.text}


def post(session, url, body_dict, error_dict):
    if not url.startswith('/'):
        url = '/' + url
    response = session.post('http://{}:8000/foundation{}'.format(session.ip, url),
                            data=json.dumps(body_dict, indent=2), timeout=session.TIMEOUT)
    if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException(
            'Receive unexpected response code "{}".'.format(response.status_code))
    try:
        return response.json()
    except:
        return {'text': response.text}


def handle_error(error, error_dict):
    error_dict['error'] = str(error)
    if not isinstance(error, IntendedException):
        error_dict['stacktrace'] = traceback.format_exc()
