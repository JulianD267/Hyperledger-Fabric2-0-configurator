#!/bin/bash
export CHANNEL_ID=mychannel		# Channel name
export VERSION=1				# Version of the Smart Contract
export FABRIC_CFG_PATH=$PWD		# This is where the core.yaml is located
source peer_vars.sh
MAINPROFILE=MainChannel
ORDERERPROFILE=OrdererDefault
BASEPATH=$PWD/crypto-config
CHAINCODES=("fabric-orionACL" "fabric-authtoken" "fabric-transaction-log")
CC_SRC_PATH=./chaincodes/go
SLEEPINTERVAL=1
LINE="=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
NOCOLOR='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
ORANGE='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[1;35m'
CYAN='\033[0;36m'
LIGHTGRAY='\033[0;37m'
DARKGRAY='\033[1;30m'
LIGHTRED='\033[1;31m'
LIGHTGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LIGHTBLUE='\033[1;34m'
LIGHTPURPLE='\033[1;35m'
LIGHTCYAN='\033[1;36m'
WHITE='\033[1;37m'
IFS=$'\n' read -d '' -r -a ccodes < chaincodes.txt

if [[ -z ${OUTPUTDEV} ]]; then
	OUTPUTDEV=/dev/stdout
fi

generateCryptoStuff(){
		echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
		echo -e "${PURPLE}  e88'Y88                             d8                                    "
		echo -e "${PURPLE} d888  'Y 888,8, Y8b Y888P 888 88e   d88    e88 88e   e88 888  ,e e,  888 8e  "
		echo -e "${PURPLE}C8888     888 \"   Y8b Y8P  888 888b d88888 d888 888b d888 888 d88 88b 888 88b "
		echo -e "${PURPLE} Y888  ,d 888      Y8b Y   888 888P  888   Y888 888P Y888 888 888   , 888 888 "
		echo -e "${PURPLE}  \"88,d88 888       888    888 88\"   888    \"88 88\"   \"88 888  \"YeeP\" 888 888 "
		echo -e "${PURPLE}                    888    888                         ,  88P          "
		echo -e "${PURPLE}                    888    888                        \"8\",P\"                  "
		echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	 	echo -e "${PURPLE}>>> Generating Crypto Material ${NOCOLOR}"
		cryptogen generate --config=./crypto-config.yaml
		echo -e "${ORANGE}[*] Generating channel.tx, genesis.block, anchor peers ${NOCOLOR}"
		configtxgen -profile $ORDERERPROFILE -outputBlock ./config/genesis.block -channelID ordererchannel > ${OUTPUTDEV}
		if [ -f ./config/genesis.block ]; then
				echo -e "		${GREEN}[+] genesis.block created ${NOCOLOR}"
		else
				echo -e "		${RED}[-] genesis.block not created ${NOCOLOR}"
				return 1
		fi
		configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID ${CHANNEL_ID} > ${OUTPUTDEV}
		if [ -f ./config/channel.tx ]; then
				echo -e "		${GREEN}[+] channel.tx created ${NOCOLOR}"
		else
				echo -e "		${RED}[-] channel.tx not created ${NOCOLOR}"
				return 1
		fi
		for (( i = 1; i <= $NO_ORGANIZATIONS; i++ )); do
			configtxgen -profile $MAINPROFILE -outputAnchorPeersUpdate ./config/Org${i}MSPanchors.tx -channelID ${CHANNEL_ID} -asOrg Org${i}MSP > ${OUTPUTDEV}
			if [ -f ./config/Org${i}MSPanchors.tx ]; then
					echo -e "		${GREEN}[+] anchor peers for Org${i}MSP created ${NOCOLOR}"
			else
					echo -e "		${RED}[-] anchor peers not created ${NOCOLOR}"
					return 1
			fi
		done
		echo -e "${GREEN}[+] Generating channel.tx, genesis.block, anchor peers ${NOCOLOR}"
		return 0
}

