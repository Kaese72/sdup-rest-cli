import argparse
import os
import requests
import json

from typing import Optional, Any, List, Dict

def optional_file_must_exist(file_name: Optional[str]) -> Optional[str]:
    if file_name is not None and not os.path.exists(file_name):
        raise ValueError(f"'{file_name}' does not exist")

    return file_name

class CLIConfig:
    def __init__(self, base_url: str, ca_cert: str, certauth_cert: Optional[str], certauth_key: Optional[str]):
        self.ca_cert = ca_cert
        self.certauth_cert = certauth_cert
        self.certauth_key = certauth_key
        self.base_url = base_url

    def get(self, path: str, parameters: Optional[List[str]] = None):
        return requests.get(f"{self.base_url}/{path}", cert=(self.certauth_cert, self.certauth_key), verify=self.ca_cert, params=parameters)


class SDUPRESTFilter:
    ATTR_KEY_INDEX = 0
    ATTR_VAL_INDEX = 1
    def __init__(self, operator: str, value: Any, key: str):
        self.operator = operator
        self.value = value
        self.key = key

    @classmethod
    def filter_from_string(cls, string):
        if len(filter_tuple := string.split("==", 1)) == 2:
            return cls(
                operator="eq",
                value=json.loads(filter_tuple[SDUPRESTFilter.ATTR_VAL_INDEX]),
                key=filter_tuple[SDUPRESTFilter.ATTR_KEY_INDEX]
            )

        else:
            raise ValueError(f"Non supported operator")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator,
            "value": self.value,
            "key": self.key,
        }


def devices(config: CLIConfig, filter: Optional[SDUPRESTFilter], device_id: Optional[str]):
    if device_id:
        resp = config.get(f"/devices/{device_id}")
        print(resp.text)

    else:
        resp = config.get("/devices", parameters=[("attributefilter", json.dumps([filter.to_dict()]))] if filter else [])
        print(resp.text)


PARSER = argparse.ArgumentParser("SDUP CLI tool")
PARSER.add_argument("--ca-cert", type=str, dest="ca_cert", default="/home/caller/Development/Private/huemie/huemie-ca/CA/rootCACert.pem")
PARSER.add_argument("--certauth-cert", type=optional_file_must_exist, dest="certauth_cert", default="/home/caller/Development/Private/huemie/huemie-ca/sdup-client/dev.sdup-client.crt")
PARSER.add_argument("--certauth-key", type=optional_file_must_exist, dest="certauth_key", default="/home/caller/Development/Private/huemie/huemie-ca/sdup-client/dev.sdup-client.key")
PARSER.add_argument("--base-url", type=str, dest="base_url", default="https://localhost:8082/rest/v0")

SUBPARSERS = PARSER.add_subparsers(dest="command", required=True)

DEVICES_COMMAND = "devices"
SUB_P_DEVICES = SUBPARSERS.add_parser(DEVICES_COMMAND)
SUB_P_DEVICES_XOR =  SUB_P_DEVICES.add_mutually_exclusive_group()
SUB_P_DEVICES_XOR.add_argument("--filter", type=SDUPRESTFilter.filter_from_string)
SUB_P_DEVICES_XOR.add_argument("--id", type=str)


ARGS = PARSER.parse_args()

CONFIG = CLIConfig(
    base_url=ARGS.base_url,
    ca_cert=ARGS.ca_cert,
    certauth_cert=ARGS.certauth_cert,
    certauth_key=ARGS.certauth_key
)

if ARGS.command == DEVICES_COMMAND:

    devices(CONFIG, ARGS.filter, ARGS.id)
