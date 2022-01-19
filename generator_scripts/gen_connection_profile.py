from generator_scripts.format import bcolors, NetworkConfiguration
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
import os
import string

def generate_connection_profile(_network_config: NetworkConfiguration,
                                _peers,
                                _orgs,
                                _orderers,
                                _domain,
                                _url,
                                _channels):
    """
    This function will generate a connection_profile.yaml file for the current network within the current workdir.
    :param _network_config: The Network Configuration structure, containing ports and stuff
    :param _peers: the number of peers to configure
    :param _orgs: the number of organizations to configure
    :param _orderers: the number of orderers to configure
    :param _domain: the domain of the channel
    """
    cwd = os.getcwd()
    new_yaml = ruamel.yaml.YAML()
    orderer_list = [f"orderer{i+1}.{_domain}" for i in range(_orderers)]
    print(bcolors.WARNING + "[*] Creating Connection Profile")
    peer_list = {}
    print(bcolors.WARNING + "   [*] Create Peer List")
    for peer in range(_peers):
        for org in range(_orgs):
            peer_list.update({f"peer{peer}.org{org+1}.{_domain}": {
                "endorsingPeer": True,
                "chaincodeQuery": True,
                "ledgerQuery": True,
                "eventSource": True,
            }})
    print(bcolors.OKGREEN + "   [+] Peer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Client List")

    client = {
        "organization": "Org1",
        "connection": {
            "options": {
                "grpc.keepalive_time_ms": 120000
            },
            "timeout":{
                "peer": {
                    "endorser": ruamel.yaml.scalarstring.SingleQuotedScalarString('300')
                },
                "orderer": ruamel.yaml.scalarstring.SingleQuotedScalarString('300')
            }
        }
    }
    print(bcolors.OKGREEN + "   [+] Client List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Channel List")
    
    channels = {}
    for i in range(_channels):
        channels.update({
        f"channel{string.ascii_lowercase[i]}": {
            "orderers": orderer_list,
            "peers": peer_list
        },
    })

    print(bcolors.OKGREEN + "   [+] Channel List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Organization List")
    organiz = {}
    for org in range(_orgs):
        peers_ls = [f"peer{i}.org{org+1}.{_domain}" for i in range(_peers)]
        organiz.update({f"Org{org+1}": {
            "mspid": f"Org{org+1}MSP",
            "peers": peers_ls,
            "certificateAuthorities": [
                f"ca.org{org+1}.{_domain}"
            ]
        }})
    print(bcolors.OKGREEN + "   [+] Organization List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Orderer List")

    ordes = {}
    i = 0
    for orderer in orderer_list:
        ordes.update({
            orderer: {
                "url": f"grpcs://{_url}:{_network_config.orderer_defport+1000*i}",
                "tlsCACerts": {
                    "path": cwd + f"/crypto-config/ordererOrganizations/{_domain}/tlsca/tlsca.{_domain}-cert.pem"
                },
                "grpcOptions": {
                    "ssl-target-name-override": orderer
                }
            }
        })
        i += 1
    print(bcolors.OKGREEN + "   [+] Orderer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Detail Peer List")

    peer_ls = {}
    host_peers = []
    for peer in range(_peers):
        for org in range(_orgs):
            host_peers.append(f"peer{peer}.org{org+1}.{_domain}")
            peer_ls.update({f"peer{peer}.org{org+1}.{_domain}": {
                "url": f"grpcs://{_url}:{_network_config.peer_defport + 1000 * ((_peers * org) + peer)}",
                "tlsCACerts": {
                    "path": cwd + f"/crypto-config/peerOrganizations/org{org+1}.{_domain}/tlsca/tlsca.org{org+1}.{_domain}-cert.pem"
                },
                "grpcOptions": {
                    "ssl-target-name-override": f"peer{peer}.org{org+1}.{_domain}",
                    "request-timeout": 120001
                }
            }})
    print(bcolors.OKGREEN + "   [+] Detail Peer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Detail CA List")

    ca_ls = {}
    i = 0
    for org in range(_orgs):
        host_peers.append("ca.org{}.{}".format(org+1, _domain))
        ca_ls.update({
            "ca.org{}.{}".format(org+1, _domain): {
                "url": f"https://{_url}:{_network_config.ca_defport+1000*i}",
                "httpOptions": {
                    "verify": False,
                },
                "registrar": [
                    {
                        "enrollId": "admin",
                        "enrollSecret": "adminpw"
                    }
                ],
                "caName": f"ca.org{org+1}.{_domain}"
            }
        })
        i += 1
    print(bcolors.OKGREEN + "   [+] Detail CA List COMPLETE")
    print(bcolors.OKBLUE + "======= Generating final Structure =======")

    final = {

        "name": DoubleQuotedScalarString(f"{_peers}-peer.{_orgs}-org.{_orderers}-orderers.{_domain}"),
        "x-type": DoubleQuotedScalarString("hlfv2"),
        "description": DoubleQuotedScalarString("Connection profile"),
        "version": DoubleQuotedScalarString("1.0"),
        "client": client,
        "channels": channels,
        "organizations": organiz,
        "orderers": ordes,
        "peers": peer_ls,
        "certificateAuthorities": ca_ls
    }
    print(bcolors.OKBLUE + "======= Final Structure COMPLETE =======")

    f = open("connection_profile.yaml", "w")
    f.write("# Please add the following lines to your DNS resolver like /etc/hosts\n")
    for peer in host_peers:
        f.write("# 127.0.0.1 " + peer + "\n")
    for orderer in orderer_list:
        f.write("# 127.0.0.1 " + orderer + "\n")
    new_yaml.dump(final, f)
    f.close()
    print(bcolors.OKGREEN + "[+] Connection Profile Created")
