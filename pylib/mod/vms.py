class Vms:

  def __init__(self, *_):
    ...

  def get_vm_names(self):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/', error_dict)
      vm_names = []
      for vm in response_dict['entities']:
        vm_names.append(vm['name'])
      return (True, vm_names)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_info(self, name):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/?include_vm_disk_config=true&include_vm_nic_config=true', error_dict)
      vm_info = {}
      for vm in response_dict['entities']:
        if vm['name'] != name:
          continue
        vm_info = {
          'name' : vm['name'],
          'uuid' : vm['uuid'],
          'memory_mb' : vm['memory_mb'],
          'num_vcpus' : vm['num_vcpus'],
          'num_cores' : vm['num_cores_per_vcpu'],
          'power_state' : vm['power_state'],
          'timezone' : vm['timezone'],
          'is_agent' : vm['vm_features'].get('AGENT_VM', False)
        }

        disks = []
        for disk in vm['vm_disk_info']:
          disk_info = {
            'bus' : disk['disk_address']['device_bus'],
            'label' : disk['disk_address']['disk_label'],
            'is_cdrom' : disk['is_cdrom'],
            'is_flashmode' : disk['flash_mode_enabled'],
            'is_empty' : disk['is_empty'],
            'vmdisk_uuid' : disk['disk_address'].get('vmdisk_uuid', ''),
            'container_uuid' : disk.get('storage_container_uuid', ''),
            'size' : disk.get('size', 0)
          }
          disks.append(disk_info)
        vm_info['disks'] = disks

        nics = []
        for nic in vm['vm_nics']:
          nic_info = {
            'mac_address' : nic['mac_address'],
            'network_uuid' : nic['network_uuid'],
            'is_connected' : nic['is_connected']
          }
        vm_info['nics'] = nics
        break
      if vm_info == {}:
        raise IntendedException('Error. Unable to find vm "{}"'.format(name))
      return (True, vm_info)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def clone_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def create_vm_new(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def create_vm_from_image(self, name, memory_mb, num_vcpus, num_cores, image_name, network_name, ip_address=''):
    error_dict = {}
    try:
      # image uuid
      response_dict = self.get_v2('/images/', error_dict)
      vmdisk_uuid = ''
      vmdisk_size = 0
      for image in response_dict['entities']:
        if image['name'] == image_name:
          vmdisk_uuid = image['vm_disk_id']
          vmdisk_size = image['vm_disk_size']
          break
      if vmdisk_uuid == '':
        raise IntendedException('Error. Unable to find image "{}"'.format(image_name))

      # network uuid
      response_dict = self.get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == network_name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # create vm with image_uuid and network_uuid
      body_dict = {
        "name": name,
        "memory_mb": memory_mb,
        "num_vcpus": num_vcpus,
        "description": "",
        "num_cores_per_vcpu": num_cores,
        "vm_disks": [
          {
            "is_cdrom": True,
            "is_empty": True,
            "disk_address": {
              "device_bus": "ide"
            }
          },
          {
            "is_cdrom": False,
            "disk_address": {
              "device_bus": "scsi"
            },
            "vm_disk_clone": {
              "disk_address": {
                "vmdisk_uuid": vmdisk_uuid
              },
              "minimum_size": vmdisk_size
            }
          }
        ],
        "vm_nics": [
          {
            "network_uuid": network_uuid,
            "requested_ip_address": ip_address
          }
        ],
        "affinity": None,
        "vm_features": {
          "AGENT_VM": False
        }
      }
      if ip_address == '':
        del body_dict['vm_nics'][0]['requested_ip_address']
      response_dict = self.post_v2('/vms/', body_dict, error_dict)
      return (True, response_dict['task_uuid'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def update_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def delete_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def get_poweredon_vms(self):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/', error_dict)
      uuids = []
      for vm in response_dict['entities']:
        state = vm['power_state'].lower()
        if state == 'on':
          uuids.append(vm['uuid'])
      return (True, uuids)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def poweron_vm(self, uuid):
    error_dict = {}
    try:
      d = {"transition":"on"}
      response_dict = self.post_v2('/vms/{}/set_power_state'.format(uuid), d, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def poweroff_vm(self, uuid):
    error_dict = {}
    try:
      d = {"transition":"off"}
      response_dict = self.post_v2('/vms/{}/set_power_state'.format(uuid), d, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def shutdown_vm(self, uuid):
    error_dict = {}
    try:
      d = {"transition":"acpi_shutdown"}
      response_dict = self.post_v2('/vms/{}/set_power_state'.format(uuid), d, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def snapshot_vm(self, vm_name, snapshot_name):
    return (False, {'error':'Error. Not supported now.'})

  def get_vm_disks(self, vm_name):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/?include_vm_disk_config=true', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        vdisks = []
        for vdisk in vm['vm_disk_info']:
          if vdisk['is_cdrom']:
            continue
          vdisks.append(vdisk['disk_address']['disk_label'])
        return (True, vdisks)
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def get_poweredon_vms(self):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/?include_vm_nic_config=true', error_dict)
      vm_list = []
      for entity in response_dict['entities']:
        if(entity.get('power_state') == 'on'):
          vm_list.append(entity.get('name'))
      return (True, vm_list)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_powerstate(self, vm_name):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        return (True, vm['power_state'])
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_ip(self, vm_name):
    error_dict = {}
    try:
      response_dict = self.get_v2('/vms/?include_vm_nic_config=true', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        if len(vm['vm_nics']) == 0:
          continue
        try:
          return (True, vm['vm_nics'][0]['ip_address'])
        except:
          pass
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)