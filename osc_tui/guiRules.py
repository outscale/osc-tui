
import json
import os
from pathlib import Path

home = str(Path.home())
PATH = home + '/.osc/osc-tui-rules.json'

RULES=None

def objectify():
    ret = None
    if os.path.isfile(PATH):
        ret = {}
        with open(PATH) as configFile :
            j = json.loads(configFile.read())
            for rule_name in j:
                rule=j[rule_name]
                if "mode" not in rule:
                    print('"mode" is a requirre argument of costum rule',
                          file=sys.stderr)
                if rule["mode"] not in ret:
                    ret[rule["mode"]] = {}
                ret[rule["mode"]][rule_name] = {
                    "ports": rule["ports"],
                    "protocols": rule["protocols"]
                }
                if "ips" in rule:
                    ret[rule["mode"]][rule_name]["ips"] = rule["ips"]
    return ret

def parse():
    global RULES
    RULES=objectify()
