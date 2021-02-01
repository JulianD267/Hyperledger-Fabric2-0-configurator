#!/bin/bash
export CHANNEL_ID=mychannel		# Channel name
export VERSION=1				# Version of the Smart Contract
export FABRIC_CFG_PATH=$PWD		# This is where the core.yaml is located

MAINPROFILE=MainChannel
ORDERERPROFILE=OrdererDefault
BASEPATH=$PWD/crypto-config
CHAINCODES=("fabric-orionACL" "fabric-authtoken" "fabric-transaction-log")
CC_SRC_PATH=./chaincodes/java
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
		configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID mychannel > ${OUTPUTDEV}
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

joinChannel(){
		echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
        echo -e "${PURPLE}  e88'Y88 888                                     888       888           ,e,"
        echo -e "${PURPLE} d888  'Y 888 ee   ,\"Y88b 888 8e  888 8e   ,e e,  888       888  e88 88e   \"  888 8e"
        echo -e "${PURPLE}C8888     888 88b \"8\" 888 888 88b 888 88b d88 88b 888       888 d888 888b 888 888 88b"
        echo -e "${PURPLE} Y888  ,d 888 888 ,ee 888 888 888 888 888 888   , 888    e  88P Y888 888P 888 888 888"
        echo -e "${PURPLE}  \"88,d88 888 888 \"88 888 888 888 888 888  \"YeeP\" 888   \"8\",P'   \"88 88\"  888 888 888"
		echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	 	echo -e "${PURPLE}>>> Joining Channel ${CHANNEL_ID} on each Peer ${NOCOLOR}"
		echo -e "${ORANGE}[*] Start Joining of Channel ${CHANNEL_ID} ${NOCOLOR}"
		for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
			for (( peer = 0; peer < $NO_PEERS; peer++ )); do
					changeOrg $peer $org
					echo -e "		${ORANGE}[*] Attempting Channel join for peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
					peer channel join --tls ${CORE_PEER_TLS_ENABLED} -b ${CHANNEL_ID}.block > ${OUTPUTDEV}
					if [ $? -eq 1 ]; then
							echo -e "		${RED}[-] Channel join failed on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
							return 1
					else
							echo -e "		${GREEN}[+] Channel join succeeded on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
					fi
			done
		done
		echo -e "${GREEN}[+] Joining succeeded ${NOCOLOR}"
		return 0
}

updateAnchors(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
    echo -e "${PURPLE}    e Y8b                      888                        8888 8888               888           d8"
    echo -e "${PURPLE}   d8b Y8b    888 8e   e88'888 888 ee   e88 88e  888,8,   8888 8888 888 88e   e88 888  ,\"Y88b  d88    ,e e,"
    echo -e "${PURPLE}  d888b Y8b   888 88b d888  '8 888 88b d888 888b 888 \"    8888 8888 888 888b d888 888 \"8\" 888 d88888 d88 88b"
    echo -e "${PURPLE} d888888888b  888 888 Y888   , 888 888 Y888 888P 888      8888 8888 888 888P Y888 888 ,ee 888  888   888   , "
    echo -e "${PURPLE}d8888888b Y8b 888 888  \"88,e8' 888 888  \"88 88\"  888      'Y88 88P' 888 88\"   \"88 888 \"88 888  888    \"YeeP\" "
    echo -e "${PURPLE}                                                                    888                                      "
    echo -e "${PURPLE}                                                                    888                                     "
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<\n"
	echo -e "${PURPLE}>>> Now we need to update the Anchor peers, to tell them, that they are important for us,\n since they serve as the gateway peers for all the others. ${NOCOLOR}"
	for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
		echo -e "		${ORANGE}[*] Attempting Anchor Update for peer0.org${org}.${DOMAIN} ${NOCOLOR}"
		changeOrg 0 ${org}		# Default Peer0 is always the Anchor
		echo -e "$CORE_PEER_LOCALMSPID $CORE_PEER_MSPCONFIGPATH $CORE_PEER_ADDRESS"
		peer channel update ${ORDERERS} -c ${CHANNEL_ID} -f ./config/Org${org}MSPanchors.tx > ${OUTPUTDEV}
		if [ $? -eq 1 ]; then
				echo -e "		${RED}[-] Anchor Update failed on peer0.org${org}.${DOMAIN} ${NOCOLOR}"
				return 1
		else
				echo -e "		${GREEN}[+] Anchor Update succeeded on peer0.org${org}.${DOMAIN} ${NOCOLOR}"
		fi
	done
	return 0
}