changeOrg(){
	org=$2
	peer=$1

	export baseport=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))
	export CORE_PEER_LOCALMSPID=Org${org}MSP
	export CORE_PEER_TLS_ENABLED=true
	export CORE_PEER_TLS_ROOTCERT_FILE=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/peers/peer0.org${org}.${DOMAIN}/tls/ca.crt
	export CORE_PEER_MSPCONFIGPATH=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/users/Admin@org${org}.${DOMAIN}/msp
	export CORE_PEER_ADDRESS=localhost:${baseport}
	#echo -e "${CYAN}>>> Changed Org: Org$org Peer$peer ${NOCOLOR}"
}

startDocker(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
    echo -e "${PURPLE}888 88e                      888     "
    echo -e "${PURPLE}888 888b   e88 88e   e88'888 888 ee  ,e e,  888,8, "
    echo -e "${PURPLE}888 8888D d888 888b d888  '8 888 P  d88 88b 888 \""
    echo -e "${PURPLE}888 888P  Y888 888P Y888   , 888 b  888   , 888    "
    echo -e "${PURPLE}888 88\"    \"88 88\"   \"88,e8' 888 8b  \"YeeP\" 888 "
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<\n"
	echo -e "${PURPLE}>>> I will now start all the containers! Docker do your thing!${NOCOLOR}"
	docker-compose up -d
	echo -e "${PURPLE}>>> Now please give the containers a short amount of time to start. Some Seconds should be enough"
}

createChannel(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
    echo -e "${PURPLE}  e88'Y88                          d8               e88'Y88 888                                     888"
    echo -e "${PURPLE} d888  'Y 888,8,  ,e e,   ,\"Y88b  d88    ,e e,     d888  'Y 888 ee   ,\"Y88b 888 8e  888 8e   ,e e,  888"
    echo -e "${PURPLE}C8888     888 \"  d88 88b \"8\" 888 d88888 d88 88b   C8888     888 88b \"8\" 888 888 88b 888 88b d88 88b 888"
    echo -e "${PURPLE} Y888  ,d 888    888   , ,ee 888  888   888   ,    Y888  ,d 888 888 ,ee 888 888 888 888 888 888   , 888"
    echo -e "${PURPLE}  \"88,d88 888     \"YeeP\" \"88 888  888    \"YeeP\"     \"88,d88 888 888 \"88 888 888 888 888 888  \"YeeP\" 888"
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	changeOrg 0 1
	if [ ! -f ./config/channel.tx ]; then
			echo -e "${RED}>>> HEY! channel.tx is missing! Generate it first. Aborting"
			return 1
	fi
	set -x
	peer channel create ${ORDERERS} -c ${CHANNEL_ID} -f ./config/channel.tx > ${OUTPUTDEV}
	set +x
	if [ $? -eq 1 ]; then
			echo -e "${PURPLE}>>> Ok second try ${NOCOLOR}"
			sleep $SLEEPINTERVAL
			peer channel create ${ORDERERS} -c ${CHANNEL_ID} -f ./config/channel.tx > ${OUTPUTDEV}
	fi
	echo -e "${PURPLE}>>> Is the block there?"
	if [ $(ls | grep ${CHANNEL_ID}.block) == "${CHANNEL_ID}.block" ]; then
		echo -e "${GREEN}[+] Yes it is, ${CHANNEL_ID}.block"
	else
		echo -e "${RED}[-] No, something went wrong, aborting"
	fi
}

