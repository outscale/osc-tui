import json

from osc_sdk_python import Gateway

if __name__ == '__main__':
    gw = Gateway(**{'profile': 'fne'})
    def decorator(func):

        def wrapped( *args, **kwargs):
            print("TEST")
            return func(*args, **kwargs)

        return wrapped
    for method_name in dir(gw):
        if not method_name.startswith("__"):
            attr = getattr(gw, method_name)
            if(callable(attr)):
                wrapped = decorator(attr)
                setattr(gw, method_name, wrapped)
    # for vm in gw.ReadVms()['Vms']:
     #   print(json.dumps(vm["SecurityGroups"]))
    vms = ((gw.ReadVms()['Vms']))
    VMs = dict()
    for vm in vms:
        VMs.update({vm['VmId']: vm})
    # print(json.dumps(VMs))
    #print  (VMs)
    # print(json.dumps(gw.ReadSecurityGroups()))

    #print("\nyour volumes:")
    # for volume in gw.ReadVolumes()["Volumes"]:
        # print(volume["VolumeId"])
    #ssgw1 = Gateway()
    #print(gw1.ReadSecurityGroups(  Filters = {    "SecurityGroupIds": [      "sg-c387f0b7"    ]})['SecurityGroups'][0]['InboundRules'])
    #imgs = gw.ReadImages()["Images"]
    # for img in imgs:
    #    account = img["AccountAlias"] if "AccountAlias" in img else "Unknow User"
    #    img_str = "creator: " + account + " id: " + img["ImageId"] + " name: " + img["ImageName"]
    #    print(img_str)
    # print(json.dumps(gw.ReadSecurityGroups(
    #            Filters={"SecurityGroupIds": ['sg-c387f0b7']}
    #        )["SecurityGroups"][0]["InboundRules"]))
    print(
        json.dumps(
            gw.CreateKeypair(
                KeypairName='test1234'),
            sort_keys=True,
            indent=4))
    print(json.dumps(gw.ReadKeypairs(), sort_keys=True, indent=4))

    from requests import get