packCC(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
    echo -e "${PURPLE}888 88e                   888        e88'Y88   e88'Y88"
    echo -e "${PURPLE}888 888D  ,\"Y88b  e88'888 888 ee    d888  'Y  d888  'Y"
    echo -e "${PURPLE}888 88\"  \"8\" 888 d888  '8 888 P    C8888     C8888"
    echo -e "${PURPLE}888      ,ee 888 Y888   , 888 b     Y888  ,d  Y888  ,d"
    echo -e "${PURPLE}888      \"88 888  \"88,e8' 888 8b     \"88,d88   \"88,d88"
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	echo -e "${PURPLE}>>> The Chaincodes now get packaged. This is done with the new lifecycle management. ${NOCOLOR}"
	echo -e "${ORANGE}[*] Start building using gradle"
	# Read the contents into the array
	# IFS=$'\n' read -d '' -r -a ccodes < chaincodes.txt

  for chaincode in "${ccodes[@]}"
	do
		echo -e "${ORANGE}	[*] Build ${chaincode} "
		pushd ${CC_SRC_PATH}/${chaincode}/
		./gradlew clean build shadowJar
		if [ $? -eq 1 ]; then
				echo -e "		${RED}[-] Gradle failed. Wrong Version? Trying with installDist ${NOCOLOR}"
				./gradlew clean build installDist		
				if [ $? -eq 1 ]; then
					echo -e "		${RED}[-] Gradle still failed ${NOCOLOR}"
					exit 1
				else
					echo -e "		${GREEN}[+] Gradle succeeded now ${NOCOLOR}"			
					
				fi
		fi
		popd
		echo $PWD
		echo -e "${GREEN}      [+] Build ${chaincode} finished"
	done
	echo -e "${GREEN}[+] Build finished \n"
	echo -e "${ORANGE}[*] Start packaging... ${NOCOLOR}"

	for chaincode in "${ccodes[@]}"
	do
		echo -e "${ORANGE}	[*] Attempting packing of ${chaincode} Chaincode"

		peer lifecycle chaincode package ${chaincode}.tar.gz --path ${CC_SRC_PATH}/${chaincode}/build/libs --lang java --label ${chaincode}_${VERSION} > ${OUTPUTDEV}
		if [ $? -eq 1 ]; then
				echo -e "		${RED}[-] Packing of ${chaincode} Chaincode failed ${NOCOLOR}"
				return 1
		else
				echo -e "		${GREEN}[+] Packing of ${chaincode} Chaincode succeeded ${NOCOLOR}"
		fi
	done
	echo -e "${GREEN}[+] Packing complete! ${NOCOLOR}"
	return 0
}

