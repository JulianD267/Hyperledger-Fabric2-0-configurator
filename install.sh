#!/bin/bash
export CHANNEL_ID=mychannel		# Channel name
export VERSION=1				# Version of the Smart Contract
export FABRIC_CFG_PATH=$PWD		# This is where the core.yaml is located
OUTPUTDEV=/dev/null
MAINPROFILE=MainChannel
ORDERERPROFILE=OrdererDefault
BASEPATH=$PWD/crypto-config
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
source peer_vars.sh
changeOrg(){
	org=$2
	peer=$1

	export baseport=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))
	export CORE_PEER_LOCALMSPID=Org${org}MSP
	export CORE_PEER_TLS_ENABLED=true
	export CORE_PEER_TLS_ROOTCERT_FILE=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/peers/peer0.org${org}.${DOMAIN}/tls/ca.crt
	export CORE_PEER_MSPCONFIGPATH=$BASEPATH/peerOrganizations/org${org}.${DOMAIN}/users/Admin@org${org}.${DOMAIN}/msp
	export CORE_PEER_ADDRESS=localhost:${baseport}
}

packCC(){
	echo -e "${PURPLE}[*] Building"
  chaincode=$1
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
	echo -e "${GREEN}[+] Build finished \n"
	echo -e "${ORANGE}[*] Start packaging... ${NOCOLOR}"
	peer lifecycle chaincode package ${chaincode}.tar.gz --path ${CC_SRC_PATH}/${chaincode}/build/libs --lang java --label ${chaincode}_${VERSION} > ${OUTPUTDEV}
	if [ $? -eq 1 ]; then
			echo -e "		${RED}[-] Packing of ${chaincode} Chaincode failed ${NOCOLOR}"
			return 1
	fi
	echo -e "${GREEN}[+] Packing complete! ${NOCOLOR}"
	return 0
}

installCC(){
	echo -e "${PURPLE}[*] Installing... \n${NOCOLOR}"
  chaincode=$1
	for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
		for (( peer = 0; peer < $NO_PEERS; peer++ )); do
			changeOrg $peer $org
			echo -e "	${ORANGE}[*] Attempting install on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR}"
			peer lifecycle chaincode install ${chaincode}.tar.gz > ${OUTPUTDEV}
			if [ $? -eq 1 ]; then
					echo -e "		${RED}[-] Install of ${chaincode} Chaincode on peer${peer}.org${org}.${DOMAIN} failed!${NOCOLOR}"
					return 1
			fi
			echo -e "${GREEN}	[+] Install on peer${peer}.org${org}.${DOMAIN} ${NOCOLOR} finished \n"
		done
	done
	echo -e "${GREEN}[+] Installing finished ${NOCOLOR}"
  	changeOrg 0 1				# peer0.org1.domain
	peer lifecycle chaincode queryinstalled >&log.txt
	if [ $? -eq 1 ]; then
			echo -e "		${RED}[-] Query of Chaincode on peer0.org1.${DOMAIN} failed!${NOCOLOR}"
			return 1
	fi
	echo -e "${PURPLE}>>> Package Identifiers: ${NOCOLOR}"
	tmp=$(sed -n "/${chaincode}_1/{s/^Package ID: //; s/, Label:.*$//; p;}" log.txt)
	echo -e "${LIGHTBLUE}>>> [>] ${chaincode}: ${tmp}  ${NOCOLOR}"	# indirect, allows to treat CID as a var name
	return 0
}

approveCC(){
  chaincode=$1
	echo -e "${PURPLE}[*] Start approving... ${NOCOLOR}"
  CID=${chaincode}_ID
	for (( org = 1; org <= $NO_ORGANIZATIONS; org++ )); do
		changeOrg 0 $org
		peer lifecycle chaincode approveformyorg ${ORDERERS} --channelID ${CHANNEL_ID} --name $chaincode --version ${VERSION} --package-id $(sed -n "/${chaincode}_1/{s/^Package ID: //; s/, Label:.*$//; p;}" log.txt) --sequence ${VERSION} --waitForEvent
		if [ $? -eq 1 ]; then
				echo -e "		${RED}	[-] Org${org} did not approve ${chaincode} Chaincode! ${NOCOLOR}"
				return 1
		fi
	done
	echo -e "${GREEN}[+] Approving complete. ${NOCOLOR}"
	return 0
}

checkCommitReadiness(){
  chaincode=$1
	echo -e "${PURPLE}[*] Check for Commit Readiness ${NOCOLOR}"
	changeOrg 0 1			#peer0.org1
	peer lifecycle chaincode checkcommitreadiness --channelID ${CHANNEL_ID} --name ${chaincode} --version ${VERSION} --sequence ${VERSION} --output json
	if [ $? -eq 1 ]; then
			echo -e "		${RED}	[-] ${chaincode} not ready to be committed! ${NOCOLOR}"
			return 1
	fi
	echo -e "${GREEN}[+] Ready to Commit"
	return 0
}

commitCC(){
  chaincode=$1
	echo -e "${PURPLE}[*] Commit${NOCOLOR}"
	changeOrg 0 1 		# peer0.org1
	peer lifecycle chaincode commit ${ORDERERS} --channelID ${CHANNEL_ID} --name ${chaincode} $PEER_CON_PARAMS --version ${VERSION} --sequence ${VERSION}
	if [ $? -eq 1 ]; then
			echo -e "		${RED}	[-] ${chaincode} could not be committed! ${NOCOLOR}"
			return 1
	fi
	echo -e "${GREEN}[+] Commit complete! ${NOCOLOR}"
	echo -e "\n${LIGHTCYAN} =<=<=<=<=<=<=<=<=<=<=<=<= Chaincode on peer <=<=<=<=<=<=<=<=<=<=<=<=<=<=\n"
	peer lifecycle chaincode querycommitted --channelID ${CHANNEL_ID} --name ${chaincode}
	echo -e "\n${LIGHTCYAN} =<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<="
}
CC=$1
# Check if folder exists
echo -e "${LIGHTCYAN}[i] Installing ${CC}"
if [ ! -d "chaincodes/java/${CC}" ]; then
  echo -e "${RED}[-] Chaincode location invalid"
  exit 1
fi
# The Packing of the Chaincode
# After the Channel is setup, the Chaincode can be packaged. This involves a compilation step
# in conjunction with the new lifecycle package method.
packCC $CC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Install of the Chaincode
# After the Chaincode has been packaged, it can be installed onto each Client by Merlin.
# This is done with the new lifecycle install method
installCC $CC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Approval of the Chaincode
# Each organization need to approve the previously installed chaincode with its attributes!
# Merlin issues requests to each Organization
approveCC $CC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The Pre-Commit Step
# Merlin will check if each Organization is ready to commit the Chaincode onto the ledger
checkCommitReadiness $CC
if [ $? -eq 1 ]; then
		return 1
fi
sleep $SLEEPINTERVAL

# The final Commit
# The Chaincode gets committed onto the ledger! Now everything should be good to go.
commitCC $CC
if [ $? -eq 1 ]; then
		return 1
fi
