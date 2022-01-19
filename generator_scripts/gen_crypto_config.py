from generator_scripts.format import bcolors, Orga, tr
import ruamel.yaml


def generate_crypto_config(_orgs=2,
                           _peers=2,
                           _orderers=3,
                           _domain="dredev.de",
                           _channels=1):
    """
    This function will generate the crypto-config.yaml file in the current directory
    :param _orgs: Number of Organizations to configure crypto material for
    :param _peers: Number of Peers per Organization
    :param _orderers: Number of Orderers
    :param _domain: Domain Name of the network
    :param _channels: Number of channels that will be created (default 1)
    """
    new_yaml = ruamel.yaml.YAML()
    peer_list = []
    specs_list = []
    for i in range(_orderers):
        specs_list.append({"Hostname": "orderer{}".format(i + 1)})
    # This step is important, since the connection to the peer might not be established exclusively within the docker
    # env where the domain name is present. So, the Certificate need to include the external, local address of the host
    specs_list.append({"SANS": ["localhost", "127.0.0.1"]})
    for org in range(_orgs):
        print(bcolors.WARNING + "       [*] Generating Crypto Material for Org{}".format(org))
        peer_list.append({
            "Name": "Org{}".format(org + 1),
            "Domain": "org{}.{}".format(org + 1, _domain),
            "EnableNodeOUs": True,
            "Template": {"Count": _peers, "SANS": ["localhost", "127.0.0.1"]},
            "Users": {"Count": 1},  # Only one user per Org
        })
        print(bcolors.OKGREEN + "       [+] Generating Crypto Material for Org{} COMPLETE".format(org))
    print(bcolors.OKBLUE + "   [*] Generating Final Object")
    final_dict = {
        "OrdererOrgs": [
            {
                "Name": "Orderer",
                "Domain": _domain,
                "EnableNodeOUs": True,
                "Specs": specs_list
            }
        ],
        "PeerOrgs": peer_list
    }
    print(bcolors.OKBLUE + "   [*] Generating Final Object COMPLETE")
    f = open("crypto-config.yaml", "w")
    new_yaml.dump(final_dict, f)
    f.close()
    print(bcolors.HEADER + "========================================")
    print(">>> crypto-config.yaml has been dumped!")
    print("========================================")