installCC(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
	echo -e "${PURPLE}888                 d8           888 888     e88'Y88   e88'Y88"
    echo -e "${PURPLE}888 888 8e   dP\"Y  d88    ,\"Y88b 888 888    d888  'Y  d888  'Y"
    echo -e "${PURPLE}888 888 88b C88b  d88888 \"8\" 888 888 888   C8888     C8888"
    echo -e "${PURPLE}888 888 888  Y88D  888   ,ee 888 888 888    Y888  ,d  Y888  ,d"
    echo -e "${PURPLE}888 888 888 d,dP   888   \"88 888 888 888     \"88,d88   \"88,d88"
    echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	echo -e "${PURPLE}\n>>> The Chaincodes is now being installed on each peer ${NOCOLOR}"
	echo -e "${ORANGE}[*] Start installing... \n${NOCOLOR}"
	for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
		for (( peer = 0; peer < $NO_PEERS; peer++ )); do
			changeOrg $peer $org
			echo -e "	${ORANGE}[*] Attempting install on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
			for chaincode in "${ccodes[@]}"
			do
				peer lifecycle chaincode install ${chaincode}.tar.gz > ${OUTPUTDEV}
				if [ $? -eq 1 ]; then
						echo -e "		${RED}[-] Install of ${chaincode} Chaincode on peer${peer}.org${org}.${DOMAIN} failed!${NOCOLOR}"
						return 1
				fi
			done
			echo -e "${GREEN}	[+] Install on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR} finished \n"
		done
	done
	echo -e "${GREEN}[+] Installing finished ${NOCOLOR}"
	echo -e "${PURPLE}>>> Alright everything seems to be installed, lets verify! ${NOCOLOR}"
	changeOrg 0 1				# peer0.org1.domain
	peer lifecycle chaincode queryinstalled >&log.txt
	if [ $? -eq 1 ]; then
			echo -e "		${RED}[-] Query of Chaincode on peer0.org1.${DOMAIN} failed!${NOCOLOR}"
			return 1
	fi
	cat log.txt
	echo -e "${PURPLE}>>> Package Identifiers: ${NOCOLOR}"
	for chaincode in "${ccodes[@]}"
	do
	    tmp=$(sed -n "/${chaincode}_1/{s/^Package ID: //; s/, Label:.*$//; p;}" log.txt)
		echo -e "${LIGHTBLUE}>>> [>] ${chaincode}: ${tmp}  ${NOCOLOR}"	# indirect, allows to treat CID as a var name
	done
	return 0
}

approveCC(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
    echo -e "${PURPLE}    e Y8b                                                              e88'Y88   e88'Y88"
    echo -e "${PURPLE}   d8b Y8b    888 88e  888 88e  888,8,  e88 88e  Y8b Y888P  ,e e,     d888  'Y  d888  'Y "
    echo -e "${PURPLE}  d888b Y8b   888 888b 888 888b 888 \"  d888 888b  Y8b Y8P  d88 88b   C8888     C8888     "
    echo -e "${PURPLE} d888888888b  888 888P 888 888P 888    Y888 888P   Y8b \"   888   ,    Y888  ,d  Y888  ,d "
    echo -e "${PURPLE}d8888888b Y8b 888 88\"  888 88\"  888     \"88 88\"     Y8P     \"YeeP\"     \"88,d88   \"88,d88 "
    echo -e "${PURPLE}              888      888                                                               "
    echo -e "${PURPLE}              888      888                                                               "
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	echo -e "${PURPLE}>>> Now the installed Chaincodes need to be approved by the Orderers and the Organizations! ${NOCOLOR}"
	echo -e "${ORANGE}[*] Start approving... ${NOCOLOR}"
	for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
		changeOrg 0 $org
		for chaincode in "${ccodes[@]}"
		do
			CID=${chaincode}_ID
			changeOrg 0 $org
			echo -e "${ORANGE}		[*] Org${org} is approving ... ${NOCOLOR}"
			peer lifecycle chaincode approveformyorg ${ORDERERS} --channelID ${CHANNEL_ID} --name $chaincode --version ${VERSION} --package-id $(sed -n "/${chaincode}_1/{s/^Package ID: //; s/, Label:.*$//; p;}" log.txt) --sequence ${VERSION} --waitForEvent > ${OUTPUTDEV}
			if [ $? -eq 1 ]; then
					echo -e "		${RED}	[-] Org${org} did not approve ${chaincode} Chaincode! ${NOCOLOR}"
					return 1
			fi
		done
	done
	echo -e "${GREEN}[+] Approving complete. ${NOCOLOR}"
	return 0
}

