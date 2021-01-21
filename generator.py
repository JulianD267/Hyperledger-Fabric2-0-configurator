import yaml
import argparse
import os
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

ca_defport = 7054
orderer_defport = 7050
peer_defport = 7051
couchdb_defport = 5984
services = {}
network_name = "byfn"

def generate_crypto_config(_orgs=2, _peers=2, _orderers=3, _domain="dredev.de"):
    domain = _domain
    anzpeers = _peers
    anzorderers = _orderers
    anzorgs = _orgs
    new_yaml = ruamel.yaml.YAML()
    peer_list = []
    specs_list = []
    for i in range(anzorderers):
        specs_list.append({"Hostname": "orderer{}".format(i + 1)})

    for org in range(anzorgs):
        print(bcolors.WARNING + "       [*] Generating Crypto Material for Org{}".format(org))
        peer_list.append({
            "Name": "Org{}".format(org + 1),
            "Domain": "org{}.{}".format(org + 1, domain),
            "Template": {"Count": anzpeers},
            "Users": {"Count": 1},  # Only one user per Org
        })
        print(bcolors.OKGREEN + "       [+] Generating Crypto Material for Org{} COMPLETE".format(org))
    print(bcolors.OKBLUE + "   [*] Generating Final Object")
    final_dict = {
        "OrdererOrgs": [
            {
                "Name": "Orderer",
                "Domain": domain,
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


class Orga:
    def __init__(self, domain, org, orgmsp, ap):
        self.org = org
        self.domain = domain
        self.org_msp = orgmsp
        self.anchor_peer = ap


def tr(s):
    return s.replace('\'<<\'', '<<')  # such output is not valid YAML!


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def generate_chaincode_entries():
    print(bcolors.OKBLUE + "[*] Please Specify your Chaincode that you want to install. We assume that it is a Java Packet within the folder \"chaincodes/java/\".")
    con = "y"
    with open("chaincodes.txt", "w+") as fp:
        while con == "y" or con == "Y":
            try:
                chaincode_name = input("Name of the folder: ")

                # Check if it exists
                if os.path.exists("chaincodes/java/"+chaincode_name):
                    fp.write(chaincode_name + "\n")
                else:
                    print(bcolors.FAIL + "[-] You provided a non existing directory! Nothing written")
                con = input("Add another? (Y/n)")
            except ValueError:
                print(bcolors.FAIL + "[-] Oof, you did not provide proper values. Exiting")
                exit(1)


def generate_configtx(_orgs=2, _orderers=3, _kafka_brokers=4, _consortium="WebConsortium", _domain="dredev.de", _blocksize=10, _timeout=1):
    yaml_new = ruamel.yaml.YAML()

    orgs = [Orga(org="", domain="ordererOrganizations", orgmsp="OrdererMSP", ap=False)]  # Default one orderer!
    for i in range(_orgs):
        orgs.append(
            Orga(org="org{}.".format(i + 1), domain="peerOrganizations", orgmsp="Org{}MSP".format(i + 1), ap=True))

    orga_list = []
    for org in orgs:
        print(bcolors.WARNING + "       [*] Configuring Org {}".format(org.org_msp))
        org_policies = {
            "Readers": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString("OR('{}.member')".format(org.org_msp))
            },
            "Writers": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString("OR('{}.member')".format(org.org_msp))
            },
            "Admins": {
                "Type": 'Signature',
                "Rule": DoubleQuotedScalarString("OR('{}.admin')".format(org.org_msp))
            },
            "Endorsement": {
                "Type": "Signature",
                "Rule": DoubleQuotedScalarString("OR('{}.member')".format(org.org_msp))
            }

        }
        orderer_org = {
            "Name": "{}".format(org.org_msp),
            "ID": "{}".format(org.org_msp),
            "MSPDir": "crypto-config/{}/{}{}/msp".format(org.domain, org.org, _domain),
            "Policies": org_policies
        }
        if org.anchor_peer:
            orderer_org.update({"AnchorPeers": [
                {
                    "Host": "peer0.{}{}".format(org.org, _domain),
                    "Port": 7051
                }
            ]})

        orga_list.append(orderer_org)
        print(bcolors.OKGREEN + "       [+] Configuring for Org {} COMPLETE".format(org.org_msp))
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
                "Rule": DoubleQuotedScalarString("MAJORITY Endorsement"),
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
    kafka_list = []
    for i in range(_orderers):
        orderer_addresses.append("orderer{}.{}:7050".format(i + 1, _domain))

    for i in range(_kafka_brokers):
        kafka_list.append("kafka{}:9092".format(i))

    print(bcolors.WARNING + "       [*] Generating Orderer Config")
    orderer = {
        "OrdererType": "kafka",
        "Addresses": orderer_addresses,

        # Batch Timeout: The amount of time to wait before creating a batch.
        "BatchTimeout": "{}s".format(_timeout),
        "BatchSize": {
            "MaxMessageCount": _blocksize,
            "AbsoluteMaxBytes": "10 MB",
            "PreferredMaxBytes": "2 MB",
        },
        "MaxChannels": 0,
        "Kafka": {
            "Brokers": kafka_list
        },
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
        ord_list.append("orderer{}.{}:7050".format(i + 1, _domain))

    print(bcolors.WARNING + "       [*] Generating Profiles")
    profiles = {
        "OrdererDefault": {
            "<<": channel,
            "Capabilities": {
                "<<": channel_capabilities
            },
            "Orderer": {
                "<<": orderer,
                "OrdererType": "kafka",
                "Addresses": ord_list,
                "Organizations": [orga_list[0]],
                "Capabilities": {
                    "<<": orderer_capabilities,
                }
            },
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


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def generate_env(_name="net"):
    f = open(".env", "w")
    f.write("COMPOSE_PROJECT_NAME={}".format(_name))
    f.close()
    print("========================================")
    print(">>> .env has been dumped!")
    print("========================================")


def generate_docker_compose(_orderers, _orgs, _peers, _domain, _kafka):
    yaml_new = ruamel.yaml.YAML()

    all_node_containers = []
    print(bcolors.OKBLUE + "======== Creating CAs ========")
    for i in range(_orgs):
        print(bcolors.WARNING + "     [*] Generating CA for org{}".format(i + 1))
        ca = {
            "image": "hyperledger/fabric-ca:1.4",
            "environment": [
                "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
                "FABRIC_CA_SERVER_CA_NAME=ca.org{}.{}".format(i + 1, _domain),
                "FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org{}.{}-cert.pem".format(
                    i + 1, _domain),
                "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk"
            ],
            "ports": ["{}:{}".format(ca_defport + i * 1000, ca_defport)],
            "command": "sh -c 'fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org{}.{}-cert.pem --ca.keyfile /etc/hyperledger/fabric-ca-server-config/priv_sk -b admin:adminpw -d'".format(
                i + 1, _domain),
            "volumes": [
                "./crypto-config/peerOrganizations/org{}.{}/ca/:/etc/hyperledger/fabric-ca-server-config".format(i + 1,
                                                                                                                 _domain)
            ],
            "container_name": "ca.org{}.{}".format(i + 1, _domain),
            "networks": [
                network_name
            ]
        }
        services.update({"ca.org{}.{}".format(i + 1, _domain): ca})
        print(bcolors.OKGREEN + "     [+] Generating CA for org{} COMPLETE".format(i + 1))

    print(bcolors.OKBLUE + "======== Creating Zookeeper ========")
    zookeepers = []
    zoo_servers = ""
    zoo_connect = ""
    for i in range(_orderers):
        zoo_servers += "server.{}=zookeeper{}:2888:3888 ".format(i + 1, i + 1)
        zoo_connect += "zookeeper{}:2181,".format(i + 1)
        zookeepers.append("zookeeper{}".format(i + 1))
    zoo_servers = zoo_servers[:-1]
    zoo_connect = zoo_connect[:-1]
    for i in range(_orderers):
        print(bcolors.WARNING + "     [*] Generating Zookeeper{}".format(i + 1))
        zoo = {
            "image": "hyperledger/fabric-zookeeper",
            "container_name": "zookeeper{}".format(i + 1),
            "restart": "always",
            "environment": [
                "ZOO_MY_ID={}".format(i + 1),
                "ZOO_SERVERS=" + zoo_servers
            ],
            "ports": [
                2181,
                2888,
                3888,
            ],
            "networks": [
                network_name
            ]
        }
        services.update({"zookeeper{}".format(i + 1): zoo})
        print(bcolors.OKGREEN + "     [+] Zookeeper{} complete".format(i + 1))

    print(bcolors.OKBLUE + "======== Creating Kafka Brokers ========")

    for i in range(_kafka):
        print(bcolors.WARNING + "     [*] Generating Kafka{}".format(i))
        ka = {
            "image": "hyperledger/fabric-kafka",
            "container_name": "kafka{}".format(i),
            #        restart: always
            "environment": [
                "KAFKA_ADVERTISED_HOST_NAME=kafka{}".format(i),
                "KAFKA_ADVERTISED_PORT=9092",
                "KAFKA_BROKER_ID={}".format(i ),
                "KAFKA_MESSAGE_MAX_BYTES=103809024",  # 99 * 1024 * 1024 B
                "KAFKA_REPLICA_FETCH_MAX_BYTES=103809024",  # 99 * 1024 * 1024 B
                "KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false",
                "KAFKA_NUM_REPLICA_FETCHERS=1",
                "KAFKA_DEFAULT_REPLICATION_FACTOR={}".format(i+1),
                "KAFKA_ZOOKEEPER_CONNECT=" + zoo_connect
            ],
            "ports": [
                9092
            ],
            "depends_on": zookeepers,
            "networks": [
                network_name
            ]

        }
        services.update({"kafka{}".format(i): ka})
        print(bcolors.OKGREEN + "     [+] Kafka{} Completed".format(i))

    print(bcolors.OKBLUE + "======= Generating Orderers =======")
    kafka_brokers = ""
    kafka_broker_list = []
    for i in range(_kafka):
        kafka_brokers += "kafka{}:9092,".format(i)
        kafka_broker_list.append("kafka{}".format(i))
    kafka_brokers = kafka_brokers[:-1]
    orderer_str = ""
    for i in range(_orderers):
        print(bcolors.WARNING + "     [*] Generating Orderer{}".format(i + 1))
        order = {
            "container_name": "orderer{}.{}".format(i + 1, _domain),
            "image": "hyperledger/fabric-orderer:2.0",
            "environment": [
                "ORDERER_HOST=orderer{}.{}".format(i + 1, _domain),
                "ORDERER_GENERAL_LOGLEVEL=debug",
                "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0",
                "ORDERER_GENERAL_LISTENPORT={}".format(orderer_defport),
                "ORDERER_GENERAL_GENESISMETHOD=file",
                "ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block",
                "ORDERER_GENERAL_LOCALMSPID=OrdererMSP",
                "ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp",
                # Kafka Orderer Type
                "CONFIGTX_ORDERER_BATCHTIMEOUT=1s",
                "CONFIGTX_ORDERER_ORDERERTYPE=kafka",
                "CONFIGTX_ORDERER_KAFKA_BROKERS=[{}]".format(kafka_brokers),
                "ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s",
                "ORDERER_KAFKA_RETRY_SHORTTOTAL=30s",
                "ORDERER_KAFKA_VERBOSE=true",
                "ORDERER_ABSOLUTEMAXBYTES=10 MB",
                "ORDERER_PREFERREDMAXBYTES=512 KB"
            ],
            "working_dir": "/opt/gopath/src/github.com/hyperledger/fabric/orderer",
            "command": "orderer",
            "ports": [
                "{}:{}".format(orderer_defport + i * 1000, orderer_defport)
            ],
            "volumes": [
                "./config/:/etc/hyperledger/configtx",
                "./crypto-config/ordererOrganizations/{}/orderers/orderer{}.{}/:/etc/hyperledger/msp/orderer".format(
                    _domain, i + 1, _domain)
            ],
            "networks": [
                network_name
            ],
            "depends_on": kafka_broker_list
        }
        services.update({"orderer{}.{}".format(i + 1, _domain): order})
        all_node_containers.append("orderer{}.{}".format(i + 1, _domain))
        orderer_str += "-o localhost:{} ".format(orderer_defport + i * 1000)
        print(bcolors.OKGREEN + "     [+] Orderer{} COMPLETE".format(i + 1))

    os.environ["ORDERERS"] = orderer_str

    print(bcolors.OKBLUE + "======= Generating Peers for Organizations =======")
    peer_addresses = ""
    basepath = os.getcwd() + "/crypto-config"
    for org in range(_orgs):
        print(bcolors.WARNING + " [*] Generating org{}.{}".format(org + 1, _domain))
        for peer in range(_peers):
            peer_addresses += "--peerAddresses localhost:{} --tlsRootCertFiles {}/peerOrganizations/org{}.{}/peers/peer{}.org{}.{}/tls/ca.crt ".format(
                peer_defport + 1000 * ((_peers * org) + peer), basepath, org + 1, _domain, peer, org + 1, _domain)
            print(bcolors.WARNING + "     [+] Generating peer{}.org{}.{}".format(peer, org + 1, _domain))
            pe = {
                "container_name": "peer{}.org{}.{}".format(peer, org + 1, _domain),
                "image": "hyperledger/fabric-peer:2.0",
                "environment": [
                    "CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock",
                    "CORE_LOGGING_PEER=debug",
                    "CORE_CHAINCODE_LOGGING_LEVEL=DEBUG",
                    "CORE_PEER_ID=peer{}.org{}.{}".format(peer, org + 1, _domain),
                    "CORE_PEER_ADDRESS=peer{}.org{}.{}:{}".format(peer, org + 1, _domain, peer_defport),
                    "CORE_PEER_LOCALMSPID=Org{}MSP".format(org + 1),
                    "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/",
                    "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_" + network_name,
                    "CORE_LEDGER_STATE_STATEDATABASE=CouchDB",
                    "CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb{}.org{}.{}:{}".format(peer, org + 1,
                                                                                                  _domain,
                                                                                                  couchdb_defport),
                    # The CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME and CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD
                    # provide the credentials for ledger to connect to CouchDB.  The username and password must
                    # match the username and password set for the associated CouchDB.
                    "CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=",
                    "CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=",
                ],
                "working_dir": "/opt/gopath/src/github.com/hyperledger/fabric",
                "command": "peer node start",
                "ports": [
                    "{}:{}".format(peer_defport + 1000 * ((_peers * org) + peer), peer_defport),
                    "{}:{}".format((peer_defport + 1) + 1000 * ((_peers * org) + peer), (peer_defport + 1)),
                    "{}:{}".format((peer_defport + 2) + 1000 * ((_peers * org) + peer), (peer_defport + 2)),
                ],
                "volumes": [
                    "/var/run/:/host/var/run/",
                    "./crypto-config/peerOrganizations/org{}.{}/peers/peer{}.org{}.{}/msp:/etc/hyperledger/msp/peer".format(
                        org + 1, _domain, peer, org + 1, _domain),
                    "./crypto-config/peerOrganizations/org{}.{}/users:/etc/hyperledger/msp/users".format(org + 1,
                                                                                                         _domain),
                    "./config:/etc/hyperledger/configtx"
                ],
                "depends_on": [
                    "couchdb{}.org{}.{}".format(peer, org + 1, _domain)
                ],
                "networks": [
                    network_name
                ]
            }
            services.update({"peer{}.org{}.{}".format(peer, org + 1, _domain): pe})
            all_node_containers.append("peer{}.org{}.{}".format(peer, org + 1, _domain))
            print(bcolors.OKGREEN + "     [+] peer{}.org{}.{} COMPLETE".format(peer, org + 1, _domain))
            print(bcolors.WARNING + "     [*] Generating couchdb{}.org{}.{}".format(peer, org + 1, _domain))
            cdb = {
                "container_name": "couchdb{}.org{}.{}".format(peer, org + 1, _domain),
                "image": "hyperledger/fabric-couchdb",
                # Populate the COUCHDB_USER and COUCHDB_PASSWORD to set an admin user and password
                # for CouchDB.  This will prevent CouchDB from operating in an "Admin Party" mode.
                "environment": [
                    "COUCHDB_USER=",
                    "COUCHDB_PASSWORD="
                ],
                "ports": [
                    "{}:{}".format(couchdb_defport + 1000 * ((_peers * org) + peer), couchdb_defport),
                ],
                "networks": [
                    network_name
                ]
            }
            services.update({"couchdb{}.org{}.{}".format(peer, org + 1, _domain): cdb})
            all_node_containers.append("couchdb{}.org{}.{}".format(peer, org + 1, _domain))
            print(bcolors.OKGREEN + "     [+] couchdb{}.org{}.{} COMPLETE".format(peer, org + 1, _domain))

        print(bcolors.OKGREEN + " [+] .org{}.{} COMPLETE".format(org + 1, _domain))
    os.environ["PEER_CON_PARAMS"] = peer_addresses

    print(bcolors.OKBLUE + "======= Generating CLI =======")
    print(bcolors.WARNING + " [*] CLI Generation started")
    cli = {
        "container_name": "cli",
        "image": "hyperledger/fabric-tools",
        "tty": True,
        # stdin_open: true
        "environment": [
            "GOPATH=/opt/gopath",
            "CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock",
            "FABRIC_LOGGING_SPEC=DEBUG",
            "CORE_PEER_ID=cli",
            "CORE_PEER_ADDRESS=peer0.org1.{}:{}".format(_domain, peer_defport),
            "CORE_PEER_LOCALMSPID=Org1MSP",
            "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.{}/users/Admin@org1.{}/msp".format(
                _domain, _domain),
            "CORE_CHAINCODE_KEEPALIVE=10"
        ],
        "working_dir": "/opt/gopath/src/github.com/hyperledger/fabric/peer",
        "command": "/bin/bash",
        "volumes": [
            "/var/run/:/host/var/run/",
            "./chaincodes/java:/opt/gopath/src/github.com/chaincodes/java",
            "./crypto-config:/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/",
            "./config:/etc/hyperledger/configtx"
        ],
        "networks": [
            network_name
        ],
        "depends_on": all_node_containers
    }
    services.update({"cli": cli})
    print(bcolors.OKGREEN + " [+] CLI Generation COMPLETE")

    print(bcolors.OKBLUE + "======= Generating final Structure =======")
    final = {
        "version": ruamel.yaml.scalarstring.SingleQuotedScalarString("2"),
        "networks": {
            network_name: None
        },
        "services": services
    }

    # yaml_new.dump(final, sys.stdout)
    f = open("docker-compose.yaml", "w")
    yaml_new.dump(final, f)
    print(bcolors.HEADER + "========================================")
    print(">>> docker-compose.yaml has been dumped!")
    print("========================================")


def generate_core():

    yaml_new = ruamel.yaml.YAML()
    print(bcolors.WARNING + "     [*] Generating Peer Core")
    peer = {
        "id": "peer",
        "networkId": "byfn",
        "listenAddress": "0.0.0.0:7051",
        "address": "0.0.0.0:7051",
        "addressAutoDetect": False,
        "keepalive": {
            "interval": "7200s",
            "timeout": "20s",
            "minInterval": "60s",
            "client": {
                "interval": "60s",
                "timeout": "20s",
            },
            "deliveryClient": {
                "interval": "60s",
                "timeout": "20s"
            }
        },
        "gossip": {
            "bootstrap": "127.0.0.1:7051",
            "useLeaderElection": True,
            "orgLeader": False,
            "membershipTrackerInterval": "5s",
            "endpoint": None,
            "maxBlockCountToStore": 100,
            "maxPropagationBurstLatency": "10ms",
            "maxPropagationBurstSize": 10,
            "propagateIterations": 1,
            "propagatePeerNum": 3,
            "pullInterval": "4s",
            "pullPeerNum": 3,
            "requestStateInfoInterval": "4s",
            # Determines frequency of pushing state info messages to peers(unit: second)
            "publishStateInfoInterval": "4s",
            # Maximum time a stateInfo message is kept until expired
            "stateInfoRetentionInterval": None,
            # Time from startup certificates are included in Alive messages(unit: second)
            "publishCertPeriod": "10s",
            # Should we skip verifying block messages or not (currently not in use)
            "skipBlockVerification": False,
            # Dial timeout(unit: second)
            "dialTimeout": "3s",
            # Connection timeout(unit: second)
            "connTimeout": "2s",
            # Buffer size of received messages
            "recvBuffSize": 20,
            # Buffer size of sending messages
            "sendBuffSize": 200,
            # Time to wait before pull engine processes incoming digests (unit: second)
            # Should be slightly smaller than requestWaitTime
            "digestWaitTime": "1s",
            # Time to wait before pull engine removes incoming nonce (unit: milliseconds)
            # Should be slightly bigger than digestWaitTime
            "requestWaitTime": "1500ms",
            # Time to wait before pull engine ends pull (unit: second)
            "responseWaitTime": "2s",
            # Alive check interval(unit: second)
            "aliveTimeInterval": "5s",
            # Alive expiration timeout(unit: second)
            "aliveExpirationTimeout": "25s",
            # Reconnect interval(unit: second)
            "reconnectInterval": "25s",
            # This is an endpoint that is published to peers outside of the organization.
            # If this isn't set, the peer will not be known to other organizations.
            "externalEndpoint": None,
            # Leader election service configuration
            "election": {
                # Longest time peer waits for stable membership during leader election startup (unit: second)
                "startupGracePeriod": "15s",
                # Interval gossip membership samples to check its stability (unit: second)
                "membershipSampleInterval": "1s",
                # Time passes since last declaration message before peer decides to perform leader election (unit: second)
                "leaderAliveThreshold": "10s",
                # Time between peer sends propose message and declares itself as a leader (sends declaration message) (unit: second)
                "leaderElectionDuration": "5s"
            },
            "pvtData": {
                "pullRetryThreshold": "60s",
                "transientstoreMaxBlockRetention": 1000,
                "pushAckTimeout": "3s",
                "btlPullMargin": 10,
                "reconcileBatchSize": 10,
                "reconcileSleepInterval": "1m",
                "reconciliationEnabled": True,
                "skipPullingInvalidTransactionsDuringCommit": False,
            },
            "state": {
                "enabled": True,
                "checkInterval": "10s",
                "responseTimeout": "3s",
                "batchSize": 10,
                "blockBufferSize": 100,
                "maxRetries": 3
            },
        },
        "tls": {
            "enabled":  False,
            "clientAuthRequired": False,
            "cert": {
                "file": "tls/server.crt",
            },
            "key": {
                "file": "tls/server.key",
            },
            "rootcert": {
                "file": "tls/ca.crt",
            },
            "clientRootCAs": {
                "files": [
                    "tls/ca.crt"
                ]
            },
            "clientKey": {
                "file": None
            },
            "clientCert": {
                "file": None
            }
        },
        "authentication": {
            "timewindow": "15m"
        },
        "fileSystemPath": "/var/hyperledger/production",
        "BCCSP": {
            "Default": "SW",
            "SW": {
                "Hash": "SHA2",
                "Security": 256,
                "FileKeyStore": {
                    "KeyStore": None,
                },
            },
            "PKCS11": {
                "Library": None,
                "Label": None,
                "Pin": None,
                "Hash": None,
                "Security": None
            }
        },
        "mspConfigPath": "msp",
        "localMspId": "SampleOrg",
        "client": {
            "connTimeout": "3s"
        },
        "deliveryclient": {
            "reconnectTotalTimeThreshold": "3600s",
            "connTimeout": "3s",
            "reConnectBackoffThreshold": "3600s",
            "addressOverrides": None,
        },
        "localMspType": "bccsp",
        "profile": {
            "enabled": False,
            "listenAddress": "0.0.0.0:6060"
        },
        "handlers": {
            "authFilters": [
                { "name": "DefaultAuth" },
                { "name": "ExpirationCheck" },
            ],
            "decorators": [
                { "name": "DefaultDecorator" }
            ],
            "endorsers": {
                "escc": {
                    "name": "DefaultEndorsement",
                    "library": None,
                }
            },
            "validators": {
                "vscc": {
                    "name": "DefaultValidation",
                    "library": None,
                }
            }
        },
        "validatorPoolSize": None,
        "discovery": {
            "enabled": True,
            "authCacheEnabled": True,
            "authCacheMaxSize": 1000,
            "authCachePurgeRetentionRatio": 0.75,
            "orgMembersAllowedAccess": False,
        },
        "limits": {
            "concurrency": {
                "qscc": 5000,
            }
        }
    }
    print(bcolors.OKGREEN + "     [+] Generating Peer Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating VM Core ")
    vm = {
        "endpoint": "unix:///var/run/docker.sock",
        "docker": {
            "tls": {
                "enabled": False,
                "ca": {
                    "file": "docker/ca.crt",
                },
                "cert": {
                    "file": "docker/tls.crt",
                },
                "key": {
                    "file": "docker/tls.key",
                },
            },
            "attachStdout": False,
            "hostConfig": {
                "NetworkMode": "host",
                "Dns": None,
                "LogConfig": {
                    "Type": "json-file",
                    "Config": {
                        "max-size": DoubleQuotedScalarString("50m"),
                        "max-file": DoubleQuotedScalarString("5")
                    }
                },
                "Memory": 2147483648
            }
        }
    }

    print(bcolors.OKGREEN + "     [+] Generating VM Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating Chaincode Core ")
    chaincode = {
        "id": {
            "path": None,
            "name": None,
        },
        "builder": "$(DOCKER_NS)/fabric-ccenv:$(TWO_DIGIT_VERSION)",
        "pull": False,
        "golang": {
            "runtime": "$(DOCKER_NS)/fabric-baseos:$(TWO_DIGIT_VERSION)",
            "dynamicLink": False,
        },
        "java": {
            "runtime": "$(DOCKER_NS)/fabric-javaenv:$(TWO_DIGIT_VERSION)",
        },
        "node": {
            "runtime": "$(DOCKER_NS)/fabric-nodeenv:$(TWO_DIGIT_VERSION)",
        },
        "externalBuilders": [],
        "installTimeout": "300s",
        "startuptimeout": "300s",
        "executetimeout": "30s",
        "mode": "net",
        "keepalive": 0,
        "system": {
            "_lifecycle": "enable",
            "cscc": "enable",
            "lscc": "enable",
            "escc": "enable",
            "vscc": "enable",
            "qscc": "enable",
        },
        "logging": {
            "level":  "info",
            "shim":   "warning",
            "format": ruamel.yaml.scalarstring.SingleQuotedScalarString('%{color}%{time:2006-01-02 15:04:05.000 MST} [%{module}] %{shortfunc} -> %{level:.4s} %{id:03x}%{color:reset} %{message}')
        }
    }

    print(bcolors.OKGREEN + "     [+] Generating Chaincode Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating Ledger Core ")
    ledger = {
        "blockchain": None,
        "state": {
            "stateDatabase": "goleveldb",
            "totalQueryLimit": 100000,
            "couchDBConfig": {
                "couchDBAddress": "127.0.0.1:5984",
                "username": None,
                "password": None,
                "maxRetries": 3,
                "maxRetriesOnStartup": 12,
                "requestTimeout": "35s",
                "internalQueryLimit": 1000,
                "maxBatchUpdateSize": 1000,
                "warmIndexesAfterNBlocks": 1,
                "createGlobalChangesDB": False,
                "cacheSize": 64,
            }
        },
        "history": {
            "enableHistoryDatabase": True,
        },
        "pvtdataStore": {
            "collElgProcMaxDbBatchSize": 5000,
            "collElgProcDbBatchesInterval": 1000
        }

    }

    print(bcolors.OKGREEN + "     [+] Generating Ledger Core COMPLETE")
    print(bcolors.WARNING + "     [*] Generating Operations Core ")
    operations = {
        "listenAddress": "127.0.0.1:9443",
        "tls": {
            "enabled": False,
            "cert": {
                "file": None,
            },
            "key": {
                "file": None,
            },
            "clientAuthRequired": False,
            "clientRootCAs": {
                "files": []
            }
        }
    }
    print(bcolors.OKGREEN + "     [+] Generating Operations Core COMPLETE")
    print(bcolors.WARNING + "     [*] Generating Metrics Core ")

    metrics = {
        "provider": "disabled",
        "statsd": {
            "network": "udp",
            "address": "127.0.0.1:8125",
            "writeInterval": "10s",
            "prefix": None
        }
    }
    print(bcolors.OKGREEN + "     [*] Generating Metrics Core COMPLETE")

    print(bcolors.OKBLUE + "======= Generating final Structure =======")
    final = {
        "peer": peer,
        "vm": vm,
        "chaincode": chaincode,
        "ledger": ledger,
        "operations": operations,
        "metrics": metrics
    }

    # yaml_new.dump(final, sys.stdout)
    f = open("core.yaml", "w")
    yaml_new.dump(final, f)
    print(bcolors.HEADER + "========================================")
    print(">>> core.yaml has been dumped!")
    print("========================================")


def create_connection_profile(_peers, _orgs, _orderers, _domain):
    new_yaml = ruamel.yaml.YAML()
    orderer_list = ["orderer{}.{}".format(i+1, _domain) for i in range(_orderers)]
    print(bcolors.WARNING + "[*] Creating Connection Profile")
    peer_list = {}
    print(bcolors.WARNING + "   [*] Create Peer List")
    for peer in range(_peers):
        for org in range(_orgs):
            peer_list.update({"peer{}.org{}.{}".format(peer, org+1, _domain): {
                "endorsingPeer": True,
                "chaincodeQuery": True,
                "ledgerQuery": True,
                "eventSource": True,
            }})
    print(bcolors.OKGREEN + "   [+] Peer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Channel List")

    channels = {
        "mychannel": {
            "orderers": orderer_list,
            "peers": peer_list
        }
    }
    print(bcolors.OKGREEN + "   [+] Channel List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Organization List")
    organiz = {}
    for org in range(_orgs):
        peers_ls = ["peer{}.org{}.{}".format(i, org+1, _domain) for i in range(_peers)]
        organiz.update({"Org{}".format(org+1): {
            "mspid": "Org{}MSP".format(org+1),
            "peers": peers_ls,
            "certificateAuthorities": [
                "ca.org{}.{}".format(org+1, _domain)
            ]
        }})
    print(bcolors.OKGREEN + "   [+] Organization List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Orderer List")

    ordes = {}
    i = 0
    for orderer in orderer_list:
        ordes.update({
            orderer: {
                "url": "grpc://localhost:{}".format(orderer_defport+1000*i),
                "grpcOptions": {
                    "ssl-target-name-override": orderer
                }
            }
        })
        i += 1
    print(bcolors.OKGREEN + "   [+] Orderer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Detail Peer List")

    peer_ls = {}
    for peer in range(_peers):
        for org in range(_orgs):
            peer_ls.update({"peer{}.org{}.{}".format(peer, org+1, _domain): {
                "url": "grpc://localhost:{}".format(peer_defport + 1000 * ((_peers * org) + peer), peer_defport),
                "grpcOptions": {
                    "ssl-target-name-override": "peer{}.org{}.{}".format(peer, org+1, _domain),
                    "request-timeout": 120001
                }
            }})
    print(bcolors.OKGREEN + "   [+] Detail Peer List COMPLETE")
    print(bcolors.WARNING + "   [*] Create Detail CA List")

    ca_ls = {}
    i = 0
    for org in range(_orgs):
        ca_ls.update({
            "ca.org{}.{}".format(org+1, _domain): {
                "url": "http://localhost:{}".format(ca_defport+1000*i),
                "httpOptions": {
                    "verify": False,
                },
                "registrar": [
                    {
                        "enrollId": "admin",
                        "enrollSecret": "adminpw"
                    }
                ],
                "caName": "ca.org{}.{}".format(org+1, _domain)
            }
        })
        i += 1
    print(bcolors.OKGREEN + "   [+] Detail CA List COMPLETE")
    print(bcolors.OKBLUE + "======= Generating final Structure =======")

    final = {
        "name": DoubleQuotedScalarString("{}-peer.{}-org.{}-orderers.{}".format(_peers, _orgs, _orderers, _domain)),
        "x-type": DoubleQuotedScalarString("hlfv2"),
        "description": DoubleQuotedScalarString("Connection profile"),
        "version": DoubleQuotedScalarString("1.0"),
        "channels": channels,
        "organizations": organiz,
        "orderers": ordes,
        "peers": peer_ls,
        "certificateAuthorities": ca_ls
    }
    print(bcolors.OKBLUE + "======= Final Structure COMPLETE =======")

    f = open("connection_profile.yaml", "w")
    new_yaml.dump(final, f)
    f.close()
    print(bcolors.OKGREEN + "[+] Connection Profile Created")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automated Hyperledger Fabic Network Generator.")
    parser.add_argument('-o', dest="orderers", default=4, type=int, help='Number of Orderers ')
    parser.add_argument('-O', dest="orgs", default=2, type=int, help='Number of Organizations ')
    parser.add_argument('-p', dest="peers", default=2, type=int, help='Number of Peers per Organization ')
    parser.add_argument('-k', dest="kafka", default=4, type=int, help='Number of Kafka Brokers ')
    parser.add_argument('-d', dest="domain", default="dredev.de", type=str, help='The Domain that will be used')
    parser.add_argument('-c', dest="consortium", default="WebConsortium", type=str,
                        help='The Consortium that will be used')
    parser.add_argument('-bs', dest="blocksize", default=10, type=int, help='The max amount of transactions per block')
    parser.add_argument('-t', dest="timeout", default=1, type=int, help='The timeout value in seconds until a block gets committed, if it is not filled to its blocksize')
    args = parser.parse_args()
    compose_name = "net"
    try:
        f = open("docker-compose.yaml")
        f.close()
        print("What have we got over here? A lonely Docker compose file. Lets stop it!")
        os.system("docker-compose down --volumes --remove-orphans")
        os.system("docker container rm $(docker container ls -a | grep dev-peer)")
        os.system("docker images -a | grep 'dev-peer' | awk '{print $3}' | xargs docker rmi")
    # Do something with the file
    except IOError:
        pass

    print(bcolors.FAIL + ">>> Alright, now let's go! <<< ")
    generate_chaincode_entries()
    print(bcolors.HEADER + ">>> First we need to create a file called '.env'. It includes a Variable for the docker-compose file")
    generate_env(compose_name)
    print(bcolors.HEADER + ">>> Ok that's done. Now lets create the Crypto Config File!")
    generate_crypto_config(_peers=args.peers,
                           _domain=args.domain,
                           _orderers=args.orderers,
                           _orgs=args.orgs)
    print(bcolors.HEADER + ">>> Crypto Config has been created. Now lets create the config file for the transactions!")
    generate_configtx(_orgs=args.orgs,
                      _orderers=args.orderers,
                      _domain=args.domain,
                      _kafka_brokers=args.kafka,
                      _consortium=args.consortium,
                      _blocksize=args.blocksize,
                      _timeout=args.timeout)
    print(bcolors.HEADER + ">>> config.tx has been created. Now generate the Docker-compose file.")
    generate_docker_compose(_orderers=args.orderers,
                            _orgs=args.orgs,
                            _peers=args.peers,
                            _domain=args.domain,
                            _kafka=args.kafka)
    print(bcolors.HEADER + ">>> docker-compose.yaml has been created. Now finally generate the core.yaml file.")
    generate_core()
    print(bcolors.HEADER + ">>> core.yaml has been created.")
    create_connection_profile(_peers=args.peers,
                              _orgs=args.orgs,
                              _orderers=args.orderers,
                              _domain=args.domain)
    print(bcolors.HEADER + ">>> All done, you can proceed with Merlin! Bye")
    # Setting some Env Variable
    os.environ["NO_ORDERERS"] = str(args.orderers)
    os.environ["NO_ORGANIZATIONS"] = str(args.orgs)
    os.environ["NO_PEERS"] = str(args.peers)
    os.environ["DOMAIN"] = args.domain
    os.environ["NO_KAFKA"] = str(args.kafka)
    os.environ["CONSORTIUM_NAME"] = args.consortium

    env_str = "export NO_ORDERERS="+str(args.orderers) + "\n"
    env_str += "export ORDERERS=\""+str(os.environ["ORDERERS"]) + "\"\n"
    env_str += "export PEER_CON_PARAMS=\""+str(os.environ["PEER_CON_PARAMS"]) + "\"\n"
    env_str += "export NO_PEERS=" + str(args.peers) + "\n"
    env_str += "export NO_ORGANIZATIONS=" + str(args.orgs) + "\n"
    env_str += "export NO_PEERS=" + str(args.peers) + "\n"
    env_str += "export DOMAIN=" + str(args.domain) + "\n"
    env_str += "export NO_KAFKA=" + str(args.kafka) + "\n"
    env_str += "export CONSORTIUM_NAME=" + str(args.consortium) + "\n"

    y = input(bcolors.FAIL + "Start Merlin now? [y/n]")
    if y == "y":
        out = input(bcolors.FAIL + "Do you want Debug output? [y/n]")
        if out == "n":
            os.environ["OUTPUTDEV"] = "/dev/null"
            env_str += "export OUTPUTDEV=/dev/null\n"
        os.system(env_str + " bash merlin.sh")
    else:
        print(bcolors.HEADER + "Alright, Quitting")

