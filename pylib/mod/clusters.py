class Clusters:

  def __init__(self, *_):
    ...

  def add_fs_whitelist(self, network, subnetmask):
    error_dict = {}
    try:
      body_dict = ['{}/{}'.format(network, subnetmask)]
      response_dict = self._post_v1('/cluster/nfs_whitelist/add_list', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)
      
  def get_cluster_info(self):
    error_dict = {}
    try:
      response_dict = self.get_v1('/cluster/', error_dict)
      return_dict = {
        # Basic
        'uuid' : response_dict['uuid'],
        'name' : response_dict['name'],
        'timezone' : response_dict['timezone'],
        'is_lts' : response_dict['isLTS'],
        'version' : response_dict['version'],
        'version_ncc' : response_dict['nccVersion'],

        # RF
        'current_redundancy_factor' : response_dict['clusterRedundancyState']['currentRedundancyFactor'],
        'desired_redundancy_factor' : response_dict['clusterRedundancyState']['desiredRedundancyFactor'],

        # Network
        'ip_external' : response_dict['clusterExternalIPAddress'],
        'ip_iscsi' : response_dict['clusterExternalDataServicesIPAddress'],
        'network_external' : response_dict['externalSubnet'],
        'network_internal' : response_dict['internalSubnet'],
        'nfs_whitelists' : response_dict['globalNfsWhiteList'],

        # Node and Block
        'num_nodes' : response_dict['numNodes'],
        'block_serials' : response_dict['blockSerials'],
        'num_blocks' : len(response_dict['blockSerials']),

        # Servers
        'name_servers' : response_dict['nameServers'],
        'ntp_servers' : response_dict['ntpServers'],
        'smtp_server' : '' if response_dict['smtpServer'] is None else response_dict['smtpServer'],

        # Storage
        'storage_type' : response_dict['storageType'],
      }

      hypervisors = response_dict['hypervisorTypes']
      if len(hypervisors) == 1:
        return_dict['hypervisor'] = hypervisors[0]
        if return_dict['hypervisor'] == 'kKvm':
          return_dict['hypervisor'] = 'AHV'
      else:
        # needs update here
        return_dict['hypervisor'] = 'unknown'

      return (True, return_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def get_cluster_name(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['name'])
    return (success, dict)

  def change_cluster_name(self):
    return {'error':'Error: Not supported now'}

  def get_hypervisor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['hypervisor'])
    return (success, dict)

  def get_version(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['version'])
    return (success, dict)

  def get_name_servers(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['name_servers'])
    return (success, dict)

  def get_ntp_servers(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['ntp_servers'])
    return (success, dict)

  def get_block_serials(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['block_serials'])
    return (success, dict)

  def get_num_nodes(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['num_nodes'])
    return (success, dict)

  def get_desired_redundancy_factor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['desired_redundancy_factor'])
    return (success, dict)

  def get_current_redundancy_factor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['current_redundancy_factor'])
    return (success, dict)