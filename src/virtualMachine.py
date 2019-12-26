class VirtualMachine:
    def __init__(self, vm_dict):
        self.status = vm_dict["State"]
        self.name = "(nil)"
        if len(vm_dict["Tags"]) > 0:
            self.name = vm_dict["Tags"][0]["Value"]
        self.id = vm_dict["VmId"]
        self.type = vm_dict["VmType"]
        self.priv_ip = vm_dict["PrivateIp"] if "PrivateIp" in vm_dict else None
        self.ext_ip = vm_dict["PublicIp"] if "PublicIp" in vm_dict else None
        self.key_pair = vm_dict["KeypairName"] if "KeypairName" in vm_dict else None
        self.az = vm_dict["Placement"]["SubregionName"]
        self.security_group = (
            vm_dict["SecurityGroups"] if "SecurityGroups" in vm_dict else None
        )

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
        s = ""
        self.summarise()
        for att in self.summary:
            s += str(att) + " "
        return s


def summary_titles():
    return "Status Name ID Type Keypair IP(Public) IP(Private) AZ".split()
