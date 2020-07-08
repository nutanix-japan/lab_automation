class Alerts:

  def __init__(self, *args, **kwargs):
    ...

  def enable_default_nutanix_email(self, enable=True):
    error_dict = {}
    try:
      body_dict = {
        "enableDefaultNutanixEmail":enable
      }
      response_dict = self.put_v1('/alerts/configuration', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def disable_default_nutanix_email(self):
    error_dict = {}
    try:
      body_dict = {
        "enableDefaultNutanixEmail":False
      }
      response_dict = self.put_v1('/alerts/configuration', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)