checkCommitReadiness(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
    echo -e "${PURPLE}  e88'Y88 888                      888        e88'Y88                                   ,e,   d8"
    echo -e "${PURPLE} d888  'Y 888 ee   ,e e,   e88'888 888 ee    d888  'Y  e88 88e  888 888 8e  888 888 8e   \"   d88   "
    echo -e "${PURPLE}C8888     888 88b d88 88b d888  '8 888 P    C8888     d888 888b 888 888 88b 888 888 88b 888 d88888"
    echo -e "${PURPLE} Y888  ,d 888 888 888   , Y888   , 888 b     Y888  ,d Y888 888P 888 888 888 888 888 888 888  888 "
    echo -e "${PURPLE}  \"88,d88 888 888  \"YeeP\"  \"88,e8' 888 8b     \"88,d88  \"88 88\"  888 888 888 888 888 888 888  888"
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	echo -e "${PURPLE}>>> Now that the chaincodes are approved by each organization, they need to be committed. First lets check for the commit readiness! ${NOCOLOR}"
	changeOrg 0 1			#peer0.org1
	for chaincode in "${ccodes[@]}"
	do
		echo -e "${ORANGE}		[*] Checking commit readiness for ${chaincode}... ${NOCOLOR}"
		peer lifecycle chaincode checkcommitreadiness --channelID ${CHANNEL_ID} --name ${chaincode} --version ${VERSION} --sequence ${VERSION} --output json > ${OUTPUTDEV}
		if [ $? -eq 1 ]; then
				echo -e "		${RED}	[-] ${chaincode} not ready to be committed! ${NOCOLOR}"
				return 1
		fi
	done
	echo -e "${PURPLE}>>> JSON with true everywhere? "
	return 0

}

commitCC(){
	echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
    echo -e "${PURPLE}  e88'Y88                                   ,e,   d8       e88'Y88   e88'Y88"
    echo -e "${PURPLE} d888  'Y  e88 88e  888 888 8e  888 888 8e   \"   d88      d888  'Y  d888  'Y "
    echo -e "${PURPLE}C8888     d888 888b 888 888 88b 888 888 88b 888 d88888   C8888     C8888     "
    echo -e "${PURPLE} Y888  ,d Y888 888P 888 888 888 888 888 888 888  888      Y888  ,d  Y888  ,d "
    echo -e "${PURPLE}  \"88,d88  \"88 88\"  888 888 888 888 888 888 888  888       \"88,d88   \"88,d88"
	echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<\n"
	echo -e "${PURPLE}>>> Alright, final step now. Lets commit all of the Chaincodes! ${NOCOLOR}"
	changeOrg 0 1 		# peer0.org1
	echo -e "${ORANGE}	[*] Start committing... ${NOCOLOR}"
	for chaincode in "${ccodes[@]}"
	do
		echo -e "${ORANGE}		[*] Commit ${chaincode}... ${NOCOLOR}"
		peer lifecycle chaincode commit ${ORDERERS} --channelID ${CHANNEL_ID} --name ${chaincode} $PEER_CON_PARAMS --version ${VERSION} --sequence ${VERSION} > ${OUTPUTDEV}
		if [ $? -eq 1 ]; then
				echo -e "		${RED}	[-] ${chaincode} could not be committed! ${NOCOLOR}"
				return 1
		fi
	done


	echo -e "${GREEN}	[+] Committing complete! ${NOCOLOR}"

	echo -e "${PURPLE}>>> Everything seems to be installed, lets see"

	echo -e "\n${LIGHTCYAN} =<=<=<=<=<=<=<=<=<=<=<=<=<=<= Chaincodes <=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	for chaincode in "${ccodes[@]}"
	do
		peer lifecycle chaincode querycommitted --channelID ${CHANNEL_ID} --name ${chaincode} > ${OUTPUTDEV}
	done
	echo -e "\n${LIGHTCYAN} =<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="

}

