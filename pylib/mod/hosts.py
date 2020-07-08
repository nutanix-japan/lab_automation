class Hosts:

  def __init__(self, *_):
    ...

  def get_node_ips(self):
    error_dict = {}
    try:
      response_dict = self.get_v2('/hosts', error_dict)
      node_ips = []
      for host in response_dict['entities']:
        d = {
          'host_ip': host['hypervisor_address'],
          'cvm_ip': host['controller_vm_backplane_ip'],
          'ipmi_ip': host['ipmi_address']
        }
        node_ips.append(d)
      return (True, d)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)