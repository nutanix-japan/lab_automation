class Networks:

  def __init__(self, *_):
    ...

  def get_network_names(self):
    error_dict = {}
    try:
      response_dict = self.get_v2('/networks/', error_dict)
      network_names = []
      for network in response_dict['entities']:
        network_names.append(network['name'])
      return (True, network_names)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def get_network_info(self, name):
    error_dict = {}
    try:
      response_dict = self.get_v2('/networks/', error_dict)
      network_info = {}
      for network in response_dict['entities']:
        if name != network['name']:
          continue
        network_info = {
          'name' : network['name'],
          'uuid' : network['uuid'],
          'vlan' : network['vlan_id'],
          'managed' : False
        }
        if 'network_address' in network['ip_config']:
          network_info['managed'] = True
          network_info['managed_address'] = network['ip_config']['network_address']
          network_info['managed_prefix'] = network['ip_config']['prefix_length']
          network_info['managed_gateway'] = network['ip_config']['default_gateway']
          network_info['managed_dhcp_address'] = network['ip_config']['dhcp_server_address']
          network_info['managed_dhcp_options'] = network['ip_config']['dhcp_options']
          pools = []
          for pool in network['ip_config']['pool']:
            words = pool['range'].split(' ')
            pools.append((words[0], words[1]))
          network_info['managed_pools'] = pools
        break
      if network_info == {}:
        raise IntendedException('Error. Unable to find network "{}"'.format(name))
      return (True, network_info)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def create_network(self, name, vlan):
    error_dict = {}
    try:
      body_dict = {
        'name' : name,
        'vlan_id' : str(vlan)
      }
      response_dict = self.post_v2('/networks/', body_dict, error_dict)
      return (True, response_dict['network_uuid'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def create_network_managed(self, name, vlan, network_address, prefix, gateway, pools, dns=''):
    error_dict = {}
    try:      
      body_dict = {
        'name' : name,
        'vlan_id' : str(vlan),
        'ip_config': {
          'dhcp_options': {
            'domain_name_servers': dns,
          },
          'network_address': network_address,
          'prefix_length': str(prefix),
          'default_gateway': gateway,
          "pool": []
        }
      }
      for pool in pools:
        entity = {'range' : '{} {}'.format(pool['from'], pool['to'])}
        body_dict['ip_config']['pool'].append(entity)

      response_dict = self.post_v2('/networks/', body_dict, error_dict)
      return (True, response_dict['network_uuid'])

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def is_network_used(self, name):
    error_dict = {}
    try:
      # Get uuid
      response_dict = self.get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # Check all VMs whether using this network or not.
      response_dict = self.get_v2('/vms/?include_vm_nic_config=true', error_dict)
      is_used = False
      for vm in response_dict['entities']:
        for nic in vm['vm_nics']:
          if network_uuid == nic['network_uuid']:
            is_used = True
            break
        if is_used:
          break
      return (True, is_used)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def delete_network(self, name):
    error_dict = {}
    try:
      # Get uuid
      response_dict = self.get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # Delete
      response_dict = self.delete_v2('/networks/{}'.format(network_uuid), error_dict)
      return (True, None)
      
    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def update_network():
    return (False, {'error':'Error. Not supported now.'})

