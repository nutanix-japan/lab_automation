import paramiko
IP = '10.149.161.41'
USERNAME = 'nutanix'
PASSWORD = 'nutanix/4u'

def exec_command(ip, user, password, command):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=password, timeout=3.0)
    (stdin, stdout, stderr) = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

print(exec_command(IP, USERNAME, PASSWORD, 'source /etc/profile; ncli --json=true cluster get-domain-fault-tolerance-status type=node'))
