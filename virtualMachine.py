class VirtualMachine():
    def __init__(self, vm_dict):
        self.status = vm_dict['State']
        self.name = vm_dict['Tags'][0]['Value']
        self.id = vm_dict['VmId']
        self.type = vm_dict['VmType']
        self.ext_ip = 'None'
        self.priv_ip = vm_dict['PrivateIp']
        if self.status != 'stopped':
            self.ext_ip = vm_dict['PublicIp']
        self.key_pair = vm_dict['KeypairName']
        self.az = vm_dict['Placement']['SubregionName']

    def summarise(self):
        self.summary = list()
        self.summary.append(self.status)
        self.summary.append(self.name)
        self.summary.append(self.id)
        self.summary.append(self.type)
        self.summary.append(self.key_pair)
        self.summary.append(self.ext_ip)
        self.summary.append(self.priv_ip)
        self.summary.append(self.az)
        return self.summary

    def __str__(self):
        s = ''
        self.summarise()
        for att in self.summary:
            s += str(att) + ' '
        return s


def summary_titles():
    return 'Status Name ID Type Keypair IP(Public) IP(Private) AZ'.split()
