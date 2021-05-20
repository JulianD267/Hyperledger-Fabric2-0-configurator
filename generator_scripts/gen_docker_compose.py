import ruamel.yaml
from generator_scripts.format import bcolors, NetworkConfiguration
import os
from ruamel.yaml.scalarstring import SingleQuotedScalarString


def generate_docker_compose(_network_config: NetworkConfiguration,
                            _orderers,
                            _orgs,
                            _peers,
                            _domain,
                            _kafka_nodes=2):
    """
    This function will create a docker-compose.yaml file within the current workdir.
    :param _network_config: The Network Configuration structure, containing Ports and stuff
    :param _orderers: the number of orderers to configure
    :param _orgs: the number of organizations to configure
    :param _peers: the number of peers to configure
    :param _domain: the domain of the channel
    :param _kafka_nodes: (Optional) the number of kafka nodes, if kafka ordering is enabled
    """
    yaml_new = ruamel.yaml.YAML()
    services = {}       # Docker Compose Services

    all_node_containers = []
    print(bcolors.OKBLUE + "======== Creating CAs ========")
    for i in range(_orgs):
        print(bcolors.WARNING + f"     [*] Generating CA for org{i + 1}")
        ca = {
            "image": "hyperledger/fabric-ca:1.4",
            "environment": [
                "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
                f"FABRIC_CA_SERVER_CA_NAME=ca.org{i+1}.{_domain}",
                f"FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org{i+1}.{_domain}-cert.pem",
                "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk",
                "FABRIC_CA_SERVER_TLS_ENABLED=true",
                f"FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/"
                f"ca.org{i+1}.{_domain}-cert.pem",
                "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk"
            ],
            "ports": [f"{_network_config.ca_defport + i * 1000}:{_network_config.ca_defport}"],
            "command": f"sh -c 'fabric-ca-server start "
                       f"--csr.hosts ca.org{i+1}.{_domain},localhost "    
                       f"--ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org{i + 1}.{_domain}-cert.pem "
                       f"--ca.keyfile /etc/hyperledger/fabric-ca-server-config/priv_sk -b admin:adminpw -d'",
            "volumes": [
                f"./crypto-config/peerOrganizations/org{i + 1}.{_domain}/ca/:/etc/hyperledger/fabric-ca-server-config"
            ],
            "container_name": f"ca.org{i+1}.{_domain}",
            "networks": [
                _network_config.network_name
            ]
        }
        services.update({f"ca.org{i + 1}.{_domain}": ca})
        print(bcolors.OKGREEN + f"     [+] Generating CA for org{i + 1} COMPLETE")

    if _network_config.ordering_service is "kafka":
        print(bcolors.OKBLUE + "======== Creating Zookeeper ========")
        zookeepers = []
        zoo_servers = ""
        zoo_connect = ""
        for i in range(_kafka_nodes):
            zoo_servers += f"server.{i + 1}=zookeeper{i + 1}:2888:3888 "
            zoo_connect += f"zookeeper{i + 1}:2181,"
            zookeepers.append(f"zookeeper{i + 1}")
        zoo_servers = zoo_servers[:-1]
        zoo_connect = zoo_connect[:-1]
        for i in range(_kafka_nodes):
            print(bcolors.WARNING + f"     [*] Generating Zookeeper{i + 1}")
            zoo = {
                "image": "hyperledger/fabric-zookeeper",
                "container_name": f"zookeeper{i + 1}",
                "restart": "always",
                "environment": [
                    f"ZOO_MY_ID={i + 1}",
                    "ZOO_SERVERS=" + zoo_servers
                ],
                "ports": [
                    2181,
                    2888,
                    3888,
                ],
                "networks": [
                    _network_config.network_name
                ]
            }
            services.update({f"zookeeper{i + 1}": zoo})
            print(bcolors.OKGREEN + f"     [+] Zookeeper{i + 1} complete")

        print(bcolors.OKBLUE + "======== Creating Kafka Brokers ========")

        for i in range(_kafka_nodes):
            print(bcolors.WARNING + f"     [*] Generating Kafka{i}")
            ka = {
                "image": "hyperledger/fabric-kafka",
                "container_name": f"kafka{i}",
                #        restart: always
                "environment": [
                    f"KAFKA_ADVERTISED_HOST_NAME=kafka{i}",
                    "KAFKA_ADVERTISED_PORT=9092",
                    f"KAFKA_BROKER_ID={i}",
                    "KAFKA_MESSAGE_MAX_BYTES=103809024",  # 99 * 1024 * 1024 B
                    "KAFKA_REPLICA_FETCH_MAX_BYTES=103809024",  # 99 * 1024 * 1024 B
                    "KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false",
                    "KAFKA_NUM_REPLICA_FETCHERS=1",
                    f"KAFKA_DEFAULT_REPLICATION_FACTOR={i+1}",
                    "KAFKA_ZOOKEEPER_CONNECT=" + zoo_connect
                ],
                "ports": [
                    9092
                ],
                "depends_on": zookeepers,
                "networks": [
                    _network_config.network_name
                ]

            }
            services.update({f"kafka{i}": ka})
            print(bcolors.OKGREEN + f"     [+] Kafka{i} Completed")

    print(bcolors.OKBLUE + "======= Generating Orderers =======")
    if _network_config.ordering_service is "kafka":
        kafka_brokers = ""
        kafka_broker_list = []
        for i in range(_kafka_nodes):
            kafka_brokers += f"kafka{i}:9092,"
            kafka_broker_list.append(f"kafka{i}")
        kafka_brokers = kafka_brokers[:-1]

    orderer_str = ""
    for i in range(_orderers):
        print(bcolors.WARNING + f"     [*] Generating Orderer{i + 1}")
        env = [
            f"ORDERER_HOST=orderer{i + 1}.{_domain}",
            "ORDERER_GENERAL_LOGLEVEL=debug",
            "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0",
            f"ORDERER_GENERAL_LISTENPORT={_network_config.orderer_defport}",
            "ORDERER_GENERAL_GENESISMETHOD=file",
            "ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block",
            "ORDERER_GENERAL_LOCALMSPID=OrdererMSP",
            "ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp",
            "CONFIGTX_ORDERER_BATCHTIMEOUT=1s",
            "ORDERER_GENERAL_CLUSTER_CLIENTCERTIFICATE=/etc/hyperledger/orderer/tls/server.crt",
            "ORDERER_GENERAL_CLUSTER_CLIENTPRIVATEKEY=/etc/hyperledger/orderer/tls/server.key",
            "ORDERER_GENERAL_CLUSTER_ROOTCAS=[/etc/hyperledger/orderer/tls/ca.crt]",
            "ORDERER_ABSOLUTEMAXBYTES=10 MB",
            "ORDERER_PREFERREDMAXBYTES=512 KB"
        ]
        if _network_config.ordering_service is "kafka":
            env.extend(["ORDERER_GENERAL_TLS_ENABLED=true",
                        "ORDERER_GENERAL_TLS_PRIVATEKEY=/etc/hyperledger/orderer/tls/server.key",
                        "ORDERER_GENERAL_TLS_CERTIFICATE=/etc/hyperledger/orderer/tls/server.crt",
                        "ORDERER_GENERAL_TLS_ROOTCAS=[/etc/hyperledger/orderer/tls/ca.crt]",
                        # Raft Orderer Type
                        "CONFIGTX_ORDERER_ORDERERTYPE=kafka",
                        f"CONFIGTX_ORDERER_KAFKA_BROKERS=[{kafka_brokers}]",
                        "ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s",
                        "ORDERER_KAFKA_RETRY_SHORTTOTAL=30s",
                        "ORDERER_KAFKA_VERBOSE=true",
                        ])
        else:
            env.extend(["ORDERER_GENERAL_TLS_ENABLED=true",
                        "ORDERER_GENERAL_TLS_PRIVATEKEY=/etc/hyperledger/orderer/tls/server.key",
                        "ORDERER_GENERAL_TLS_CERTIFICATE=/etc/hyperledger/orderer/tls/server.crt",
                        "ORDERER_GENERAL_TLS_ROOTCAS=[/etc/hyperledger/orderer/tls/ca.crt]",
                        # Raft Orderer Type
                        "CONFIGTX_ORDERER_ORDERERTYPE=etcdraft"
                        ])
        order = {
            "container_name": f"orderer{i + 1}.{_domain}",
            "image": "hyperledger/fabric-orderer:2.0",
            "environment": env,
            "working_dir": "/opt/gopath/src/github.com/hyperledger/fabric/orderer",
            "command": "orderer",
            "ports": [
                f"{_network_config.orderer_defport + i * 1000}:{_network_config.orderer_defport}"   # 8050:7050
            ],
            "volumes": [
                "./config/:/etc/hyperledger/configtx",
                "./config/genesis.block:/etc/hyperledger/orderer/orderer.genesis.block",
                f"./crypto-config/ordererOrganizations/{_domain}/orderers/orderer{i+1}.{_domain}/:"
                f"/etc/hyperledger/msp/orderer",
                f"./crypto-config/ordererOrganizations/{_domain}/orderers/orderer{i + 1}.{_domain}/msp:"
                f"/etc/hyperledger/orderer/msp",
                f"./crypto-config/ordererOrganizations/{_domain}/orderers/orderer{i + 1}.{_domain}/tls/:"
                "/etc/hyperledger/orderer/tls",
            ],
            "networks": [
                _network_config.network_name
            ],
        }
        if _network_config.ordering_service is "kafka":
            order.update({"depends_on": kafka_broker_list})

        services.update({f"orderer{i + 1}.{_domain}": order})
        all_node_containers.append(f"orderer{i + 1}.{_domain}")
        if i == 0:
            # Enabling TLS: We need to only specify one single orderer with Raft. We choose the first one
            # Additionally, since we call the peer tool from external, the override of the orderer TLS Name is mandatory
            # for certificate verification
            orderer_str += f"-o localhost:{_network_config.orderer_defport + i * 1000} " \
                           f"--tls " \
                           f"--ordererTLSHostnameOverride orderer{i+1}.dredev.de " \
                           f"--cafile=./crypto-config/ordererOrganizations/{_domain}/orderers/orderer{i+1}.{_domain}" \
                           f"/msp/tlscacerts/tlsca.{_domain}-cert.pem"

        print(bcolors.OKGREEN + f"     [+] Orderer{i + 1} COMPLETE")

    os.environ["ORDERERS"] = orderer_str

    print(bcolors.OKBLUE + "======= Generating Peers for Organizations =======")
    peer_addresses = ""
    basepath = os.getcwd() + "/crypto-config"
    for org in range(_orgs):
        print(bcolors.WARNING + f" [*] Generating org{org + 1}.{_domain}")
        for peer in range(_peers):
            peer_addresses += f"--peerAddresses " \
                              f"localhost:{_network_config.peer_defport + 1000 * ((_peers * org) + peer)} " \
                              f"--tlsRootCertFiles {basepath}/peerOrganizations/org{org + 1}.{_domain}/" \
                              f"peers/peer{peer}.org{org + 1}.{_domain}/tls/ca.crt "
            print(bcolors.WARNING + f"     [+] Generating peer{peer}.org{org + 1}.{_domain}")
            pe = {
                "container_name": f"peer{peer}.org{org + 1}.{_domain}",
                "image": "hyperledger/fabric-peer:2.0",
                "environment": [
                    "CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock",
                    "CORE_LOGGING_PEER=debug",
                    "CORE_CHAINCODE_LOGGING_LEVEL=DEBUG",
                    f"CORE_PEER_ID=peer{peer}.org{org + 1}.{_domain}",
                    f"CORE_PEER_ADDRESS=peer{peer}.org{org + 1}.{_domain}:{_network_config.peer_defport}",
                    f"CORE_PEER_LOCALMSPID=Org{org + 1}MSP",
                    f"CORE_PEER_CHAINCODEADDRESS=peer{peer}.org{org + 1}.{_domain}:{_network_config.peer_defport+1}",
                    f"CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:{_network_config.peer_defport+1}",
                    "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/",
                    "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_" + _network_config.network_name,
                    "CORE_LEDGER_STATE_STATEDATABASE=CouchDB",
                    f"CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb{peer}.org{org + 1}.{_domain}:"
                    f"{_network_config.couchdb_defport}",
                    # The CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME and CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD
                    # provide the credentials for ledger to connect to CouchDB.  The username and password must
                    # match the username and password set for the associated CouchDB.
                    "CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=",
                    "CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=",
                    "CORE_PEER_TLS_ENABLED=true",
                    "CORE_PEER_GOSSIP_USELEADERELECTION=true",
                    "CORE_PEER_GOSSIP_ORGLEADER=false",

                    f"CORE_PEER_GOSSIP_BOOTSTRAP=peer{peer}.org{org + 1}.{_domain}:{_network_config.peer_defport}",
                    f"CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer{peer}.org{org + 1}.{_domain}:{_network_config.peer_defport}",
                    "CORE_PEER_PROFILE_ENABLED=true",
                    "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
                    "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
                    "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt"
                ],
                "working_dir": "/opt/gopath/src/github.com/hyperledger/fabric",
                "command": "peer node start",
                "ports": [
                    f"{ _network_config.peer_defport   +1000*((_peers * org) + peer)}:{_network_config.peer_defport}",
                    f"{(_network_config.peer_defport+1)+1000*((_peers * org) + peer)}:{_network_config.peer_defport+1}",
                    f"{(_network_config.peer_defport+2)+1000*((_peers * org) + peer)}:{_network_config.peer_defport+2}",
                ],
                "volumes": [
                    "/var/run/:/host/var/run/",
                    f"./crypto-config/peerOrganizations/org{org + 1}.{_domain}/peers/peer{peer}.org{org + 1}.{_domain}/"
                    f"msp:/etc/hyperledger/msp/peer",
                    f"./crypto-config/peerOrganizations/org{org + 1}.{_domain}/peers/peer{peer}.org{org + 1}.{_domain}/"
                    f"tls:/etc/hyperledger/fabric/tls",
                    f"./crypto-config/peerOrganizations/org{org + 1}.{_domain}/users:/etc/hyperledger/msp/users",
                    "./config:/etc/hyperledger/configtx"
                ],
                "depends_on": [
                    f"couchdb{peer}.org{org + 1}.{_domain}"
                ],
                "networks": [
                    _network_config.network_name
                ]
            }
            services.update({f"peer{peer}.org{org + 1}.{_domain}": pe})
            all_node_containers.append(f"peer{peer}.org{org + 1}.{_domain}")
            print(bcolors.OKGREEN + f"     [+] peer{peer}.org{org + 1}.{_domain} COMPLETE")
            print(bcolors.WARNING + f"     [*] Generating couchdb{peer}.org{org + 1}.{_domain}")
            cdb = {
                "container_name": f"couchdb{peer}.org{org + 1}.{_domain}",
                "image": "hyperledger/fabric-couchdb",
                # Populate the COUCHDB_USER and COUCHDB_PASSWORD to set an admin user and password
                # for CouchDB.  This will prevent CouchDB from operating in an "Admin Party" mode.
                "environment": [
                    "COUCHDB_USER=",
                    "COUCHDB_PASSWORD="
                ],
                "ports": [
                    f"{_network_config.couchdb_defport + 1000*((_peers*org)+peer)}:{_network_config.couchdb_defport}"
                ],
                "networks": [
                    _network_config.network_name
                ]
            }
            services.update({f"couchdb{peer}.org{org + 1}.{_domain}": cdb})
            all_node_containers.append(f"couchdb{peer}.org{org + 1}.{_domain}")
            print(bcolors.OKGREEN + f"     [+] couchdb{peer}.org{org + 1}.{_domain} COMPLETE")

        print(bcolors.OKGREEN + f" [+] .org{org + 1}.{_domain} COMPLETE")
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
            f"CORE_PEER_ADDRESS=peer0.org1.{_domain}:{_network_config.peer_defport}",
            "CORE_PEER_LOCALMSPID=Org1MSP",
            f"CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/"
            f"org1.{_domain}/users/Admin@org1.{_domain}/msp",
            "CORE_PEER_TLS_ENABLED=true",
            f"CORE_PEER_TLS_CERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/"
            f"org1.{_domain}/peers/peer0.org1.{_domain}/tls/server.crt",
            f"CORE_PEER_TLS_KEY_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/"
            f"org1.{_domain}/peers/peer0.org1.{_domain}/tls/server.key",
            f"CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/"
            f"org1.{_domain}/peers/peer0.org1.{_domain}/tls/ca.crt",
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
            _network_config.network_name
        ],
        "depends_on": all_node_containers
    }
    services.update({"cli": cli})
    print(bcolors.OKGREEN + " [+] CLI Generation COMPLETE")

    print(bcolors.OKBLUE + "======= Generating final Structure =======")
    final = {
        "version": SingleQuotedScalarString("2"),
        "networks": {
            _network_config.network_name: None
        },
        "services": services
    }

    # yaml_new.dump(final, sys.stdout)
    f = open("docker-compose.yaml", "w")
    yaml_new.dump(final, f)
    print(bcolors.HEADER + "========================================")
    print(">>> docker-compose.yaml has been dumped!")
    print("========================================")
