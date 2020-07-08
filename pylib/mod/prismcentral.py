class PrismCentral:

  def __init__(self, *_):
    ...

  def get_pc_vms(self):
    error_dict = {}
    try:
      response_list = self.get_v1('/multicluster/cluster_external_state', error_dict)
      pc_ip_list = []
      for response in response_list:
        pc_ip_list.append(response.get('clusterDetails').get('ipAddresses')[0])

      pc_name_list = []
      response_dict = self.get_v2('/vms/?include_vm_nic_config=true', error_dict)
      for entity in response_dict['entities']:
        if len(entity.get('vm_nics')) > 0:
          try:
            vm_ip = entity.get('vm_nics')[0].get('ip_address')
            if vm_ip in pc_ip_list:
              pc_name_list.append(entity.get('name'))
          except:
            pass
      return (True, pc_name_list)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)

  def make_pc(self, version, container, ip, network, subnetmask, gateway):
    pass
    '''
    Request URL: https://10.149.161.41:9440/api/nutanix/v3/prism_central
    Request Method: POST

    Payload
    {
       "resources":{
          "version":"5.10.3",
          "should_auto_register":false,
          "pc_vm_list":[
             {
                "vm_name":"PrismCentral",
                "container_uuid":"0fc0176b-7eac-4fb0-a27d-9069bc3cf371",
                "num_sockets":4,
                "data_disk_size_bytes":536870912000,
                "memory_size_bytes":17179869184,
                "dns_server_ip_list":[
                   "8.8.8.8"
                ],
                "nic_list":[
                   {
                      "ip_list":[
                         "10.149.161.42"
                      ],
                      "network_configuration":{
                         "network_uuid":"a134b6d8-6e4d-4dea-9aa3-c6d225ffdb3b",
                         "subnet_mask":"255.255.252.0",
                         "default_gateway":"10.149.160.1"
                      }
                   }
                ]
             }
          ]
       }
    }
    '''

  def register_pc(self):
    pass
    '''
    https://10.149.161.41:9440/PrismGateway/services/rest/v1/multicluster/add_to_multicluster
    Request Method: POST
    Status Code: 200 OK

    {
       "ipAddresses":[
          "10.149.161.42"
       ],
       "username":"admin",
       "password":"Nutanix/4u!"
    }
    '''
