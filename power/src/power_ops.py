import time
import traceback
from client_power import NutanixPowerClient, NutanixClusterClient

class PowerOps:
  def __init__(self, cluster, nodes):
    self.ip =       cluster['external_ip']
    self.user =     cluster['user']
    self.password = cluster['password']
    self.nodes = nodes
    self.session = NutanixPowerClient()

  ###
  ## Check
  ###

  def is_all_host_down(self):
    all_down = True
    for node in self.nodes:
      ipmi_ip = node['ipmi_ip']
      ipmi_user = node['ipmi_user']
      ipmi_password = node['ipmi_password']
      (success, is_down) = self.session.is_host_down(ipmi_ip, ipmi_user, ipmi_password)
      if not success:
        raise Exception('error happens')
      print('host {} is down:{}'.format(node['host_ip'], is_down))
      if not is_down:
        all_down = False
    return all_down

  def is_all_host_up(self):
    all_up = True
    for node in self.nodes:
      ipmi_ip = node['ipmi_ip']
      ipmi_user = node['ipmi_user']
      ipmi_password = node['ipmi_password']
      (success, is_down) = self.session.is_host_down(ipmi_ip, ipmi_user, ipmi_password)
      if not success:
        raise Exception('error happens')
      print('host {} is down:{}'.format(node['host_ip'], is_down))
      if is_down:
        all_up = False
    return all_up

  def is_all_host_accessible(self):
    all_accessible = True
    for node in self.nodes:
      host_ip = node['host_ip']
      host_user = node['host_user']
      host_password = node['host_password']
      (_, accessible) = self.session.is_host_accessible(host_ip, host_user, host_password)
      print('host {} is accessible:{}'.format(host_ip, accessible))
      if not accessible:
        all_accessible = False
    return all_accessible

  def is_all_cvm_down(self):
    all_down = True
    for node in self.nodes:
      host_ip = node['host_ip']
      host_user = node['host_user']
      host_password = node['host_password']
      (success, is_down) = self.session.is_cvm_down(host_ip, host_user, host_password)
      if not success:
        raise Exception('error happens')
      print('cvm {} is down:{}'.format(node['cvm_ip'], is_down))
      if not is_down:
        all_down = False
    return all_down

  def is_all_cvm_up(self):
    all_up = True
    for node in self.nodes:
      host_ip = node['host_ip']
      host_user = node['host_user']
      host_password = node['host_password']
      (success, is_down) = self.session.is_cvm_down(host_ip, host_user, host_password)
      if not success:
        raise Exception('error happens')
      print('cvm {} is down:{}'.format(node['cvm_ip'], is_down))
      if is_down:
        all_up = False
        break
    return all_up

  def is_all_cvm_accessible(self):
    all_accessible = True
    for node in self.nodes:
      cvm_ip = node['cvm_ip']
      cvm_user = node['cvm_user']
      cvm_password = node['cvm_password']
      (_, accessible) = self.session.is_host_accessible(cvm_ip, cvm_user, cvm_password)
      print('cvm {} is accessible:{}'.format(cvm_ip, accessible))
      if not accessible:
        all_accessible = False
    return all_accessible

  def is_cluster_down(self):
    for node in self.nodes:
      ip = node['cvm_ip']
      user = node['cvm_user']
      password = node['cvm_password']
      (success, down) = self.session.is_cluster_down(ip, user, password)
      if not success:
        continue
      return down

    # failed to get cluster status from all cvms.
    # judge cluster is down 
    return True

  def is_cluster_up(self):
    return not self.is_cluster_down()


  ###
  ## UP
  ###

  def up_all_host(self):
    print('up_all_host()')
    for i in range(5):
      if self.is_all_host_up():
        return True
      for node in self.nodes:
        ipmi_ip = node['ipmi_ip']
        ipmi_user = node['ipmi_user']
        ipmi_password = node['ipmi_password']
        host_ip = node['host_ip']
        print('power on host {} through ipmi'.format(host_ip))
        (success, _) = self.session.up_host(ipmi_ip, ipmi_user, ipmi_password)
        if not success:
          print('failed to power on host: {}'.format(host_ip))
      time.sleep(20)
    print("Unable to power on hosts via IPMI.")
    return False

  def wait_till_all_host_becoming_accesible(self):
    print('wait_till_all_host_becoming_accesible()')
    for i in range(60):
      if self.is_all_host_accessible():
        return True
      print('waiting all host become accessible. {}/60'.format(i))
      time.sleep(5)
    print("Failed to see all CVMs are up")
    return False

  def wait_till_all_cvm_up(self):
    print('wait_till_all_cvm_up()')
    for i in range(12):
      try:
        if self.is_all_cvm_up():
          return True
      except:
        pass
      print('waiting all cvm up. {}/12'.format(i))
      time.sleep(5)
    print("Failed to see all CVMs are up")
    return False

  def wait_till_all_cvm_accessible(self):
    print('wait_till_all_cvm_accessible()')
    for i in range(24):
      try:
        if self.is_all_cvm_accessible():
          return True
      except:
        pass
      print('waiting all cvm become accessible. {}/24'.format(i))
      time.sleep(5)
    print("Failed to see all CVMs are up")
    return False

  def up_cluster(self):
    print('up_cluster()')
    node = self.nodes[0]
    ip = node['cvm_ip']
    user = node['cvm_user']
    password = node['cvm_password']

    for i in range(30):
      (success, is_down) = self.session.is_cluster_down(ip, user, password)
      if success:
        if not is_down:
          return True
        else:
          self.session.up_cluster(ip, user, password)
      time.sleep(10)
    print("failed to start cluster")
    return False

  ####
  ## Down Over Cluster
  ####

  def down_over_cluster(self):
    print('down_over_cluster()')
    tasks = [
        self.down_all_guestvms
    ]
    for task in tasks:
        task_name = task.__name__
        print(f'child task {task_name}')
        if not task():
            print(f'failed {task_name}')
            return False
    return True

  def down_all_guestvms(self):
    print('down_all_guestvms()')
    client = NutanixClusterClient(self.ip, self.user, self.password)
    for i in range(6):
      try:
        (_, vm_uuids) = client.get_poweredon_vms()
        if len(vm_uuids) == 0:
          return True
        else:
          print('power on vms: {}'.format(vm_uuids))
        for vm_uuid in vm_uuids:
          if i<5:
            client.shutdown_vm(vm_uuid)
          else:
            client.poweroff_vm(vm_uuid)
      except:
        print(traceback.format_exc())
      time.sleep(10)
    print('failed to off all vms')
    return False

  def down_cluster(self):
    print('down_cluster()')
    if self.is_cluster_down():
      return True

    for node in self.nodes:
      cvm_ip = self.nodes[0]['cvm_ip']
      cvm_user = self.nodes[0]['cvm_user']
      cvm_password = self.nodes[0]['cvm_password']
      (success, _) = self.session.down_cluster(cvm_ip, cvm_user, cvm_password)
      if success:
        break

    for i in range(12):
      if self.is_cluster_down():
        time.sleep(10)
        return True
      time.sleep(5)
    print('failed to stop cluster')
    return False

  def down_all_cvms(self):
    print('down_all_cvms()')
    for node in self.nodes:
      cvm_ip = node['cvm_ip']
      cvm_user = node['cvm_user']
      cvm_password = node['cvm_password']
      (success, _) = self.session.down_cvm(cvm_ip, cvm_user, cvm_password)
      print('cvm {} down request success:{}'.format(cvm_ip, success))

    for i in range(36):
      if self.is_all_cvm_down():
        return True
      print('waiting all cvms are down {}/36'.format(i))
      time.sleep(5)
    print('failed to down all cvms')
    return False

  def down_all_hosts(self):
    print('down_all_hosts()')
    for node in self.nodes:
      host_ip = node['host_ip']
      host_user = node['host_user']
      host_password = node['host_password']
      (success, _) = self.session.down_host(host_ip, host_user, host_password)
      print('host {} down request success:{}'.format(host_ip, success))

    for i in range(24):
      if self.is_all_host_down():
        return True
      print('waiting all hosts are down {}/24'.format(i))
      time.sleep(5)
    return self.down_all_hosts_force()

  def down_all_hosts_force(self):
    print('down_all_hosts_force()')
    for node in self.nodes:
      ipmi_ip = node['ipmi_ip']
      ipmi_user = node['ipmi_user']
      ipmi_password = node['ipmi_password']
      self.session.down_host_force(ipmi_ip, ipmi_user, ipmi_password)
    return True