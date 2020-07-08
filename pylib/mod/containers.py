class Containers:

  def __init__(self, *_):
    ...

  def get_container_names(self):
    error_dict = {}
    try:
      response_dict = self.get_v1('/containers/', error_dict)
      container_names = []
      for cont in response_dict['entities']:
        container_names.append(cont['name'])
      return (True, container_names)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def get_container_info(self, name):
    error_dict = {}
    try:
      response_dict = self.get_v1('/containers/', error_dict)
      container_info = {}
      for cont in response_dict['entities']:
        if cont['name'] != name:
          continue
        container_info = {
          'uuid':cont['containerUuid'],
          'id':cont['id'],
          'storagepool_uuid':cont['storagePoolUuid'],
          'usage':cont['usageStats']['storage.usage_bytes']
        }
        break  
      if len(container_info) == 0:
        raise IntendedException('Error. Unable to find container "{}"'.format(name))
      return (True, container_info)
      
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def create_container(self, container_name, storagepool_name=''):
    error_dict = {}
    try:
      # Get storage pool uuid.
      response_dict = self.get_v1('/storage_pools/', error_dict)
      storagepool_dict = {}
      for storagepool in response_dict['entities']:
        storagepool_dict[storagepool['name']] = storagepool['storagePoolUuid']
      storagepool_uuid = ''
      if storagepool_name == '':
        if len(storagepool_dict) != 1:
          raise IntendedException('Error. Needs to provide storagepool name if having 2+ pools.')
        storagepool_uuid = storagepool_dict.popitem()[1]
      else:
        if storagepool_name not in storagepool_dict:
          raise IntendedException('Error. Storagepool name "{}" doesn\'t exist.'.format(storagepool_name))
        storagepool_uuid = storagepool_dict[storagepool_name]

      # Create container
      body_dict = {
        "id": None,
        "name": container_name,
        "storagePoolId": storagepool_uuid,
        "totalExplicitReservedCapacity": 0,
        "advertisedCapacity": None,
        "compressionEnabled": True,
        "compressionDelayInSecs": 0,
        "fingerPrintOnWrite": "OFF",
        "onDiskDedup": "OFF"
      }
      response_dict = self.post_v1('/containers/', body_dict, error_dict)
      return (True, response_dict['value'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def update_container(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def delete_container(self, name):
    error_dict = {}
    try:
      # Get uuid from name
      response_dict = self.get_v1('/containers/', error_dict)
      container_uuid = ''
      for cont in response_dict['entities']:
        if cont['name'] == name:
          container_uuid = cont['containerUuid']
          break
      if container_uuid == '':
        raise IntendedException('Error. Unable to find container "{}"'.format(name))

      # Delete
      response_dict = self.delete_v1('/containers/{}'.format(container_uuid), error_dict)
      return (True, response_dict['value'])
      
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

