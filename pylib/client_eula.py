import json
import requests
from mod.base import Base
from mod.alerts import Alerts
from mod.users import Users

class NutanixEulaClient(Base, Alerts, Users):

  def __init__(self, ip, username, password, timeout_connection=5, timeout_read=15):
    super().__init__(ip, username, password, timeout_connection, timeout_read)


  @staticmethod
  def change_default_system_password(ip, user, old_password, new_password):
    # Make session without auth
    session = requests.Session()
    session.auth = (user, old_password)
    session.verify = False                 
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    body_dict = {
      "oldPassword":old_password,
      "newPassword":new_password
    }
    response = session.post('https://{}:9440/api/nutanix/v1/utils/change_default_system_password'.format(ip), 
      data=json.dumps(body_dict, indent=2))

    # https://10.149.161.41:9440/PrismGateway/services/rest/v1/utils/change_default_system_password

    if response.ok:
      return (True, response.json())
    else:
      error_dict = {}
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      error_dict['error'] = response.text
      return (False, error_dict)


  def set_eula(self, user_name, company_name, job_title):
    error_dict = {}
    try:
      body_dict = {
        "username":user_name,
        "companyName":company_name,
        "jobTitle":job_title
      }
      response_dict = self.post_v1('/eulas/accept', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def set_initial_pulse_enable(self, enable=True):
    error_dict = {}
    try:
      body_dict = {
        "emailContactList":None,
        "enable":enable,
        "verbosityType":None,
        "enableDefaultNutanixEmail":False,
        "defaultNutanixEmail":None,
        "nosVersion":None,
        "isPulsePromptNeeded":False,
        "remindLater":None
      }
      response_dict = self.put_v1('/pulse', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)
