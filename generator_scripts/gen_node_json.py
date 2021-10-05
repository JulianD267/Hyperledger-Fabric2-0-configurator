from generator_scripts.format import bcolors, NetworkConfiguration
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
import os
import json
import base64
def generate_node_json(_network_config: NetworkConfiguration,
                                _peers,
                                _orgs,
                                _orderers,
                                _domain,
                                _url):
    """
    This function will generate a nodes.json file in the Nodes directory containing the necessary format for the VS Code
    extension.
    :param _network_config: The Network Configuration structure, containing ports and stuff
    :param _peers: the number of peers to configure
    :param _orgs: the number of organizations to configure
    :param _orderers: the number of orderers to configure
    :param _domain: the domain of the channel
    :param _url the physical network URL of the nodes
    """
    cwd = os.getcwd()
    nodes = list()

    print(bcolors.WARNING + "[*] Creating Nodes")
    print(bcolors.WARNING + "   [*] Create Peer Nodes")

    for org in range(_orgs):
        my_pem = ""
        with open(f"crypto-config/peerOrganizations/org{org+1}.{_domain}/msp/tlscacerts/tlsca.org{org+1}.{_domain}-cert.pem", "rb") as f:
            my_pem = base64.b64encode(f.read()).decode("utf-8")
        for peer in range(_peers):
            my_peer = {
                "name": f"peer{peer}.org{org+1}.{_domain}",
                "api_url": f"grpcs://{_url}:{_network_config.peer_defport + 1000 * ((_peers * org) + peer)}",
                "type": "fabric-peer",
                "msp_id": f"Org{org+1}MSP",
                "pem": my_pem,
                "wallet": "wallet",
                "identity": f"org{org+1}Admin"
            }
            nodes.append(my_peer)

    print(bcolors.OKGREEN + "   [+] Peer Nodes COMPLETE")
    print(bcolors.WARNING + "   [*] Create CA Nodes")
    for org in range(_orgs):
        my_ca = {
            "name": f"ca.org{org+1}.{_domain}",
            "api_url": f"http://{_url}:{_network_config.ca_defport + org * 1000}",
            "type": "fabric-ca",
            "ca_name": f"ca.org{org+1}.{_domain}",
            "enroll_id": "admin",
            "enroll_secret": "adminpw",
            "wallet": "wallet",
            "identity": f"org{org+1}Admin"
         }
        nodes.append(my_ca)
    print(bcolors.OKGREEN + "   [+] CA Nodes COMPLETE")
    print(bcolors.WARNING + "   [*] Create Orderer Nodes")

    with open(f"crypto-config/ordererOrganizations/{_domain}/msp/tlscacerts/tlsca.{_domain}-cert.pem",
              "rb") as f:
        my_pem = base64.b64encode(f.read()).decode("utf-8")
    for orderer in range(_orderers):
        my_ord = {
            "name": f"orderer{orderer+1}.{_domain}",
            "api_url": f"grpc://{_url}:{_network_config.orderer_defport + orderer * 1000}",
            "type": "fabric-orderer",
            "msp_id": "OrdererMSP",
            "pem": my_pem,
            "wallet": "wallet",
            "identity": "adminOrderer",
            "cluster": "ordererCluster"
        }
        nodes.append(my_ord)
    print(bcolors.OKGREEN + "   [+] Orderer Nodes COMPLETE")
    print(bcolors.OKBLUE + "======= Final Structure COMPLETE =======")
    if not os.path.exists("Nodes"):
        os.makedirs("nodes")
    with open("nodes/nodes.json", "w") as f:
        f.write(json.dumps(nodes))

    print(bcolors.OKGREEN + "[+] Nodes Created")
