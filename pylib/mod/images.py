class Images:

  def __init__(self, *_):
    ...

  def get_image_names(self):
    error_dict = {}
    try:
      response_dict = self.get_v08('/images/', error_dict)
      image_names = []
      for image in response_dict['entities']:
        image_names.append(image['name'])
      return (True, image_names)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def upload_image(self, file_url, target_container, image_name):
    error_dict = {}
    try:
      # Get container UUID
      response_dict = self.get_v1('/containers/', error_dict)
      target_container_uuid = ''
      for cont in response_dict['entities']:
        if cont['name'] == target_container:
          target_container_uuid = cont['containerUuid']
          break
      if target_container_uuid == '':
        raise IntendedException('Unable to find container "{}"'.format(target_container))

      # Upload
      is_iso = file_url.lower().endswith('.iso')
      image_type = 'ISO_IMAGE' if is_iso else 'DISK_IMAGE'
      body_dict = {
        "name": image_name,
        "annotation": "",
        "imageType": image_type,
        "imageImportSpec": {
          "containerUuid": target_container_uuid,
          "url": file_url,
        }
      }
      response_dict = self.post_v08('/images/', body_dict, error_dict)
      return (True, response_dict['taskUuid'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def create_image_from_vm_vdisk(self, vm_name, vm_disk, target_container, image_name):
    error_dict = {}
    try:
      # Get vdisk_uuid and source_container_uuid
      response_dict = self.get_v2('/vms/?include_vm_disk_config=true', error_dict)
      vdisk_uuid = ''
      source_container_uuid = ''
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        for vdisk in vm['vm_disk_info']:
          if vdisk['disk_address']['disk_label'] != vm_disk:
            continue
          vdisk_uuid = vdisk['disk_address']['vmdisk_uuid']
          source_container_uuid = vdisk['storage_container_uuid']
          break
        break
      if vdisk_uuid == '':
        raise Exception('Error: Unable to find VM "{}" which has vDisk "{}"'.format(vm_name, vm_disk))

      # Get souce_container_name and target_container_uuid
      response_dict = self.get_v1('/containers/', error_dict)
      source_container_name = ''
      target_container_uuid = ''
      for cont in response_dict['entities']:
        if cont['containerUuid'] == source_container_uuid:
          source_container_name = cont['name']
        if cont['name'] == target_container:
          target_container_uuid = cont['containerUuid']
      if source_container_name == '':
        raise IntendedException('Error: Unable to find source container name from uuid="{}".'.format(source_container_uuid))
      if target_container_uuid == '':
        raise IntendedException('Error: Unable to find container "{}"'.format(target_container))

      # Upload image from VM vDisk
      nfs_url = 'nfs://127.0.0.1/{}/.acropolis/vmdisk/{}'.format(source_container_name, vdisk_uuid)
      body_dict = {
        "name": image_name,
        "annotation": "",
        "imageType": 'DISK_IMAGE',
        "imageImportSpec": {
          "containerUuid": target_container_uuid,
          "url": nfs_url,
        }
      }
      response_dict = self.post_v08('/images/', body_dict, error_dict)
      return (True, response_dict['taskUuid'])
      
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def delete_image(self, name):
    error_dict = {}
    try:
      # Get image UUID
      response_dict = self.get_v08('/images/', error_dict)
      image_uuid = ''
      for image in response_dict['entities']:
        if image['name'] == name:
          image_uuid = image['uuid']
          break
      if image_uuid == '':
        raise IntendedException('Error: Unable to find image "{}"'.format(name))

      # Delete
      response_dict = self.delete_v08('/images/{}'.format(image_uuid), error_dict)
      return (True, response_dict['taskUuid'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

