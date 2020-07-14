import paramiko
IP = '10.149.161.41'
USERNAME = 'nutanix'
PASSWORD = 'nutanix/4u'

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(IP, username=USERNAME, password=PASSWORD, timeout=3.0)
(stdin, stdout, stderr) = client.exec_command('uname -a')
output = stdout.read().decode()
print(output)
client.close()
