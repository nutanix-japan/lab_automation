from mod.base import Base
from mod.clusters import Clusters
from mod.hosts import Hosts
from mod.vms import Vms
import subprocess
import paramiko

class NutanixClusterClient(Base, Clusters, Hosts, Vms):
  def __init__(self, ip, username, password, timeout_connection=5, timeout_read=15):
    super().__init__(ip, username, password, timeout_connection, timeout_read)


class NutanixPowerClient:

  def __init__(self):
    pass

  ###
  ## Check
  ###

  def is_host_down(self, ipmi_ip, ipmi_user, ipmi_password):
    try:
      command = 'ipmitool -I lanplus -U {} -P {} -H {} power status'.format(ipmi_user, ipmi_password, ipmi_ip)
      res_bytes = subprocess.check_output(command.split())
      res_string = res_bytes.decode('utf-8').strip()
    except Exception as e:
      print(e)
      return (False, False)

    words = res_string.lower().split()
    if 'off' in words:
      return (True, True)
    if 'on' in words:
      return (True, False)
    return (False, False)
    
  def is_host_accessible(self, host_ip, host_user, host_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(host_ip, username=host_user, password=host_password, timeout=5.0)
      command = "date"
      stdin, stdout, stderr = client.exec_command(command)
      return (True, True)
    except Exception as e:
      print(e)
      return (True, False)

  def is_cvm_down(self, host_ip, host_user, host_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(host_ip, username=host_user, password=host_password, timeout=5.0)

      command = "bash -c 'virsh list | wc -l'"
      stdin, stdout, stderr = client.exec_command(command)
      buf = stdout.read().decode().strip()
      is_down = buf == '3'
      return (True, is_down)
    except Exception as e:
      print(e)
    return (False, False)

  def is_cluster_down(self, cvm_ip, cvm_user, cvm_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(cvm_ip, username=cvm_user, password=cvm_password, timeout=5)
      command = "/usr/local/nutanix/cluster/bin/cluster status | grep state"
      stdin, stdout, stderr = client.exec_command(command)
      buf = stdout.read().decode().strip()
      cluster_state = buf.split()
      is_stop = cluster_state[-1] == "stop"
      return (True, is_stop)
    except Exception as e:
      print(e)
    return (False, False)

  ###
  ## UP
  ###

  def up_host(self, ipmi_ip, ipmi_user, ipmi_password):
    try:
      command = 'ipmitool -I lanplus -U {} -P {} -H {} chassis power on'.format(ipmi_user, ipmi_password, ipmi_ip)
      res = subprocess.check_output(command.split()).decode('utf-8').strip()
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

  def up_cluster(self, cvm_ip, cvm_user, cvm_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(cvm_ip, username=cvm_user, password=cvm_password, timeout=3.0)
      command = '/usr/local/nutanix/cluster/bin/cluster start'
      stdin, stdout, stderr = client.exec_command(command)
      print(stdout.read().decode().strip())
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

  ###
  ## Down
  ###

  def down_cluster(self, cvm_ip, cvm_user, cvm_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(cvm_ip, username=cvm_user, password=cvm_password)
      command = "/home/nutanix/prism/cli/ncli cluster stop force=true"
      stdin, stdout, stderr = client.exec_command(command)
      stdin.close()
      stdout.close()
      stderr.close()
      client.close()
      print(stdout.read().decode().strip())
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

  def down_cvm(self, cvm_ip, cvm_user, cvm_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(cvm_ip, username=cvm_user, password=cvm_password)
      command = "sudo /usr/sbin/shutdown -P now"
      stdin, stdout, stderr = client.exec_command(command)
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

  def down_host(self, host_ip, host_user, host_password):
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(host_ip, username=host_user, password=host_password)
      command = "shutdown -h now"
      stdin, stdout, stderr = client.exec_command(command)
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

  def down_host_force(self, ipmi_ip, ipmi_user, ipmi_password):
    try:
      command = 'ipmitool -I lanplus -U {} -P {} -H {} chassis power off'.format(user, password, ip)
      res = subprocess.check_output(command.split()).decode('utf-8').strip()
      return (True, True)
    except Exception as e:
      print(e)
    return (False, False)

