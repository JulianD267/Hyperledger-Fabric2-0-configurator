import argparse
import os
from generator_scripts.format import bcolors, NetworkConfiguration
from generator_scripts.gen_configtx import generate_configtx
from generator_scripts.gen_connection_profile import generate_connection_profile
from generator_scripts.gen_crypto_config import generate_crypto_config
from generator_scripts.gen_docker_compose import generate_docker_compose
from generator_scripts.gen_core import generate_core
from generator_scripts.gen_env import generate_env
from generator_scripts.gen_node_json import generate_node_json
from generator_scripts.gen_wallet import generate_wallets
config = NetworkConfiguration(_orderer_defport=7050,
                              _peer_defport=7051,
                              _ca_defport=7054,
                              _couchdb_defport=5984,
                              _network_name="byfn",
                              _ordering_service="raft")


def generate_chaincode_entries():
    print(bcolors.OKBLUE + "[*] Please Specify your Chaincode that you want to install. "
                           "We assume that it is a Java Packet within the folder \"chaincodes/java/\".")
    con = "y"
    with open("chaincodes.txt", "w+") as fp:
        while con == "y" or con == "Y":
            try:
                chaincode_name = input(bcolors.OKBLUE + "Name of the folder: ")
                if chaincode_name == "":
                    print("Ok no chaincode to install, continue.")
                    con = "n"
                else:
                    # Check if it exists
                    if os.path.exists("chaincodes/java/"+chaincode_name):
                        fp.write(chaincode_name + "\n")
                    else:
                        print(bcolors.FAIL + "[-] You provided a non existing directory! Nothing written")
                    con = input("Add another? (Y/n)")
            except ValueError:
                print(bcolors.FAIL + "[-] Oof, you did not provide proper values. Exiting")
                exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automated Hyperledger Fabic Network Generator.")
    parser.add_argument('-o', dest="orderers", default=4, type=int, help='Number of Orderers ')
    parser.add_argument('-O', dest="orgs", default=2, type=int, help='Number of Organizations ')
    parser.add_argument('-p', dest="peers", default=2, type=int, help='Number of Peers per Organization ')
    parser.add_argument('-k', dest="kafka", default=-1, type=int, help='Number of Kafka Brokers. NOTE: If you set this,'
                                                                       'Kafka Ordering will be enabled instead of Raft!'
                                                                       )
    parser.add_argument('-d', dest="domain", default="dredev.de", type=str, help='The Domain that will be used')
    parser.add_argument('-c', dest="consortium", default="WebConsortium", type=str,
                        help='The Consortium that will be used')
    parser.add_argument('-bs', dest="blocksize", default=10, type=int, help='The max amount of transactions per block')
    parser.add_argument('-t', dest="timeout", default=1, type=int, help='The timeout value in seconds until a block '
                                                                        'gets committed, if it is not filled to its '
                                                                        'blocksize')
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
    print(bcolors.HEADER + ">>> First we need to create a file called '.env'. "
                           "It includes a Variable for the docker-compose file")
    generate_env(compose_name)
    print(bcolors.HEADER + ">>> Ok that's done. Now lets create the Crypto Config File!")
    if args.kafka < 0:
        kafka = False
        config.ordering_service = "raft"
        print(bcolors.OKBLUE + ">>> USING RAFT")
    else:
        kafka = True
        config.ordering_service = "kafka"
        print(bcolors.OKBLUE + ">>> USING KAFKA")

    generate_crypto_config(_peers=args.peers,
                           _domain=args.domain,
                           _orderers=args.orderers,
                           _orgs=args.orgs)
    print(bcolors.HEADER + ">>> Crypto Config has been created. Now lets create the config file for the transactions!")
    generate_configtx(_network_config=config,
                      _orgs=args.orgs,
                      _orderers=args.orderers,
                      _domain=args.domain,
                      _kafka_brokers=args.kafka,
                      _consortium=args.consortium,
                      _blocksize=args.blocksize,
                      _timeout=args.timeout)
    print(bcolors.HEADER + ">>> config.tx has been created. Now generate the Docker-compose file.")
    generate_docker_compose(_network_config=config,
                            _orderers=args.orderers,
                            _orgs=args.orgs,
                            _peers=args.peers,
                            _domain=args.domain,
                            _kafka_nodes=args.kafka
                            )
    print(bcolors.HEADER + ">>> docker-compose.yaml has been created. Now finally generate the core.yaml file.")
    generate_core()
    print(bcolors.HEADER + ">>> core.yaml has been created.")
    generate_connection_profile(_network_config=config,
                                _peers=args.peers,
                                _orgs=args.orgs,
                                _orderers=args.orderers,
                                _domain=args.domain,
                                _url="localhost")
    print(bcolors.HEADER + ">>> connection_profile.yaml has been created.")

    print(bcolors.HEADER + ">>> All done, you can proceed with Merlin! Bye")
    # Setting some Env Variable
    basic_vars = [
        f"NO_ORDERERS=\"{args.orderers}\"\n",
        f"NO_ORGANIZATIONS=\"{args.orgs}\"\n",
        f"NO_PEERS=\"{args.peers}\"\n",
        f"DOMAIN=\"{args.domain}\"\n"
        f"CONSORTIUM_NAME=\"{args.consortium}\"\n",
        f"ORDERERS=\"{os.environ['ORDERERS']}\"\n",
        f"PEER_CON_PARAMS=\"{os.environ['PEER_CON_PARAMS']}\"\n",
    ]

    connection_params = [
        "CORE_PEER_LOCALMSPID=Org1MSP\n",
        "CORE_PEER_TLS_ENABLED=true\n",
        f"CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org1.{args.domain}/peers/"
        f"peer0.org1.{args.domain}/tls/ca.crt\n",
        f"CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org1.{args.domain}/users/"
        f"Admin@org1.{args.domain}/msp\n",
        f"export CORE_PEER_ADDRESS=localhost:{config.peer_defport}\n",
        "BASEPATH=$PWD/crypto-config\n"
    ]
    if kafka:
        basic_vars.append(f"NO_KAFKA=\"{args.kafka}\"")

    # os.environ["NO_ORDERERS"] = str(args.orderers)
    # os.environ["NO_ORGANIZATIONS"] = str(args.orgs)
    # os.environ["NO_PEERS"] = str(args.peers)
    # os.environ["DOMAIN"] = args.domain
    # os.environ["CONSORTIUM_NAME"] = args.consortium

    # env_str = "export NO_ORDERERS="+str(args.orderers) + "\n"
    # env_str += "export ORDERERS=\""+str(os.environ["ORDERERS"]) + "\"\n"
    # env_str += "export PEER_CON_PARAMS=\""+str(os.environ["PEER_CON_PARAMS"]) + "\"\n"
    # env_str += "export NO_PEERS=" + str(args.peers) + "\n"
    # env_str += "export NO_ORGANIZATIONS=" + str(args.orgs) + "\n"
    # env_str += "export DOMAIN=" + str(args.domain) + "\n"
    # env_str += "export CONSORTIUM_NAME=" + str(args.consortium) + "\n"
    # if kafka:
    #     os.environ["NO_KAFKA"] = str(args.kafka)
    #     env_str += "export NO_KAFKA=" + str(args.kafka) + "\n"
    # print(env_str)
    # Export the Connection Parameters to a source bash file



    y = input(bcolors.FAIL + "Start Merlin now? [y/n]")
    if y == "y":
        out = input(bcolors.FAIL + "Do you want Debug output? [y/n]")
        if out == "n":
            basic_vars.append("OUTPUTDEV=/dev/null\n")
        with open("peer_vars.sh", "w+") as con:
            # con.write(f"ORDERERS=\"{os.environ['ORDERERS']}\"\n")
            # con.write(f"PEER_CON_PARAMS=\"{os.environ['PEER_CON_PARAMS']}\"\n")
            # con.write("CORE_PEER_LOCALMSPID=Org1MSP\n")
            # con.write("CORE_PEER_TLS_ENABLED=true\n")
            # con.write(f"CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org1.{args.domain}/peers/"
            #           f"peer0.org1.{args.domain}/tls/ca.crt\n")
            # con.write(f"CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org1.{args.domain}/users/"
            #           f"Admin@org1.{args.domain}/msp\n")
            # con.write(f"export CORE_PEER_ADDRESS=localhost:{config.peer_defport}\n")
            # con.write("BASEPATH=$PWD/crypto-config\n")
            # con.write("DOMAIN=dredev.de\n")
            # con.write(f"NO_PEERS={args.peers}\n")
            # con.write(f"NO_ORGANIZATIONS={args.orgs}\n")
            # con.write(f"DOMAIN={args.domain}\n")
            # con.write(f"CONSORTIUM_NAME={args.consortium}\n")
            # if kafka:
            #     os.environ["NO_KAFKA"] = str(args.kafka)
            # env_str += "export NO_KAFKA=" + str(args.kafka) + "\n"
            con.writelines(basic_vars)
            con.writelines(connection_params)
            co = ["changeOrg(){\n",
                  "  org=$2\n",
                  "  peer=$1\n",
                  "  export baseport=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))\n",
                  "  export CORE_PEER_LOCALMSPID=Org${org}MSP\n",
                  "  export CORE_PEER_TLS_ENABLED=true\n",
                  "  export CORE_PEER_TLS_ROOTCERT_FILE=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/peers/"
                  "peer0.org${org}.${DOMAIN}/tls/ca.crt\n",
                  "  export CORE_PEER_MSPCONFIGPATH=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/users/"
                  "Admin@org${org}.${DOMAIN}/msp\n",
                  "  export CORE_PEER_ADDRESS=localhost:${baseport}\n"
                  "}\n"]
            con.writelines(co)
        os.system("bash merlin.sh")
        print(bcolors.WARNING + "   [*] Starting credential creation..." + bcolors.ENDC)
        generate_node_json(_network_config=config,
                           _peers=args.peers,
                           _orgs=args.orgs,
                           _orderers=args.orderers,
                           _domain=args.domain,
                           _url="localhost")
        print(bcolors.HEADER + ">>> nodes.json has been created. Generating Wallets now")
        generate_wallets(_network_config=config,
                         _orgs=args.orgs,
                         _domain=args.domain)
        print(bcolors.OKGREEN + "   [+] Credential creation complete" + bcolors.ENDC)
    else:
        print(bcolors.HEADER + "Alright, Quitting")
