#!/bin/sh

docker pull juliandreyer/fabric-baseimage:2.1
docker pull juliandreyer/fabric-ca:2.1
docker pull juliandreyer/fabric-baseos:2.1
docker pull juliandreyer/fabric-couchdb:2.1
docker pull juliandreyer/fabric-ccenv:2.1
docker pull juliandreyer/fabric-orderer:2.1
docker pull juliandreyer/fabric-peer:2.1
docker pull juliandreyer/fabric-tools:2.1

# Tag them
docker tag juliandreyer/fabric-baseimage:2.1 hyperledger/fabric-baseimage:2.1
docker tag juliandreyer/fabric-ca:2.1 hyperledger/fabric-ca:2.1
docker tag juliandreyer/fabric-baseos:2.1 hyperledger/fabric-baseos:2.1
docker tag juliandreyer/fabric-couchdb:2.1 hyperledger/fabric-couchdb:2.1
docker tag juliandreyer/fabric-ccenv:2.1 hyperledger/fabric-ccenv:2.1
docker tag juliandreyer/fabric-orderer:2.1 hyperledger/fabric-orderer:2.1
docker tag juliandreyer/fabric-peer:2.1 hyperledger/fabric-peer:2.1
docker tag juliandreyer/fabric-tools:2.1 hyperledger/fabric-tools:2.1

# Show them
docker images
