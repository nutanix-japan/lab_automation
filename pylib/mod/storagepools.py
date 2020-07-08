class StoragePools:

  def __init__(self, *_):
    ...

  def get_storagepool_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/storage_pools/', error_dict)
      storagepools = []
      for storagepool in response_dict['entities']:
        storagepools.append(storagepool['name'])
      return (True, storagepools)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)