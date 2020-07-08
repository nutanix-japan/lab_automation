class Users:

  def __init__(self, *_):
    ...

  def change_password(self, old_password, new_password):
    error_dict = {}
    try:
      body_dict = {
        "oldPassword":old_password,
        "newPassword":new_password
      }
      response_dict = self.put_v1('/users/change_password', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def change_language(self, user, language):
    error_dict = {}
    try:
      if language not in ['en-US', 'ja-JP', 'zh-CN']:
        raise Exception('Error: language must be one of them "en-US", "ja-JP", "zh-CN"')
      
      body_dict = {
        "username":user,
        "locale":language,
      }
      response_dict = self.put_v1('/users/{}/profile'.format(user), body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

