from osc_sdk_python import Gateway
import json
if __name__ == '__main__':
    gw = Gateway()

    #for vm in gw.ReadVms():
    #print(json.dumps(gw.ReadVms()['Vms'][0]["SecurityGroups"]))
    vms = ((gw.ReadVms()['Vms']))
    VMs = dict()
    for vm in vms:
        VMs.update({vm['VmId'] : vm})
    #print  (VMs)
    #print(json.dumps(gw.ReadSecurityGroups()))

    #print("\nyour volumes:")
    #for volume in gw.ReadVolumes()["Volumes"]:
        #print(volume["VolumeId"])
    #print(gw.ReadSecurityGroups(  Filters = {    "SecurityGroupIds": [      "sg-ceb6c7a7"    ]})['SecurityGroups'][0]['InboundRules'])
    from requests import get

    ip = get('https://api.ipify.org').text
    print(gw.CreateSecurityGroupRule(FromPortRange = 22,
        IpProtocol= 'tcp',
        IpRange= ip + '/32',
        ToPortRange= 22,
        SecurityGroupId= 'sg-4bac10fa',
        Flow= 'Inbound',
        #'SecurityGroupAccountIdToLink' :
        ))
    print(gw.DeleteSecurityGroupRule(FromPortRange = 22,
        IpProtocol= 'tcp',
        IpRange= ip + '/32',
        ToPortRange= 22,
        SecurityGroupId= 'sg-4bac10fa',
        Flow= 'Inbound',
        #'SecurityGroupAccountIdToLink' :
        ))
