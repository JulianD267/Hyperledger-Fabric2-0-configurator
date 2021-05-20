from generator_scripts.format import bcolors, Orga, tr, NetworkConfiguration
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString


def generate_configtx(_network_config: NetworkConfiguration,
                      _orgs=2,
                      _orderers=3,
                      _kafka_brokers=3,
                      _consortium="WebConsortium",
                      _domain="dredev.de",
                      _blocksize=10,
                      _timeout=1):
    """
    This Function will generate a configtx.yaml file in the current working dir.
    :param _network_config: Configuration Structure for Network affairs like ports or dns names
    :param _orgs: Number of Organizations to configure (default 2)
    :param _orderers: Number of Orderers to configure (default 3)
    :param _kafka_brokers: (Optional) if Kafka = true, Number of Kafka Nodes to configure (default 3)
    :param _consortium: Generic Consortium name (default "WebConsortium")
    :param _domain: Domain name of the network (default "dredev.de")
    :param _blocksize: Configurable amount of transactions per block
    :param _timeout: Block Timeout, influencing block generation
    """

    yaml_new = ruamel.yaml.YAML()

    orgs = [Orga(org="", domain="ordererOrganizations", orgmsp="OrdererMSP", ap=False)]  # Default one orderer!
    # Create Orga Objects to have an object orriented approach. Otherwise this would be too tedious to maintain
    for i in range(_orgs):
        orgs.append(
            Orga(org=f"org{i + 1}.", domain="peerOrganizations", orgmsp=f"Org{i + 1}MSP", ap=True))

    orga_list = []

    # Configure the Access Policies
    for org in orgs:
        print(bcolors.WARNING + f"       [*] Configuring Org {org.org_msp}")
        org_policies = {
            "Readers": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString(f"OR('{org.org_msp}.member')")
            },
            "Writers": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString(f"OR('{org.org_msp}.member')")
            },
            "Admins": {
                "Type": 'Signature',
                "Rule": DoubleQuotedScalarString(f"OR('{org.org_msp}.admin')")
            },
            "Endorsement": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString(f"OR('{org.org_msp}.member')")
            }

        }
        orderer_org = {
            "Name": f"{org.org_msp}",
            "ID": f"{org.org_msp}",
            "MSPDir": f"crypto-config/{org.domain}/{org.org}{_domain}/msp",
            "Policies": org_policies
        }
        if org.anchor_peer:
            orderer_org.update({"AnchorPeers": [
                {
                    "Host": f"peer0.{org.org}{_domain}",
                    "Port": 7051
                }
            ]})

        orga_list.append(orderer_org)
        print(bcolors.OKGREEN + f"       [+] Configuring for Org {org.org_msp} COMPLETE")
    print(bcolors.WARNING + "       [*] Configuring Capabilities")
    channel_capabilities = {"V2_0": True}
    orderer_capabilities = {"V2_0": True}
    app_capabilities = {"V2_0": True}

    capabilities = {
        "Channel": channel_capabilities,
        "Orderer": orderer_capabilities,
        "Application": app_capabilities
    }
    print(bcolors.OKGREEN + "       [+] Configuring Capabilities COMPLETE")

    print(bcolors.WARNING + "       [*] Configuring App Permissions")
    application = {
        "ACLs": {
            "_lifecycle/CheckCommitReadiness": "/Channel/Application/Writers",

            # ACL policy for _lifecycle's "CommitChaincodeDefinition" function
            "_lifecycle/CommitChaincodeDefinition": "/Channel/Application/Writers",

            # ACL policy for _lifecycle's "QueryChaincodeDefinition" function
            "_lifecycle/QueryChaincodeDefinition": "/Channel/Application/Readers",

            # ACL policy for _lifecycle's "QueryChaincodeDefinitions" function
            "_lifecycle/QueryChaincodeDefinitions": "/Channel/Application/Readers",

            # ---Lifecycle System Chaincode (lscc) function to policy mapping for access control---#
            # ACL policy for lscc's "getid" function
            "lscc/ChaincodeExists": "/Channel/Application/Readers",

            # ACL policy for lscc's "getdepspec" function
            "lscc/GetDeploymentSpec": "/Channel/Application/Readers",

            # ACL policy for lscc's "getccdata" function
            "lscc/GetChaincodeData": "/Channel/Application/Readers",

            # ACL Policy for lscc's "getchaincodes" function
            "lscc/GetInstantiatedChaincodes": "/Channel/Application/Readers",

            # ---Query System Chaincode (qscc) function to policy mapping for access control---#

            # ACL policy for qscc's "GetChainInfo" function
            "qscc/GetChainInfo": "/Channel/Application/Readers",

            # ACL policy for qscc's "GetBlockByNumber" function
            "qscc/GetBlockByNumber": "/Channel/Application/Readers",

            # ACL policy for qscc's  "GetBlockByHash" function
            "qscc/GetBlockByHash": "/Channel/Application/Readers",

            # ACL policy for qscc's "GetTransactionByID" function
            "qscc/GetTransactionByID": "/Channel/Application/Readers",

            # ACL policy for qscc's "GetBlockByTxID" function
            "qscc/GetBlockByTxID": "/Channel/Application/Readers",

            # ---Configuration System Chaincode (cscc) function to policy mapping for access control---#

            # ACL policy for cscc's "GetConfigBlock" function
            "cscc/GetConfigBlock": "/Channel/Application/Readers",

            # ACL policy for cscc's "GetConfigTree" function
            "cscc/GetConfigTree": "/Channel/Application/Readers",

            # ACL policy for cscc's "SimulateConfigTreeUpdate" function
            "cscc/SimulateConfigTreeUpdate": "/Channel/Application/Readers",

            # ---Miscellanesous peer function to policy mapping for access control---#

            # ACL policy for invoking chaincodes on peer
            "peer/Propose": "/Channel/Application/Writers",

            # ACL policy for chaincode to chaincode invocation
            "peer/ChaincodeToChaincode": "/Channel/Application/Readers",

            # ---Events resource to policy mapping for access control###---#

            # ACL policy for sending block events
            "event/Block": "/Channel/Application/Readers",

            # ACL policy for sending filtered block events
            "event/FilteredBlock": "/Channel/Application/Readers",
        },
        "Organizations": None,
        "Policies": {
            "LifecycleEndorsement": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("MAJORITY Endorsement"),
            },
            "Endorsement": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Endorsement"),
            },
            "Readers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Readers")
            },
            "Writers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Writers")
            },
            "Admins": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("MAJORITY Admins")
            }
        },
        "Capabilities": {
            "<<": app_capabilities
        }
    }
    print(bcolors.OKGREEN + "       [+] Configuring App Permissions COMPLETE")
    orderer_addresses = []
    orderer_addresses_with_port = []
    kafka_list = []
    for i in range(_orderers):
        orderer_addresses.append(f"orderer{i + 1}.{_domain}")
        orderer_addresses_with_port.append(f"orderer{i + 1}.{_domain}:7050")

    for i in range(_kafka_brokers):
        kafka_list.append(f"kafka{i}:9092")

    print(bcolors.WARNING + "       [*] Generating Orderer Config")

    orderer = {
        "Addresses": orderer_addresses_with_port,
        # Batch Timeout: The amount of time to wait before creating a batch.
        "BatchTimeout": f"{_timeout}s",
        "BatchSize": {
            "MaxMessageCount": _blocksize,
            "AbsoluteMaxBytes": "10 MB",
            "PreferredMaxBytes": "2 MB",
        },
        "MaxChannels": 0,

        "Organizations": None,
        "Policies": {
            "Readers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Readers")
            },
            "Writers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Writers")
            },
            "Admins": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("MAJORITY Admins")
            },
            "BlockValidation": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Writers")
            }

        },
        "Capabilities": {
            "<<": orderer_capabilities
        }
    }
    if _network_config.ordering_service is "kafka":
        # Use Kafka Ordering
        orderer.update({"OrdererType": "kafka"})
        orderer.update({"Kafka": {
            "Brokers": kafka_list
        }})
    else:
        # Use Raft Ordering
        orderer.update({"OrdererType": "etcdraft"})
        raft_config = {
            "Consenters": [{
                "Host": addr,
                "Port": _network_config.orderer_defport,
                "ClientTLSCert": f"crypto-config/ordererOrganizations/{_domain}/orderers/{addr}/tls/server.crt",
                "ServerTLSCert": f"crypto-config/ordererOrganizations/{_domain}/orderers/{addr}/tls/server.crt"
            } for addr in orderer_addresses]
        }
        orderer.update({"EtcdRaft": raft_config})

    print(bcolors.OKGREEN + "       [+] Generating Orderer Config COMPLETE")
    print(bcolors.WARNING + "       [*] Generating Channel Config")
    channel = {
        "Policies": {
            "Readers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Readers"),
            },
            "Writers": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("ANY Writers"),
            },
            "Admins": {
                "Type": "ImplicitMeta",
                "Rule": DoubleQuotedScalarString("MAJORITY Admins")
            }
        },
        "Capabilities": {
            "<<": channel_capabilities,
        }
    }
    print(bcolors.OKGREEN + "       [*] Generating Channel Config COMPLETE")

    ord_list = []
    for i in range(_orderers):
        ord_list.append(f"orderer{i + 1}.{_domain}:7050")

    print(bcolors.WARNING + "       [*] Generating Profiles")
    orderer_p = {"<<": orderer,
                 "Addresses": ord_list,
                 "Organizations": [orga_list[0]],
                 "Capabilities": {
                     "<<": orderer_capabilities,
                 }
                 }
    if _network_config.ordering_service is "kafka":
        orderer_p.update({"OrdererType": "kafka"})
    else:
        orderer_p.update({"OrdererType": "etcdraft"})
        orderer_p.update({"EtcdRaft": raft_config})

    profiles = {
        "OrdererDefault": {
            "<<": channel,
            "Capabilities": {
                "<<": channel_capabilities
            },
            "Orderer": orderer_p,
            "Consortiums": {
                _consortium: {
                    "Organizations":
                        orga_list[1:]
                }
            }

        },
        "MainChannel": {
            "<<": channel,
            "Consortium": _consortium,
            "Application": {
                "<<": application,
                "Organizations": orga_list[1:]
            },
            "Capabilities": {
                "<<": app_capabilities
            }

        }
    }
    print(bcolors.OKGREEN + "       [+] Generating Profiles COMPLETE")
    print(bcolors.OKBLUE + "    [*] Generating Final Object")
    final = {
        "Organizations": orga_list,
        "Capabilities": capabilities,
        "Application": application,
        "Orderer": orderer,
        "Channel": channel,
        "Profiles": profiles
    }
    print(bcolors.OKBLUE + "    [+] Generating Final Object COMPLETE")

    f = open("configtx.yaml", "w")
    yaml_new.dump(final, f, transform=tr)

    print(bcolors.HEADER + "========================================")
    print(">>> configtx.yaml has been dumped!")
    print("========================================")
