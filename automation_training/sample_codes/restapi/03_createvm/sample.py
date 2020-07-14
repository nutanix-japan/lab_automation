import requests, json, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IP = '10.149.161.41'
USER = 'admin'
PASSWORD = 'Devops4Eva!'
VM_NAME = 'myvm'
VM_CPU = 1
VM_MEMORY_MB = 1024

def get_body(name, cpu, memory_mb):
    d = {
        "name":name,
        "memory_mb":memory_mb,
        "num_vcpus":1,
        "description":"",
        "num_cores_per_vcpu":cpu,
        "timezone":"UTC",
        "boot":{
            "uefi_boot":False,
            "boot_device_order":[
                "CDROM",
                "DISK",
                "NIC"
            ]
        },
        "vm_disks":[
            {
                "is_cdrom":True,
                "is_empty":True,
                "disk_address":{
                    "device_bus":"ide",
                    "device_index":0
                }
            }
        ],
        "hypervisor_type":"ACROPOLIS",
        "vm_features":{
            "AGENT_VM":False
        }
    }
    return json.dumps(d)


session = requests.Session()
session.auth = (USER, PASSWORD)
session.verify = False                              
session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

url = f'https://{IP}:9440/PrismGateway/services/rest/v2.0/vms?include_vm_disk_config=true&include_vm_nic_config=true'
body = get_body(VM_NAME, VM_CPU, VM_MEMORY_MB)
response = session.post(url, data=body)

if response.ok:
    j = response.json()
    print(json.dumps(j, indent=2))
else:
    print('error happens')
    print(f'sutatus code : {response.status_code}')
    print(response.text)