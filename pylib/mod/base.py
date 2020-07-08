import requests
from requests.exceptions import RequestException

import json
import traceback
import logging
import datetime

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

class Base:
  def __init__(self, ip, username, password, timeout_connection=5, timeout_read=15):
    self.TIMEOUT = (timeout_connection, timeout_read)

    is_port_open = True
    import socket
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(timeout_connection) # seconds
      s.connect((ip, 9440))
      s.shutdown(2)
    except Exception as e:
      is_port_open = False
    if not is_port_open:
      raise Exception('unable to connect to "{}". please check ip and port.'.format(ip))

    # Make session
    session = requests.Session()
    session.ip = ip
    session.password = password
    session.auth = (username, password)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    self.session = session

    # Test session
    is_requests_ok = True
    url = 'https://{}:9440/PrismGateway/services/rest/v1/cluster'.format(ip)
    try:
      resp = session.get(url, timeout=self.TIMEOUT)
    except:
      is_requests_ok = False
    if not is_requests_ok:
      raise Exception('server port is open. but unexpected error happens')
    if not resp.ok:
      raise Exception('server port is open. but unable to get cluster info. please check your credential')

  def handle_error(self, error, error_dict):
    error_dict['error'] = str(error)
    if not isinstance(error, IntendedException):
      error_dict['stacktrace'] = traceback.format_exc()

  def get_v08(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    attempts = 0
    while attempts < 3:
      try:
        response = self.session.get('https://{}:9440/api/nutanix/v0.8{}'.format(self.session.ip, url), timeout=self.TIMEOUT)
        break
      except RequestException as e:
        attempts += 1

    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def post_v08(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.post('https://{}:9440/api/nutanix/v0.8{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def put_v08(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.put('https://{}:9440/api/nutanix/v0.8{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def delete_v08(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.delete('https://{}:9440/api/nutanix/v0.8{}'.format(self.session.ip, url),
     timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    try:
      return response.json()
    except:
      return {}

  def get_v1(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.get('https://{}:9440/api/nutanix/v1{}'.format(self.session.ip, url), 
      timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def post_v1(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.post('https://{}:9440/api/nutanix/v1{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def put_v1(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.put('https://{}:9440/api/nutanix/v1{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def delete_v1(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.delete('https://{}:9440/api/nutanix/v1{}'.format(self.session.ip, url), 
      timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    try:
      return response.json()
    except:
      return {}

  def get_v2(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.get('https://{}:9440/api/nutanix/v2.0{}'.format(self.session.ip, url),
     timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def post_v2(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.post('https://{}:9440/api/nutanix/v2.0{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def put_v2(self, url, body_dict, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.put('https://{}:9440/api/nutanix/v2.0{}'.format(self.session.ip, url), 
      data=json.dumps(body_dict, indent=2), timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    return response.json()

  def delete_v2(self, url, error_dict):
    if not url.startswith('/'): url = '/' + url
    response = self.session.delete('https://{}:9440/api/nutanix/v2.0{}'.format(self.session.ip, url),
     timeout=self.TIMEOUT)
    if not response.ok:
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
    try:
      return response.json()
    except:
      return {}

class IntendedException(Exception):
  pass