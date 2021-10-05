from generator_scripts.format import bcolors, NetworkConfiguration
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
import os
import json
import base64
def generate_wallets(_network_config: NetworkConfiguration,
                                _orgs,
                                _domain):
    """
    This function will generate a wallet for VS Code import.
    :param _network_config: The Network Configuration structure, containing ports and stuff
    :param _orgs: the number of organizations to configure
    """
    cwd = os.getcwd()
    nodes = list()

    print(bcolors.WARNING + "[*] Creating Wallets")
    # Orderer Wallet
    print(bcolors.WARNING + "   [*] Create Orderer ID")
    orderer_id = {
        "mspId": "OrdererMSP",
        "type": "X.509",
        "version": 1
    }
    orderer_creds = {}
    with open(f"crypto-config/ordererOrganizations/{_domain}/users/Admin@{_domain}/msp/keystore/priv_sk",
              "rb") as f:
        privkey = f.read().decode("utf-8")
        orderer_creds.update({"privateKey": privkey})

    with open(f"crypto-config/ordererOrganizations/{_domain}/users/Admin@{_domain}/msp/signcerts/Admin@{_domain}-cert.pem",
              "rb") as f:
        cert = f.read().decode("utf-8")
        orderer_creds.update({"certificate": cert})

    orderer_id.update({"credentials": orderer_creds})

    with open("wallet/ordererAdmin.id", "w+") as f:
        f.write(json.dumps(orderer_id))


    print(bcolors.OKGREEN + "   [+] Create Orderer ID Complete")
    for org in range(_orgs):
        print(bcolors.WARNING + f"   [*] Create Org{org+1}MSP ID")
        org_id = {
            "mspId": f"Org{org+1}MSP",
            "type": "X.509",
            "version": 1
        }
        org_creds = {}
        with open(f"crypto-config/peerOrganizations/org{org+1}.{_domain}/users/Admin@org{org+1}.{_domain}/msp/keystore/priv_sk",
                  "rb") as f:
            privkey = f.read().decode("utf-8")
            org_creds.update({"privateKey": privkey})

        with open(
                f"crypto-config/peerOrganizations/org{org+1}.{_domain}/users/Admin@org{org+1}.{_domain}/msp/signcerts/Admin@org{org+1}.{_domain}-cert.pem",
                "rb") as f:
            cert = f.read().decode("utf-8")
            org_creds.update({"certificate": cert})

        org_id.update({"credentials": org_creds})

        with open(f"wallet/org{org+1}Admin.id", "w+") as f:
            f.write(json.dumps(org_id))
        print(bcolors.OKGREEN + f"   [+] Org{org + 1}MSP ID Complete")
    print(bcolors.OKGREEN + "[+] Wallet Created")
