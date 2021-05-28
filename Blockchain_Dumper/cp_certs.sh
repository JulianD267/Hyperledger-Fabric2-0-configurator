#!/bin/bash
RES="src/main/resources/fabricConfig"
FABRIC_LOC=..
# CA
cp ${FABRIC_LOC}/crypto-config/peerOrganizations/org1.dredev.de/ca/ca.org1.dredev.de-cert.pem ${RES}

# Connection Profile
cp ${FABRIC_LOC}/connection_profile.yaml ${RES}