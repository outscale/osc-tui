from osc_sdk_python import Gateway
import json
if __name__ == '__main__':
    gw = Gateway()

    print("your virtual machines:")
    #for vm in gw.ReadVms():
    print(json.dumps(gw.ReadVms()))

    #print("\nyour volumes:")
    #for volume in gw.ReadVolumes()["Volumes"]:
        #print(volume["VolumeId"])
