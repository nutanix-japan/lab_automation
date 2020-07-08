class Files:

  def __init__(self, *_):
    ...

  def get_fsvms(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/vfilers', error_dict)
      fsvm_list = []
      for entity in response_dict['entities']:
        for nvms in entity['nvms']:
          fsvm_list.append(nvms['name'])
      return (True, fsvm_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)