writeScripts(){
	QUERYFILE=query
	INVOKEFILE=invoke

	echo -e "${PURPLE}\n>>> I will create an invoke script for you! ${NOCOLOR}"
	if [ -f $INVOKEFILE ]; then
		rm $INVOKEFILE
	fi
	echo -e "#!/bin/bash" >> $INVOKEFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $INVOKEFILE
	echo -e "	echo \"usage:  ./$INVOKEFILE <SmartContract> <Function> <args> \"" >> $INVOKEFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $INVOKEFILE
	echo -e "	echo \"Example: ./$INVOKEFILE fabric-authtoken createAuthToken [\\\"test\\\"] \"" >> $INVOKEFILE
	echo -e "	exit 1" >> $INVOKEFILE
	echo -e "fi" >> $INVOKEFILE
	echo -e "ORDERERS=\"$ORDERERS\"" >> $INVOKEFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $INVOKEFILE
	echo -e "export CORE_PEER_LOCALMSPID=$CORE_PEER_LOCALMSPID" >> $INVOKEFILE
	echo -e "export CORE_PEER_MSPCONFIGPATH=$CORE_PEER_MSPCONFIGPATH" >> $INVOKEFILE
	echo -e "export CORE_PEER_ADDRESS=$CORE_PEER_ADDRESS" >> $INVOKEFILE
	echo -e "PEER_CON_PARAMS=\"$PEER_CON_PARAMS\"" >> $INVOKEFILE
	echo -e "FUNCTION=\$2" >> $INVOKEFILE
	echo -e "SMARTCONTRACT=\$1" >> $INVOKEFILE
	echo -e "ARGS=\$3" >> $INVOKEFILE
	echo -e "echo -e \"Invoking \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $INVOKEFILE
	echo -e "peer chaincode invoke \$ORDERERS -C \$CHANNEL_ID -n \$SMARTCONTRACT \$PEER_CON_PARAMS -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $INVOKEFILE
	chmod +x $INVOKEFILE
	echo -e "${GREEN}[+] $INVOKEFILE created successfully"

	echo -e "${PURPLE}\n>>> I will create a Query script for you! ${NOCOLOR}"
	if [ -f $QUERYFILE ]; then
		rm $QUERYFILE
	fi
	echo -e "#!/bin/bash" >> $QUERYFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $QUERYFILE
	echo -e "	echo \"usage:  ./$QUERYFILE <SmartContract> <Function> <args> \"" >> $QUERYFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $QUERYFILE
	echo -e "	echo \"Example: ./$QUERYFILE fabric-authtoken readAuthToken [\\\"test\\\"] \"" >> $QUERYFILE
	echo -e "	exit 1" >> $QUERYFILE
	echo -e "fi" >> $QUERYFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $QUERYFILE
	echo -e "export CORE_PEER_LOCALMSPID=$CORE_PEER_LOCALMSPID" >> $QUERYFILE
	echo -e "export CORE_PEER_MSPCONFIGPATH=$CORE_PEER_MSPCONFIGPATH" >> $QUERYFILE
	echo -e "export CORE_PEER_ADDRESS=$CORE_PEER_ADDRESS" >> $QUERYFILE
	echo -e "FUNCTION=\$2" >> $QUERYFILE
	echo -e "SMARTCONTRACT=\$1" >> $QUERYFILE
	echo -e "ARGS=\$3" >> $QUERYFILE
	echo -e "echo -e \"Querying \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $QUERYFILE
	echo -e "peer chaincode query -C \$CHANNEL_ID -n \$SMARTCONTRACT -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $QUERYFILE
	chmod +x $QUERYFILE

	echo -e "${GREEN}[+] $QUERYFILE created successfully"
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

# The Channel Join
# Merlin will then automatically join the newly created channel on each peer within the network!
joinChannel
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Update of the Anchor peers
# After each peer had joined the channel, the corresponding anchor peers need to be updated as well.
# Those are important for the communication across organizations.
updateAnchors
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Packing of the Chaincode
# After the Channel is setup, the Chaincode can be packaged. This involves a compilation step
# in conjunction with the new lifecycle package method.
packCC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Install of the Chaincode
# After the Chaincode has been packaged, it can be installed onto each Client by Merlin.
# This is done with the new lifecycle install method
installCC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Approval of the Chaincode
# Each organization need to approve the previously installed chaincode with its attributes!
# Merlin issues requests to each Organization
approveCC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Pre-Commit Step
# Merlin will check if each Organization is ready to commit the Chaincode onto the ledger
checkCommitReadiness
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The final Commit
# The Chaincode gets committed onto the ledger! Now everything should be good to go.
commitCC
if [ $? -eq 1 ]; then
		return 1
fi

# Easy interaction
# For the invoke/Query of the ledger, the commands need certain parameters which depend
# on the network configuration and are quite hideous to work with. Thus Merlin creates two
# simple scripts which include all the necessary environment variables.
writeScripts

echo -e "${GREEN}\n>>> ALL DONE !!! Happy interacting"
# echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
# echo -e "${PURPLE}.___________. _______     _______.___________."
# echo -e "${PURPLE}|           ||   ____|   /       |           |"
# echo -e "${PURPLE}\`---|  |----\`|  |__     |   (----\`---|  |----\`"
# echo -e "${PURPLE}    |  |     |   __|     \   \       |  |     "
# echo -e "${PURPLE}    |  |     |  |____.----)   |      |  |     "
# echo -e "${PURPLE}    |__|     |_______|_______/       |__|     "
# echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<\n"
# echo -e "${PURPLE}>>> Lets test the invoke of AuthToken!\n"
# peer chaincode invoke $ORDERERS -C $CHANNEL_ID -n fabric-authtoken $PEER_CON_PARAMS -c '{"function": "createAuthToken", "Args":["test"]}'
#
# echo -e "${PURPLE}>>> Lets test the invoke of Default!\n"
# peer chaincode invoke $ORDERERS -C $CHANNEL_ID -n fabric-default $PEER_CON_PARAMS -c '{"function": "createDefaultAsset", "Args":["test"]}'
#
# echo -e "${PURPLE}\n>>> Lets test the query of AuthToken in 4s! ${NOCOLOR}"
# sleep 4
#
# peer chaincode query -C $CHANNEL_ID -n fabric-authtoken -c '{"function":"readAuthToken", "Args":["test"]}'
# echo -e "${PURPLE}\n>>> Lets test the query of Default! ${NOCOLOR}"
# peer chaincode query -C $CHANNEL_ID -n fabric-default -c '{"function":"readDefaultAsset", "Args":["test"]}'

#testRoutine 50
echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
echo -e "${PURPLE}888 88e"
echo -e "${PURPLE}888 888b   e88 88e  888 8e   ,e e,"
echo -e "${PURPLE}888 8888D d888 888b 888 88b d88 88b"
echo -e "${PURPLE}888 888P  Y888 888P 888 888 888   ,"
echo -e "${PURPLE}888 88\"    \"88 88\"  888 888  \"YeeP\""
#echo -e "${PURPLE} _______   ______   .__   __.  _______  __  "
#echo -e "${PURPLE}|       \\ /  __  \\  |  \\ |  | |   ____||  | "
#echo -e "${PURPLE}|  .--.  |  |  |  | |   \\|  | |  |__   |  | "
#echo -e "${PURPLE}|  |  |  |  |  |  | |  . \`  | |   __|  |  | "
#echo -e "${PURPLE}|  '--'  |  \`--'  | |  |\\   | |  |____ |__| "
#echo -e "${PURPLE}|_______/ \\______/  |__| \\__| |_______|(__) "
echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"

