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
    print(gw.ReadSecurityGroups(  Filters = {
    "SecurityGroupIds": [
      "sg-ceb6c7a7"
    ]})['SecurityGroups'][0]['InboundRules'])