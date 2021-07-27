#!/bin/bash
export CHANNEL_ID=mychannel		# Channel name
export VERSION=1				# Version of the Smart Contract
export FABRIC_CFG_PATH=$PWD		# This is where the core.yaml is located
source peer_vars.sh
MAINPROFILE=MainChannel
ORDERERPROFILE=OrdererDefault
BASEPATH=$PWD/crypto-config
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


changeOrg(){
	org=$2
	peer=$1

	export baseport=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))
	export CORE_PEER_LOCALMSPID=Org${org}MSP
	export CORE_PEER_TLS_ENABLED=true
	export CORE_PEER_TLS_ROOTCERT_FILE=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/peers/peer${peer}.org${org}.${DOMAIN}/tls/ca.crt
	export CORE_PEER_MSPCONFIGPATH=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/users/Admin@org${org}.${DOMAIN}/msp
	export CORE_PEER_ADDRESS=peer${peer}.org${org}.${DOMAIN}:${baseport}
	#echo -e "${CYAN}>>> Changed Org: Org$org Peer$peer ${NOCOLOR}"
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
	if [ ${#ccodes[@]} -eq 0 ]; then
		echo -e "${LIGHTCYAN}	[i] No Chaincode to install, skipping"
	else
	# GO Chaincode, just package it
		echo -e "${ORANGE}[*] Start packaging... ${NOCOLOR}"

		for chaincode in "${ccodes[@]}"
		do
			echo -e "${ORANGE}	[*] Attempting packing of ${chaincode} Chaincode"

			peer lifecycle chaincode package ${chaincode}.tar.gz --path ${CC_SRC_PATH}/${chaincode} --lang golang --label ${chaincode}_${VERSION} > ${OUTPUTDEV}
			if [ $? -eq 1 ]; then
					echo -e "		${RED}[-] Packing of ${chaincode} Chaincode failed ${NOCOLOR}"
					return 1
			else
					echo -e "		${GREEN}[+] Packing of ${chaincode} Chaincode succeeded ${NOCOLOR}"
			fi
		done
		echo -e "${GREEN}[+] Packing complete! ${NOCOLOR}"
	fi
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
	if [ ${#ccodes[@]} -eq 0 ]; then
		echo -e "${LIGHTCYAN}	[i] No Chaincode to install, skipping"
	else
		echo -e "${PURPLE}\n>>> The Chaincodes is now being installed on each peer ${NOCOLOR}"
		echo -e "${ORANGE}[*] Start installing... \n${NOCOLOR}"
		for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
			for (( peer = 0; peer < $NO_PEERS; peer++ )); do
				changeOrg $peer $org
				echo -e "	${ORANGE}[*] Attempting install on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
				for chaincode in "${ccodes[@]}"
				do
					peer lifecycle chaincode install ${chaincode}.tar.gz > ${OUTPUTDEV}
					declare -i attempts=0
					while [ $? -eq 1 ] || [ $attempts -eq 5 ]; do
						peer lifecycle chaincode install ${chaincode}.tar.gz > ${OUTPUTDEV}
						echo -e "		${RED}[-] Install of ${chaincode} Chaincode on peer${peer}.org${org}.${DOMAIN} failed!${NOCOLOR} Again!"	
						attempts=$(( attempts + 1 ))						
					done
					if [ $? -eq 1 ]; then
						# Still failed
						echo -e "		${RED}[-] Install of ${chaincode} Chaincode on peer${peer}.org${org}.${DOMAIN} failed!${NOCOLOR} Finally, aborting!"	
						exit 1
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
	fi
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
	if [ ${#ccodes[@]} -eq 0 ]; then
		echo -e "${LIGHTCYAN}	[i] No Chaincode to install, skipping"
	else
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
	fi
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
	if [ ${#ccodes[@]} -eq 0 ]; then
		echo -e "${LIGHTCYAN}	[i] No Chaincode to install, skipping"
	else
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
	fi
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
	if [ ${#ccodes[@]} -eq 0 ]; then
		echo -e "${LIGHTCYAN}	[i] No Chaincode to install, skipping"
	else
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
	fi
}

writeScripts(){
	QUERYFILE=query
	PIQUERYFILE=query-pi
	INVOKEFILE=invoke
	PIINVOKEFILE=invoke-pi

	echo -e "${PURPLE}\n>>> I will create an invoke script for you! ${NOCOLOR}"
	if [ -f $INVOKEFILE ]; then
		rm $INVOKEFILE
	fi
	if [ -f $PIINVOKEFILE ]; then
		rm $PIINVOKEFILE
	fi
	echo -e "#!/bin/bash" >> $INVOKEFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $INVOKEFILE
	echo -e "	echo \"usage:  ./$INVOKEFILE <SmartContract> <Function> <args> \"" >> $INVOKEFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $INVOKEFILE
	echo -e "	echo \"Example: ./$INVOKEFILE fabric-authtoken createAuthToken [\\\"test\\\"] \"" >> $INVOKEFILE
	echo -e "	exit 1" >> $INVOKEFILE
	echo -e "fi" >> $INVOKEFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $INVOKEFILE
	echo -e "source peer_vars.sh" >> $INVOKEFILE
	echo -e "changeOrg 0 1" >> $INVOKEFILE
	echo -e "FUNCTION=\$2" >> $INVOKEFILE
	echo -e "SMARTCONTRACT=\$1" >> $INVOKEFILE
	echo -e "ARGS=\$3" >> $INVOKEFILE
	echo -e "echo -e \"Invoking \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $INVOKEFILE
	echo -e "peer chaincode invoke \$ORDERERS -C \$CHANNEL_ID -n \$SMARTCONTRACT \$PEER_CON_PARAMS -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $INVOKEFILE
	chmod +x $INVOKEFILE
	echo -e "${GREEN}[+] $INVOKEFILE created successfully"

	echo -e "#!/bin/bash" >> $PIINVOKEFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $PIINVOKEFILE
	echo -e "	echo \"usage:  ./$PIINVOKEFILE <SmartContract> <Function> <args> \"" >> $PIINVOKEFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $PIINVOKEFILE
	echo -e "	echo \"Example: ./$PIINVOKEFILE fabric-authtoken createAuthToken [\\\"test\\\"] \"" >> $PIINVOKEFILE
	echo -e "	exit 1" >> $PIINVOKEFILE
	echo -e "fi" >> $PIINVOKEFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $PIINVOKEFILE
	echo -e "source peer_vars.sh" >> $PIINVOKEFILE
	echo -e "changeOrg 1 1" >> $PIINVOKEFILE
	echo -e "FUNCTION=\$2" >> $PIINVOKEFILE
	echo -e "SMARTCONTRACT=\$1" >> $PIINVOKEFILE
	echo -e "ARGS=\$3" >> $PIINVOKEFILE
	echo -e "echo -e \"Invoking \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $PIINVOKEFILE
	echo -e "peer chaincode invoke \$ORDERERS -C \$CHANNEL_ID -n \$SMARTCONTRACT \$PEER_CON_PARAMS -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $PIINVOKEFILE
	chmod +x $PIINVOKEFILE
	echo -e "${GREEN}[+] $PIINVOKEFILE created successfully"


	echo -e "${PURPLE}\n>>> I will create a Query script for you! ${NOCOLOR}"
	if [ -f $QUERYFILE ]; then
		rm $QUERYFILE
	fi
	if [ -f $PIQUERYFILE ]; then
		rm $PIQUERYFILE
	fi
	echo -e "#!/bin/bash" >> $QUERYFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $QUERYFILE
	echo -e "	echo \"usage:  ./$QUERYFILE <SmartContract> <Function> <args> \"" >> $QUERYFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $QUERYFILE
	echo -e "	echo \"Example: ./$QUERYFILE fabric-authtoken readAuthToken [\\\"test\\\"] \"" >> $QUERYFILE
	echo -e "	exit 1" >> $QUERYFILE
	echo -e "fi" >> $QUERYFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $QUERYFILE
	echo -e "source peer_vars.sh" >> $QUERYFILE
	echo -e "changeOrg 0 1" >> $QUERYFILE
	echo -e "FUNCTION=\$2" >> $QUERYFILE
	echo -e "SMARTCONTRACT=\$1" >> $QUERYFILE
	echo -e "ARGS=\$3" >> $QUERYFILE
	echo -e "echo -e \"Querying \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $QUERYFILE
	echo -e "peer chaincode query -C \$CHANNEL_ID -n \$SMARTCONTRACT -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $QUERYFILE
	chmod +x $QUERYFILE

	echo -e "${GREEN}[+] $QUERYFILE created successfully"

	echo -e "#!/bin/bash" >> $PIQUERYFILE
	echo -e "if [ \$# -lt 3 ]; then" >> $PIQUERYFILE
	echo -e "	echo \"usage:  ./$PIQUERYFILE <SmartContract> <Function> <args> \"" >> $PIQUERYFILE
	echo -e "	echo \"Note that args need to be an array of strings, with ESCAPED quotes. \"" >> $PIQUERYFILE
	echo -e "	echo \"Example: ./$PIQUERYFILE fabric-authtoken readAuthToken [\\\"test\\\"] \"" >> $PIQUERYFILE
	echo -e "	exit 1" >> $PIQUERYFILE
	echo -e "fi" >> $PIQUERYFILE
	echo -e "CHANNEL_ID=$CHANNEL_ID" >> $PIQUERYFILE
	echo -e "source peer_vars.sh" >> $PIQUERYFILE
	echo -e "changeOrg 1 1" >> $PIQUERYFILE
	echo -e "FUNCTION=\$2" >> $PIQUERYFILE
	echo -e "SMARTCONTRACT=\$1" >> $PIQUERYFILE
	echo -e "ARGS=\$3" >> $PIQUERYFILE
	echo -e "echo -e \"Querying \$FUNCTION of \$SMARTCONTRACT on \$CHANNEL_ID with \$ARGS\"" >> $PIQUERYFILE
	echo -e "peer chaincode query -C \$CHANNEL_ID -n \$SMARTCONTRACT -c \"{\\\"function\\\": \\\"\$FUNCTION\\\", \\\"Args\\\": \$ARGS}\"" >> $PIQUERYFILE
	chmod +x $PIQUERYFILE

	echo -e "${GREEN}[+] $PIQUERYFILE created successfully"
}

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
echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
echo -e "${PURPLE}888 88e"
echo -e "${PURPLE}888 888b   e88 88e  888 8e   ,e e,"
echo -e "${PURPLE}888 8888D d888 888b 888 88b d88 88b"
echo -e "${PURPLE}888 888P  Y888 888P 888 888 888   ,"
echo -e "${PURPLE}888 88\"    \"88 88\"  888 888  \"YeeP\""
echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
