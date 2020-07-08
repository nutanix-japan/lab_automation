class Application:

  def __init__(self, *_):
    ...

  def change_autologout_minute(self, user_timeout, system_timeout):
    error_dict = {}
    try:
      user_timeout = user_timeout * 60 * 1000
      system_timeout = system_timeout * 60 * 1000

      # user_data
      body_dict = {
        "type":"UI_CONFIG",
        "key":"autoLogoutTime",
        "username":"admin",
        "value":user_timeout
      }
      response_dict = self.put_v1('/application/user_data', body_dict, error_dict)

      body_dict = {
        "type":"ui_config",
        "key":"autoLogoutGlobal",
        "value":system_timeout
      }
      response_dict = self.put_v1('/application/system_data', body_dict, error_dict)

      body_dict = {
        "type":"ui_config",
        "key":"autoLogoutOverride",
        "value":0
      }
      response_dict = self.put_v1('/application/system_data', body_dict, error_dict)
      return (True, {})

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)