start(){
	echo -e "Printing to $OUTPUTDEV"
	echo -e "${YELLOW}${LINE}"
	echo -e "=>	.___  ___.  _______ .______       __       __  .__   __.	<="
	echo -e "=>	|   \/   | |   ____||   _  \     |  |     |  | |  \ |  |	<="
	echo -e "=>	|  \  /  | |  |__   |  |_)  |    |  |     |  | |   \|  |	<= "
	echo -e "=>	|  |\/|  | |   __|  |      /     |  |     |  | |  .    |	<= "
	echo -e "=>	|  |  |  | |  |____ |  |\  \----.|  \`----.|  | |  |\   |	<= "
	echo -e "=>	|__|  |__| |_______|| _| \______||_______||__| |__| \__|	<= "
	echo -e "${LINE}\n"
	echo -e ">>> This is Merlin, the automated Fabric Test Network Production service. I hope you already generated the necessary yaml files!"
	echo -e "\n>>> First let me see if all the necessary programs are installed in your PATH"
	which configtxgen
	if [ "$?" -eq 0 ]
	then
			echo -e "${GREEN}[+] Configtxgen installed!"
	else
			echo -e "${RED}[-] Configtxgen not installed!"
			return 1
	fi

	which peer
	if [ "$?" -ne 0 ]; then
		echo -e "${RED}[-] peer not installed!"
		return 1
	else
		echo -e "${GREEN}[+] peer installed!"
	fi

	which cryptogen &> /dev/null
	if [ "$?" -ne 0 ]; then
		echo -e "${RED}[-] cryptogen not installed!"
		return 1
	else
		echo -e "${GREEN}[+] cryptogen installed!"
	fi

	which docker-compose &> /dev/null
	if [ "$?" -ne 0 ]; then
		echo -e "${RED}[-] docker-compose not installed!"
		return 1
	else
		echo -e "${GREEN}[+] docker-compose installed!"
	fi

	which ls &> /dev/null
	if [ "$?" -ne 0 ]; then
		echo -e "${RED}[-] ls not installed!"
		return 1
	else
		echo -e "${GREEN}[+] ls installed!"
	fi

	which grep &> /dev/null
	if [ "$?" -ne 0 ]; then
		echo -e "${RED}[-] grep not installed!"
		return 1
	else
		echo -e "${GREEN}[+] grep installed!"
	fi
	echo -e "${GREEN}>>> Great! Every needed tool is installed! \n"
	echo -e "${PURPLE}>>> Check the files!"
	if [ ! -f core.yaml ]; then
			echo -e "${RED}>>> core.yaml missing - aborting"
			return 1
	elif [ ! -f crypto-config.yaml ]; then
			echo -e "${RED}>>> crypto-config.yaml missing - aborting"
			return 1
	elif [ ! -f configtx.yaml ]; then
			echo -e "${RED}>>> configtx.yaml missing - aborting"
			return 1
	elif [ ! -f docker-compose.yaml ]; then
			echo -e "${RED}>>> docker-compose.yaml missing - aborting"
			return 1
	elif [ ! -f .env ]; then
			echo -e "${RED}>>> .env missing - aborting"
			return 1
	else
			echo -e "${GREEN}>>> Alright everything is fine! I will now clean the unnecessary old files"
			rm -rf config crypto-config fabric-* log.txt
			echo -e "${PURPLE}>>> Should be fine now, here we go!"
			return 0
	fi
}


# The startup routine.
# Merlin is initialized and checks all of the necessary tools like configtxgen. It will SampleConsortium
# Clean up all old waste, which would later be overwritten. So be sure to backup anything you want to safe!
start
if [ $? -eq 1 ]; then
		return 1
fi

# The Crypto Generation
# Merlin will create all the necessary certificates and credentials for the different nodes of the network
generateCryptoStuff
if [ $? -eq 1 ]; then
		return 1
fi

# The Docker Start
# Merlin will automatically create all of the defined Docker Containers within the docker-compose.yaml file.
# The Containers need some time to start, so be sure to give some seconds of sleep until you continue!
startDocker
sleep 15

# The Channel Creation
# Merlin will now create a new Channel called $CHANNEL_ID. This depends on the Crypto Cerficates from
# the Crypto Generation step!
createChannel
sleep $SLEEPINTERVAL


echo -e "${GREEN}\n>>> Done for now"
echo -e "${RED}\n>>> STOPPING PEER1 and COUCHDB1"
docker stop couchdb1.org1.dredev.de
docker stop peer1.org1.dredev.de

